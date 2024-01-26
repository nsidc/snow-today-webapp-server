import sys

from invoke import task
from loguru import logger

from .util import REPO_ROOT_DIR, print_and_run

sys.path.append(str(REPO_ROOT_DIR))


@task(aliases=('mypy',))
def typecheck(ctx):
    """Check for type correctness using mypy."""
    mypy_cfg_fp = REPO_ROOT_DIR / 'pyproject.toml'

    print_and_run(f'mypy --config-file={mypy_cfg_fp} .')
    logger.success('🦆 Type checking passed.')


@task(default=True, pre=[typecheck])
def static(ctx):
    """Run all static analysis tasks."""
    logger.success("🎉🎉🎉 All static analysis passed! 🎉🎉🎉")
