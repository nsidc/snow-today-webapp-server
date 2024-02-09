import shutil
from pathlib import Path

from loguru import logger


def _copytree_log(path, names):
    """Log copytree progress.

    Based on example:

    https://docs.python.org/3/library/shutil.html#copytree-example
    """
    logger.debug(f"Copying {len(names)} files from {path}...")
    return []


def copy_files(
    from_path: Path,
    to_path: Path,
) -> None:
    """Copy all files in `from_path` to `to_path`.

    Supports nested directories.
    """
    shutil.copytree(
        from_path,
        to_path,
        dirs_exist_ok=True,
        ignore=_copytree_log,
    )
