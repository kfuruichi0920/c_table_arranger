#!/usr/bin/env python3
"""Build script for creating Windows binary distribution."""

import subprocess
import sys
from pathlib import Path


def build_binary() -> None:
    """Build Windows binary using PyInstaller."""
    # Create build directory if it doesn't exist
    build_dir = Path("dist")
    build_dir.mkdir(exist_ok=True)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single file executable
        "--console",  # Console application
        "--name", "c-table-arranger",
        "--distpath", str(build_dir),
        "c_table_arranger/main.py"
    ]
    
    print("Building Windows binary...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("Build successful!")
        print(f"Binary created at: {build_dir / 'c-table-arranger.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_binary()