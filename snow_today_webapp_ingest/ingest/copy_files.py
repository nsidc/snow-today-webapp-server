import shutil
from pathlib import Path


def copy_files(
    from_path: Path,
    to_path: Path,
) -> None:
    """Copy all files in `from_path` to `to_path`.

    Supports nested directories.
    """
    shutil.copytree(from_path, to_path, dirs_exist_ok=True)
