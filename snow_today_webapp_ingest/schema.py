import json
from pathlib import Path

from jsonschema import ValidationError, validate
from loguru import logger

from snow_today_webapp_ingest.types_.base import BaseModel, RootModel
from snow_today_webapp_ingest.types_.regions import SubRegionsIndex, SuperRegionsIndex
from snow_today_webapp_ingest.types_.swe import SwePayload

SCHEMA_PYDANTIC_MODELS: dict[str, type[BaseModel] | type[RootModel]] = {
    # "colormapsIndex": ...,
    # "variablesIndex": ...,
    "superRegionsIndex": SuperRegionsIndex,
    "subRegionsIndex": SubRegionsIndex,
    "swePayload": SwePayload,
}
SCHEMAS = list(SCHEMA_PYDANTIC_MODELS.keys())


def get_jsonschema(schema_name: str) -> dict:
    return SCHEMA_PYDANTIC_MODELS[schema_name].model_json_schema()


def validate_against_schema(file: Path, *, schema_name: str) -> None:
    if schema_name not in SCHEMAS:
        msg = f"{schema_name=} invalid. Must be one of: {SCHEMAS}"
        logger.error(msg)
        raise RuntimeError(msg)

    file_json = json.loads(file.read_text())

    try:
        validate(
            schema=get_jsonschema(schema_name),
            instance=file_json,
        )

    except ValidationError as e:
        logger.error(f"'{file.name}' failed validation ({e})")
        raise
