from invoke import task

from .util import REPO_ROOT_DIR, print_and_run


@task(aliases=('jsonschema', 'validate'))
def validate_json(ctx):
    """Validate JSON against schemas.

    TODO: Add runtime validations that jsonschema can't do:
        * Only one variable is set `default: true`
        * Only one variable is set to `type: notprocessed`, and the rest
          `type: variable`
    """
    print_and_run(
        'jsonschema'
        f' -i {REPO_ROOT_DIR}/data/variables.json'
        f' {REPO_ROOT_DIR}/schema/variablesIndex.json'
    )
    print_and_run(
        'jsonschema'
        f' -i {REPO_ROOT_DIR}/data/regions.json'
        f' {REPO_ROOT_DIR}/schema/regionsIndex.json',
    )
    print("✔️ JSON validation passed.")


@task(aliases=('mypy',))
def typecheck(ctx):
    """Check for type correctness using mypy."""
    mypy_cfg_fp = REPO_ROOT_DIR / '.mypy.ini'

    print_and_run(f'mypy --config-file={mypy_cfg_fp} .')
    print('🦆 Type checking passed.')


@task(default=True, pre=[validate_json, typecheck])
def static(ctx):
    """Run all static analysis tasks."""
    print("🎉🎉🎉 All static analysis passed.")
