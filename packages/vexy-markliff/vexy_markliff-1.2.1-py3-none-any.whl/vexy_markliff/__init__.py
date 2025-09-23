"""Top-level package for vexy_markliff."""
# this_file: src/vexy_markliff/__init__.py

from vexy_markliff.__version__ import __version__
from vexy_markliff.vexy_markliff import Config, main, process_data

__all__ = [
    "Config",
    "__version__",
    "main",
    "process_data",
]
