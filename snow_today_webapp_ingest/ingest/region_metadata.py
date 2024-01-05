import json
import re
from pathlib import Path
from re import Pattern
from typing import TypedDict

from jsonschema import ValidationError, validate
from loguru import logger

from snow_today_webapp_ingest.constants.paths import INCOMING_REGIONS_ROOT_JSON
from snow_today_webapp_ingest.constants.schemas import (
    REGIONS_INDEX_SCHEMA_FP,
    SUB_REGION_COLLECTIONS_INDEX_SCHEMA_FP,
    SUB_REGIONS_HIERARCHY_SCHEMA_FP,
    SUB_REGIONS_INDEX_SCHEMA_FP,
)


class SchemaMatcher(TypedDict):
    schema: dict
    matcher: Pattern


schemas_by_filename_regex: list[SchemaMatcher] = [
    {
        'schema': json.loads(REGIONS_INDEX_SCHEMA_FP.read_text()),
        'matcher': re.compile(fr'^{INCOMING_REGIONS_ROOT_JSON.name}$'),
    },
    {
        'schema': json.loads(SUB_REGION_COLLECTIONS_INDEX_SCHEMA_FP.read_text()),
        'matcher': re.compile(r'^collections.json$'),
    },
    {
        'schema': json.loads(SUB_REGIONS_INDEX_SCHEMA_FP.read_text()),
        'matcher': re.compile(r'^\d+.json$'),
    },
    {
        'schema': json.loads(SUB_REGIONS_HIERARCHY_SCHEMA_FP.read_text()),
        'matcher': re.compile(r'^\d+_hierarchy.json$'),
    },
]


def ingest_region_metadata(
    from_path: Path,
    to_path: Path,
) -> None:
    """Ingest region metadata (JSON)."""
    to_path.mkdir(parents=True, exist_ok=True)

    for file in from_path.glob("*"):
        # Validate the JSON with the appropriate schema
        try:
            for schema_matcher in schemas_by_filename_regex:
                if schema_matcher["matcher"].match(file.name):
                    logger.debug(f"Validating '{file.name}'...")
                    file_json = json.loads(file.read_text())
                    validate(
                        schema=schema_matcher["schema"],
                        instance=file_json,
                    )
                    logger.info(f"'{file.name}' validated!")
                    break
            else:
                logger.warning(
                    f"'{file.name}' is not a recognized filename pattern, and will be"
                    " ignored."
                )
                continue
        except ValidationError as e:
            logger.error(f"'{file.name}' failed validation ({e})")
            raise

        # Write JSON to destination
        output_fp = to_path / file.name
        output_fp.write_text(json.dumps(file_json))
        logger.info(f"Wrote to '{output_fp}'")
