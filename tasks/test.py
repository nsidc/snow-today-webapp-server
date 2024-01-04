from invoke import task

from .util import REPO_ROOT_DIR, print_and_run


@task(aliases=('mypy',))
def typecheck(ctx):
    """Check for type correctness using mypy."""
    mypy_cfg_fp = REPO_ROOT_DIR / 'pyproject.toml'

    print_and_run(f'mypy --config-file={mypy_cfg_fp} .')
    print('🦆 Type checking passed.')


@task(default=True, pre=[typecheck])
def static(ctx):
    """Run all static analysis tasks."""
    print("🎉🎉🎉 All static analysis passed.")
