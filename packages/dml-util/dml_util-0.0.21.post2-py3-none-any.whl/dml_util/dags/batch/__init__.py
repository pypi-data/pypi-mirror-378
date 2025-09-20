#!/usr/bin/env python3
import json
import os
import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from dml_util import __version__
from dml_util.aws.s3 import S3Store

_here_ = Path(__file__).parent
LOCAL_TEST = os.getenv("DML_TESTING")


def zipit(directory_path, output_zip):
    # FIXME: Use reproducible zip
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname)


def zip_up(s3, filepath):
    with TemporaryDirectory() as tmpd:
        os.system(f"cp {filepath} {tmpd}/index.py")
        if LOCAL_TEST:
            root = _here_.parent.parent.parent.parent
            os.system(f"pip install {root} -t {tmpd}")
        else:
            os.system(f"pip install 'dml-util=={__version__}' -t {tmpd}")
        with NamedTemporaryFile(suffix=".zip") as tmpf:
            zipit(tmpd, tmpf.name)
            tmpf.flush()
            obj = s3.put(filepath=tmpf.name, suffix=".zip")
    print(f"Uploaded zip to {obj.uri}")
    return dict(zip(["S3Bucket", "S3Key"], s3.parse_uri(obj.uri)))


def load():
    s3 = S3Store()
    with open(_here_ / "cf.json") as f:
        js = json.load(f)
    js["Resources"]["Fn"]["Properties"]["Code"] = zip_up(s3, _here_ / "impl.py")  # code_data
    params = {"Bucket": s3.bucket, "Prefix": "opt/dml/exec/batch"}
    return js, params, "LambdaFunctionArn", "dml-util-lambda-adapter"
