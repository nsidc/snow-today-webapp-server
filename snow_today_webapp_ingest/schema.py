import json
from pathlib import Path

from IPython.display import Markdown, display
from jsonschema import ValidationError, validate
from loguru import logger

from snow_today_webapp_ingest.data_classes import (
    VALIDATABLE_OUTPUT_DATA_CLASSES,
    OutputDataClassName,
)


def display_jsonschema_markdown(data_class_name: OutputDataClassName) -> None:
    display(Markdown('```json\n' f"{get_jsonschema_str(data_class_name)}\n" '```'))


def get_jsonschema(data_class_name: OutputDataClassName) -> dict:
    data_class = VALIDATABLE_OUTPUT_DATA_CLASSES[data_class_name]

    if not data_class.validation_metadata:
        msg = f"Expected validation  metadata not found for {data_class_name=}"
        logger.error(msg)
        raise LookupError(msg)

    return data_class.validation_metadata.model.model_json_schema()


def get_jsonschema_str(data_class_name: OutputDataClassName) -> str:
    return json.dumps(
        get_jsonschema(data_class_name),
        indent=2,
    )


def schema_by_filename(filename: str) -> dict:
    for data_class_name, data_class in VALIDATABLE_OUTPUT_DATA_CLASSES.items():
        if not data_class.validation_metadata:
            continue
        if data_class.validation_metadata.filename_pattern.match(filename):
            logger.debug(f"Found matching schema: {data_class_name}")
            return data_class.validation_metadata.model.model_json_schema()

    msg = f"No schema matched the provided filename '{filename}'."
    logger.error(msg)
    raise LookupError(msg)


def validate_against_schema(file: Path) -> None:
    schema = schema_by_filename(file.name)
    file_json = json.loads(file.read_text())

    try:
        # TODO: Just load with Pydantic instead of validating with
        # jsonschema?
        validate(
            schema=schema,
            instance=file_json,
        )

    except ValidationError as e:
        logger.error(f"'{file.name}' failed validation ({e})")
        raise
