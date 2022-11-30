from pathlib import Path

from invoke import run

REPO_ROOT_DIR = Path(__file__).parent.parent
PACKAGE_DIR = REPO_ROOT_DIR / 'snow_today_webapp_ingest'


def print_and_run(cmd, **run_kwargs):
    print(cmd)
    kwargs = {
        'pty': True,
        **run_kwargs,
    }
    return run(cmd, **kwargs)
