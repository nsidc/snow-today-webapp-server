import inspect
import os
from pathlib import Path

from invoke import run

REPO_ROOT_DIR = Path(__file__).parent.parent


def print_and_run(cmd, **run_kwargs):
    print(cmd)
    kwargs = {
        'pty': True,
        **run_kwargs,
    }
    return run(cmd, **kwargs)
