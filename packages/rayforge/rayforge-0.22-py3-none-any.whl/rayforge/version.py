import os
import subprocess
from typing import Optional

__dir__ = os.path.dirname(__file__)


def get_version_from_git() -> Optional[str]:
    try:
        output = subprocess.check_output(
            ["git", "describe"], stderr=subprocess.DEVNULL, cwd=__dir__
        )
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        NotADirectoryError,
    ):
        return None
    return output.decode("ascii").strip()


def get_version_from_pkg() -> Optional[str]:
    try:
        from importlib.metadata import version, PackageNotFoundError
    except ImportError:
        return None

    try:
        return version("rayforge")
    except PackageNotFoundError:
        return None


def get_version_from_file() -> Optional[str]:
    version_file = os.path.join(__dir__, "version.txt")
    try:
        with open(version_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
