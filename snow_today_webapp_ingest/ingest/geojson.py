import json
from pathlib import Path
from pprint import pformat

from loguru import logger


def fix_and_ingest_geojson(
    from_path: Path,  # A directory path; must exist.
    to_path: Path,  # A directory path; may or may not exist yet.
) -> None:
    """Read GeoJSON from `from_path`, fix, and write to `to_path`.

    This is a temporary hack to resolve problems with incoming GeoJSON files.
    """
    glob = "*.geojson"
    input_files = list(from_path.glob(glob))

    # TODO: A lot of this is lifted from validate_and_copy_json.py; if we need to keep
    #       this around, should DRY.
    if len(input_files) == 0:
        msg = f'Aborting: no files found at {from_path=} matching {glob=}'
        logger.critical(msg)
        raise RuntimeError(msg)

    input_files_pretty = pformat([str(p) for p in input_files], indent=4)
    logger.debug(f'Validating and copying:\n{input_files_pretty}...')

    to_path.mkdir(parents=True, exist_ok=True)
    for file in input_files:
        to_filepath = to_path / file.name
        fix_and_write_geojson_file(
            input_file=file,
            output_file=to_filepath,
        )


def fix_and_write_geojson_file(input_file: Path, output_file: Path) -> None:
    """Read GeoJSON from `input_file`, fix errors, validate, and write `output_file."""
    input_geojson = json.loads(input_file.read_text())

    if isinstance(input_geojson['features'], list):
        output_geojson = input_geojson
    else:
        logger.warning(
            f"Input GeoJSON {input_file} contains a 'features' element that is not"
            " a list. This matches a known pattern, attempting to fix..."
        )
        output_geojson = _fix(input_geojson)

    output_file.write_text(json.dumps(output_geojson))


def _fix(input_geojson: dict) -> dict:
    """Fix a geojson file.

    We look for two specific forms of error and assume the needed fixes:

    * "features" and "geometry" are singular:
        * Convert "features" to a 1-length list
    * "features" is singular but "geometry" is a list:
        * Generate the list of "features" from the "geometry" list.
        * Fix multipolygon coordinates to add one more layer of nesting
    """
    assert not isinstance(input_geojson['features'], list)
    if isinstance(input_geojson['features']['geometry'], dict):
        # Sometimes, geometry and features are _both_ singular, in which case we need to
        # wrap features in a list and continue. Seems like the coordinates are fine.
        return {
            **input_geojson,
            "features": [input_geojson['features']],
        }
    else:
        # Most of the time, geometry is a list, in which case we need to generate the
        # features list from the geometry list.
        output_features = [
            {
                "type": "Feature",
                "geometry": {**geom, "coordinates": [geom["coordinates"]]},
            }
            for geom in input_geojson['features']['geometry']
        ]
        return {
            **input_geojson,
            "features": output_features,
        }
