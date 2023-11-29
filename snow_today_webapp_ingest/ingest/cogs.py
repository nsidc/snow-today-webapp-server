"""Convert non-CO GeoTIFFs to Cloud-Optimized GeoTIFFs."""
import subprocess
from pathlib import Path
from pprint import pformat

from loguru import logger


def make_cloud_optimized(
    *,
    input_tif_path: Path,
    output_tif_path: Path,
) -> Path:
    if output_tif_path.is_file():
        output_tif_path.unlink()
        logger.info(f'Removed {output_tif_path}')

    # TODO: -a_nodata 65535? Currently nodata value is not defined in metadata.
    subprocess.run(
        (
            f'gdal_translate "{input_tif_path}" "{output_tif_path}"'
            ' -of COG'
            ' -co "OVERVIEW_RESAMPLING=NEAREST"'
            ' -co "COMPRESS=LZW"'
        ),
        shell=True,
    )

    logger.info(f'Created COG {output_tif_path}')
    return output_tif_path


def ingest_cogs(
    *,
    from_path: Path,
    to_path: Path,
) -> None:
    input_tifs = list(from_path.glob('*.tif'))

    if len(input_tifs) == 0:
        msg = f'Aborting: no inputs found at: {from_path}'
        logger.warning(msg)
        raise RuntimeError(msg)

    input_tifs_pretty = pformat([str(p) for p in input_tifs])
    logger.info(f'Generating COGS from: {input_tifs_pretty}')

    to_path.mkdir(exist_ok=True, parents=True)
    for input_tif in input_tifs:
        logger.info(f'Cloud-optimizing input file {input_tif}...')
        make_cloud_optimized(
            input_tif_path=input_tif,
            output_tif_path=(to_path / input_tif.name),
        )


if __name__ == '__main__':
    ingest_cogs()
