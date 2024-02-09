import json
import re
from pathlib import Path
from pprint import pformat

from jsonschema import validate
from loguru import logger

from snow_today_webapp_ingest.types_.base import BaseModel, RootModel


def validate_and_copy_json(
    from_path: Path,  # A file path; exists.
    to_path: Path,  # A file path; doesn't exist yet.
    *,
    model: type[BaseModel] | type[RootModel],
) -> None:
    """Validate `from_path` file against `model`, then copy to `to_path`."""
    logger.debug(f"Copying {from_path} -> {to_path}...")

    source_json = json.loads(from_path.read_text())
    schema_json = model.model_json_schema()

    validate(schema=schema_json, instance=source_json)
    logger.info(f"Validated: {from_path.name}")

    to_path.parent.mkdir(parents=True, exist_ok=True)
    to_path.write_text(json.dumps(source_json))
    logger.debug(f"Created: {to_path}")


def validate_and_copy_json_matching_pattern(
    from_path: Path,  # A directory path; must exist.
    to_path: Path,  # A directory path; may or may not exist yet.
    *,
    model: type[BaseModel] | type[RootModel],
    pattern: re.Pattern,
) -> None:
    """Validate and copy files matching `pattern` from `from_path` to `to_path`."""
    all_files = from_path.glob("*")
    input_files = [f for f in all_files if pattern.match(f.name)]

    if len(input_files) == 0:
        msg = f'Aborting: no files found at {from_path=} matching {pattern=}'
        logger.critical(msg)
        raise RuntimeError(msg)

    input_files_pretty = pformat([str(p) for p in input_files], indent=4)
    logger.debug(f'Validating and copying:\n{input_files_pretty}...')

    to_path.mkdir(parents=True, exist_ok=True)
    for file in input_files:
        to_filepath = to_path / file.name
        validate_and_copy_json(file, to_filepath, model=model)

    logger.debug('Successfully validated and copied {len(input_files)} files')
