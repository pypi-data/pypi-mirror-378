import json
import os
import subprocess
import sys
from argparse import ArgumentParser
from importlib import import_module
from time import time

from daggerml import Dml, Executable

from dml_util import __version_tuple__


def imp(name):
    return import_module(f"dml_util.dags.{name}")


def main():
    parser = ArgumentParser(description="Spin up a known cfn stack (in a dag).")
    parser.add_argument("name", nargs="?")
    parser.add_argument("-f", "--filepath")
    parser.add_argument("-i", "--add-version-info", action="store_true")
    parser.add_argument("-l", "--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        here = os.path.dirname(__file__)
        for x in os.listdir(here):
            if os.path.isdir(f"{here}/{x}") and x != "__pycache__":
                print(x)
        sys.exit(0)
    version = "-".join(map(str, __version_tuple__[:3]))  # drop .dev0 and .post0, etc.
    assert args.name is not None, "name is required unless --list is set"
    with Dml().new(args.name, f"creating {args.name} cfn stack") as dag:
        if args.filepath is None:
            mod = imp(args.name)
            tpl, params, output_name, adapter = mod.load()
        else:
            resp = subprocess.run([args.filepath], check=True, capture_output=True, text=True)
            tpl, params, output_name, adapter = json.loads(resp.stdout)
        dag.tpl = tpl
        dag.params = params
        dag.adapter = adapter
        dag.output_name = output_name
        dag.cfn_fn = Executable("cfn", adapter="dml-util-local-adapter")
        dag.stack = dag.cfn_fn(
            (f"dml-v{version}-{args.name}" if args.add_version_info else args.name),
            dag.tpl,
            params,
            time(),
            sleep=lambda: 5_000,
        )
        dag.commit(Executable(dag.stack[output_name].value(), adapter=adapter))
