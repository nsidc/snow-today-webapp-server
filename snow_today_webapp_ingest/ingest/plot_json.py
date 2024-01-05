"""Convert CSV plot files to JSON and write them to disk.

The output will be a JSON object with the CSV headers as keys. Values will be arrays
representing the column for each header.

NOTE: These outputs should not be committed!
"""
import json
from pathlib import Path
from pprint import pformat

from jsonschema import ValidationError, validate
from loguru import logger

from snow_today_webapp_ingest.constants.schemas import PLOT_DATA_SCHEMA_FP


def ingest_plot_json(
    from_path: Path,
    to_path: Path,
) -> None:
    input_files = list(from_path.glob('*.json'))

    if len(input_files) == 0:
        msg = f'Aborting: no inputs found at: {from_path}'
        logger.critical(msg)
        raise RuntimeError(msg)

    input_files_pretty = pformat([str(p) for p in input_files], indent=4)
    logger.info(f'Ingesting plot JSON from:\n{input_files_pretty}...')

    schema = json.loads(PLOT_DATA_SCHEMA_FP.read_text())

    for input_json_fp in input_files:
        input_json = json.loads(input_json_fp.read_text())

        # Validate
        # TODO: Validate filename meets expected pattern of
        # `{regionId}_{variableId}.json`
        try:
            validate(schema=schema, instance=input_json)
            logger.debug(f"'{input_json_fp.name}' validated!")
        except ValidationError as e:
            logger.error(f"'{input_json_fp.name}' failed validation ({e})")
            raise

        # Write JSON to destination
        output_fp = to_path / input_json_fp.name
        output_fp.parent.mkdir(parents=True, exist_ok=True)
        output_fp.write_text(json.dumps(input_json))
        logger.debug(f"Wrote to '{output_fp}'")

    logger.info(f'{len(input_files)} plot JSON files ingested to {to_path}')
