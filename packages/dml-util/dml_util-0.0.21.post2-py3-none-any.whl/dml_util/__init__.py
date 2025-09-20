"""DaggerML utilities."""

# Try to import version first
try:
    from dml_util.__about__ import __version__, __version_tuple__
except ImportError:
    __version__ = "local"
    __version_tuple__ = ("local",)

# to register adapters, runners, and patches
import dml_util.adapters
import dml_util.runners

# Import core utilities that have no daggerml dependency
# Import adapters
from dml_util.aws import get_client
from dml_util.aws.s3 import S3Store
from dml_util.core.utils import dict_product, tree_map

try:
    import dml_util.wrapper  # to `new_dag` patch
    from dml_util import funk  # imported in advance for funkify
    from dml_util.funk import aws_fndag, dkr_build, funkify
except ImportError:
    pass
