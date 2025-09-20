"""Local execution runners.

This module provides runners for executing tasks in local environments.
These runners can execute scripts, Python code, conda environments,
and other local execution contexts.
"""

import json
import logging
import os
import shlex
import subprocess
from tempfile import TemporaryDirectory, mkdtemp
from textwrap import dedent

from dml_util.core.utils import if_read_file, proc_exists, run_cli
from dml_util.lib.submit import launch_detached
from dml_util.runners.base import RunnerBase

logger = logging.getLogger(__name__)


class ScriptRunner(RunnerBase):
    """Runs a script locally."""

    @classmethod
    def funkify(cls, script, cmd=("python3",), suffix=".py"):
        return {"script": script, "cmd": list(cmd), "suffix": suffix}

    def submit(self):
        logger.debug("Submitting script to local runner")
        tmpd = mkdtemp(prefix="dml.")
        script_path = f"{tmpd}/script" + (self.input.kwargs["suffix"] or "")
        with open(script_path, "w") as f:
            f.write(self.input.kwargs["script"])
        with open(f"{tmpd}/input.dump", "w") as f:
            f.write(self.input.dump)
        env = {
            **self.config.to_envvars(),
            "DML_INPUT_LOC": f"{tmpd}/input.dump",
            "DML_OUTPUT_LOC": f"{tmpd}/output.dump",
            "DML_LOG_STDOUT": f"/run/{self.input.cache_key}/stdout",
            "DML_LOG_STDERR": f"/run/{self.input.cache_key}/stderr",
        }
        logger.debug(f"Environment for script: {json.dumps(env)}")
        proc_id = launch_detached([*self.input.kwargs["cmd"], script_path], env=env)
        return proc_id, tmpd

    def update(self, state):
        # TODO: update logging to include message
        # TODO: remove stderr printing unless debug or error
        pid = state.get("pid")
        if pid is None:
            pid, tmpd = self.submit()
            logger.info(f"Process {pid} started in {tmpd}")
            return {"pid": pid, "tmpd": tmpd}, f"{pid = } started", None
        tmpd = state["tmpd"]
        if proc_exists(pid):
            logger.debug(f"Process {pid} is still running")
            return state, f"{pid = } running", None
        logger.info(f"Process {pid} finished, checking output")
        dump = if_read_file(f"{tmpd}/output.dump")
        if dump:
            logger.debug(f"Process {pid} wrote output. Returning.")
            return None, f"{pid = } finished", dump
        logger.warning(f"Process {pid} did not write output, raising error")
        msg = f"[Script] {pid = } finished without writing output"
        raise RuntimeError(msg)

    def gc(self, state):
        logger.debug(f"Cleaning up state: {state}")
        if "pid" in state:
            logger.debug(f"Killing process {state['pid']}")
            run_cli(f"kill -9 {state['pid']} || echo", shell=True)
        if "tmpd" in state:
            logger.debug(f"Removing temporary directory {state['tmpd']}")
            command = "rm -r {} || echo".format(shlex.quote(state["tmpd"]))
            run_cli(command, shell=True)
        logger.debug("Calling super().gc()")
        super().gc(state)


class WrappedRunner(RunnerBase):
    """Runs a script that wraps another runner.

    Note: This runner does not keep state or handle job locks -- it's expecting the sub-runner to handle that.
    """

    @classmethod
    def funkify(cls, script, sub):
        kw = {"script": script, "sub": sub}
        return kw

    def run(self):
        """Overrides the RunnerBase.run method with a simple pass-through to the script."""
        sub_adapter, sub_uri, sub_kwargs = self.input.get_sub()
        with TemporaryDirectory() as tmpd:
            with open(f"{tmpd}/script", "w") as f:
                f.write(self.input.kwargs["script"])
            subprocess.run(["chmod", "+x", f"{tmpd}/script"], check=True)
            cmd = [f"{tmpd}/script", sub_adapter, sub_uri]
            env = os.environ.copy()
            env.update(self.config.to_envvars())
            result = subprocess.run(
                cmd,
                input=sub_kwargs,
                capture_output=True,
                check=False,
                text=True,
                env=env,
            )
        if result.returncode != 0:
            msg = "\n".join(
                [
                    f"Wrapped: {cmd}",
                    f"{result.returncode = }",
                    "",
                    "STDOUT:",
                    result.stdout,
                    "",
                    "=" * 10,
                    "STDERR:",
                    result.stderr,
                ]
            )
            raise RuntimeError(msg)
        return result.stdout, result.stderr


class HatchRunner(WrappedRunner):
    """Runs a script in a Hatch environment."""

    @classmethod
    def funkify(cls, name, sub, path=None):
        cd_str = "" if path is None else f"cd {shlex.quote(path)}"
        script = dedent(
            f"""
            #!/usr/bin/env bash
            set -euo pipefail

            which hatch >&2 || {{ echo "ERROR: hatch not found in PATH" >&2; exit 1; }}
            {cd_str}
            hatch env create {name} >&2 || echo "ERROR: hatch env create failed" >&2

            INPUT_DATA=$(cat)
            # if DML_DEBUG is set, print input data to stderr
            if [[ -n "${{DML_DEBUG:-}}" ]]; then
                echo "INPUT DATA:" >&2
                echo "$INPUT_DATA" >&2
                echo "DONE with input data" >&2
            fi
            echo "$INPUT_DATA" | hatch -e {name} run "$@"
            """
        ).strip()
        return WrappedRunner.funkify(script, sub)


class UvRunner(WrappedRunner):
    """Runs a script in a UV environment."""

    @classmethod
    def funkify(cls, sub, path=None):
        """
        Creates a script for running commands in a UV environment.

        This method is intended to be used in `dml_util.funkify`.

        Parameters
        ----------
        sub : str
            The sub data (adapter, uri, data) to be executed in the UV environment.
        path : str, optional
            The directory path to change into before executing the command.
            If None, no directory change is performed.

        Returns
        -------
        dict
            A dictionary that `dml_util.funkify` can use to create a dml executable Resource.
        """
        cd_str = "" if path is None else f"cd {shlex.quote(path)}"
        script = dedent(
            f"""
            #!/usr/bin/env bash
            set -euo pipefail

            {cd_str}
            uv run "$@"
            """
        ).strip()
        return WrappedRunner.funkify(script, sub)


class CondaRunner(WrappedRunner):
    """Runs a script in a Conda environment."""

    @classmethod
    def funkify(cls, name, sub, conda_loc=None):
        if conda_loc is None:
            conda_loc = str(run_cli(["conda", "info", "--base"]).strip())
            logger.info("Using conda from %r", conda_loc)
        script = dedent(
            f"""
            #!/usr/bin/env bash
            set -euo pipefail

            source {shlex.quote(conda_loc)}/etc/profile.d/conda.sh
            conda deactivate || echo 'no active conda environment to deactivate' >&2
            conda activate {name} >&2
            exec "$@"
            """
        ).strip()
        return WrappedRunner.funkify(script, sub)
