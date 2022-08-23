from pathlib import Path

from invoke import task

from .util import REPO_ROOT_DIR, print_and_run


@task(aliases=('flake8',))
def lint(ctx):
    """Run static analysis with flake8."""
    flake8_cfg_fp = REPO_ROOT_DIR / '.flake8'

    print_and_run(
        f'cd {REPO_ROOT_DIR}'
        f' && flake8 --config {flake8_cfg_fp} .'
    )
    print("🎉👕 Linting passed.")


@task(aliases=('mypy',))
def typecheck(ctx):
    """Check for type correctness using mypy."""
    mypy_cfg_fp = REPO_ROOT_DIR / '.mypy.ini'

    print_and_run(f'mypy --config-file=-{mypy_cfg_fp} .')
    print('🎉🦆 Type checking passed.')


@task(default=True, pre=[lint, typecheck])
def static(ctx):
    """Run all static analysis tasks."""
    pass
