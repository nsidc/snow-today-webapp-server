import json
from pathlib import Path

from jsonschema import validate
from loguru import logger


def validate_and_copy_json(
    from_path: Path,
    to_path: Path,
    *,
    schema_path: Path,
) -> None:
    source_json = json.loads(from_path.read_text())
    schema_json = json.loads(schema_path.read_text())

    validate(schema=schema_json, instance=source_json)
    logger.info(f"{from_path.name} validated!")

    to_path.write_text(json.dumps(source_json))
