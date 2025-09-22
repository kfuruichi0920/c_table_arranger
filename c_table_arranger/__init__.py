"""C Table Arranger - C language array data extractor and formatter."""

from importlib import metadata

DEFAULT_VERSION = "0.1.0"

try:
    __version__ = metadata.version("c-table-arranger")
except metadata.PackageNotFoundError:
    __version__ = DEFAULT_VERSION

__all__ = ["__version__"]
