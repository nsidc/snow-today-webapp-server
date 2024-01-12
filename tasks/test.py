import itertools
import logging
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


@task(aliases=('validate',))
def validate_json(ctx):
    from snow_today_webapp_ingest.logging_ import setup_logger
    from snow_today_webapp_ingest.schema import validate_against_schema

    setup_logger(logger, log_level=logging.DEBUG)

    doc_dir = REPO_ROOT_DIR / 'doc' / 'interfaces'
    static_dir = REPO_ROOT_DIR / 'static'
    files = itertools.chain(
        doc_dir.glob('*/example_data/**/*.json'),
        static_dir.glob('*.json'),
    )
    for file in files:
        logger.info(f"Validating {file}...")
        validate_against_schema(file)
        logger.success("Valid!")

    logger.success('📋 JSON validation passed.')


@task(default=True, pre=[validate_json, typecheck])
def static(ctx):
    """Run all static analysis tasks."""
    logger.success("🎉🎉🎉 All static analysis passed! 🎉🎉🎉")
