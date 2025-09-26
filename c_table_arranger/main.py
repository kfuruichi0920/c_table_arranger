"""Main entry point for C Table Arranger."""

try:
    from .cli import main
except (ImportError, SystemError):
    # PyInstaller などでスクリプトとして実行される場合、パッケージコンテキストが欠落することがあります。
    # PyInstaller などでバンドルした実行環境では相対インポートが失敗することがあるため、
    # その場合は絶対インポートに切り替えてエントリポイントを確保します。
    from c_table_arranger.cli import main

if __name__ == '__main__':
    main()
