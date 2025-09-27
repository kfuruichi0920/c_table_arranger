"""C Table Arranger - C language array data extractor and formatter."""

from importlib import metadata

# ランタイム時にパッケージメタデータを参照してバージョン番号を取得します。
DEFAULT_VERSION = "0.2.0"

try:
    # パッケージがインストールされていれば正式なバージョンを使用します。
    __version__ = metadata.version("c-table-arranger")
except metadata.PackageNotFoundError:
    # メタデータが見つからない場合は開発時の既定値を返します。
    __version__ = DEFAULT_VERSION

__all__ = ["__version__"]
