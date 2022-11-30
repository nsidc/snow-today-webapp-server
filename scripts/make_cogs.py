"""Convert EPSG:4326 non-CO GeoTIFFs to Cloud-Optimized GeoTIFFs in Web Mercator."""
import subprocess
from pathlib import Path
from pprint import pformat

from constants.paths import INCOMING_TIF_DIR, STORAGE_COGS_DIR
from loguru import logger


def make_cloud_optimized(input_tif_path: Path) -> Path:
    output_tif_path = STORAGE_COGS_DIR / input_tif_path.name
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


def update_symlink(tif_path: Path) -> Path:
    """Create or update symbolic link pointing to `tif_path`.

    Get symbolic link filename by chopping varname and file extension off the end of
    `tif_path`.
    """
    symlink_fn = '_'.join(tif_path.name.split('_')[3:])
    symlink_path = STORAGE_COGS_DIR / symlink_fn
    symlink_target = tif_path.name

    if symlink_path.is_file():
        symlink_path.unlink()
    symlink_path.symlink_to(symlink_target)

    logger.debug(f'Created symlink {symlink_path} -> {symlink_target}')
    return symlink_path


def make_cogs() -> None:
    STORAGE_COGS_DIR.mkdir(exist_ok=True, parents=True)

    output_tifs: list[Path] = []
    symlinks: list[Path] = []

    input_tifs = list(INCOMING_TIF_DIR.glob('*.tif'))

    if len(input_tifs) == 0:
        msg = f'Aborting: no inputs found at: {INCOMING_TIF_DIR}'
        logger.warning(msg)
        raise RuntimeError(msg)

    input_tifs_pretty = pformat([str(p) for p in input_tifs])
    logger.info(f'Generating COGS from: {input_tifs_pretty}')
    for input_tif in input_tifs:
        print()
        print(f'Processing input file {input_tif}')
        output_tif = make_cloud_optimized(input_tif)
        symlink = update_symlink(output_tif)

        output_tifs.append(output_tif)
        symlinks.append(symlink)

    output_dir_contents = STORAGE_COGS_DIR.glob('*.tif')
    output_dir_contents_to_clean = (
        set(output_dir_contents) - set(output_tifs) - set(symlinks)
    )
    for f in output_dir_contents_to_clean:
        f.unlink()
        print(f'Removed {f}')


if __name__ == '__main__':
    make_cogs()
