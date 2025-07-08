#!/usr/bin/env python3
"""
Dokku API CLI - Simple wrapper for Makefile commands

This module provides a command-line interface that wraps the Makefile commands,
allowing users to manage Dokku API after installing from PyPI.

Usage:
    dokku-api <command>     # Run any Makefile command
    dokku-api help          # Show all available commands from Makefile
"""
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import dokku_api
except ImportError:
    print("Install the dokku-api package first using 'pip install dokku-api'")
    sys.exit(1)


def get_package_dir():
    """
    Get the directory where the package is installed.
    """
    return Path(dokku_api.__file__).parent


def run_make_command(command, args=None):
    """
    Run a Makefile command using the config directory's Makefile.
    """
    if not shutil.which("make"):
        print("Error: 'make' not found. Install GNU Make first.")
        return 1

    try:
        package_dir = get_package_dir()
        makefile_path = package_dir / "Makefile"

        # Ensure Makefile exists in directory
        if not makefile_path.exists():
            print("Error: Could not find Makefile at the Dokku API package")
            return 1

        # Ensure .env exists in directory
        source = package_dir / ".env.sample"
        destination = package_dir / ".env"

        if not destination.exists():
            shutil.copy(source, destination)

        # Run make from the config directory where .env is located
        cmd = ["make", "-f", str(makefile_path), command] + (args or [])

        # Set working directory to config directory for make execution
        return subprocess.run(cmd, cwd=package_dir).returncode

    except Exception as e:
        print(f"Error running make command: {e}")
        return 1


def main():
    """
    Main CLI entry point.
    """
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    if command in ["help", "--help", "-h"]:
        return run_make_command("help")

    return run_make_command(command, args)


if __name__ == "__main__":
    sys.exit(main())
