"""Main entry point for C Table Arranger."""

try:
    from .cli import main
except (ImportError, SystemError):
    # When the module is executed as a top-level script (e.g. after PyInstaller build)
    # the package context may be missing, so fall back to absolute import.
    from c_table_arranger.cli import main

if __name__ == '__main__':
    main()
