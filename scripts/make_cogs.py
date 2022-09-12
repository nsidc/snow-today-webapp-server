"""Convert EPSG:4326 non-CO GeoTIFFs to Cloud-Optimized GeoTIFFs in Web Mercator."""
import subprocess
from pathlib import Path

from util.env import env_get

STORAGE_DIR = Path(env_get('STORAGE_DIR'))
OUTPUT_DIR = Path(env_get('SERVER_COGS_DIR'))

INPUT_VERSION = 'v004'
INPUT_ROOT_DIR = STORAGE_DIR / 'snow_today_2.0_testing' / f'{INPUT_VERSION}_westernUS'
INPUT_DIR = INPUT_ROOT_DIR / 'EPSG3857' / '2021' / 'LZW'


def make_cloud_optimized(input_tif_path: Path) -> Path:
    output_tif_path = OUTPUT_DIR / input_tif_path.name
    if output_tif_path.is_file():
        output_tif_path.unlink()
        print(f'Removed {output_tif_path}')

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

    print(f'Created COG {output_tif_path}')
    return output_tif_path


def update_symlink(tif_path: Path) -> Path:
    """Create or update symbolic link pointing to `tif_path`.

    Get symbolic link filename by chopping varname and file extension off the end of
    `tif_path`.
    """
    symlink_fn = '_'.join(tif_path.name.split('_')[3:])
    symlink_path = OUTPUT_DIR / symlink_fn
    symlink_target = tif_path.name

    if symlink_path.is_file():
        symlink_path.unlink()
    symlink_path.symlink_to(symlink_target)

    print(f'Created symlink {symlink_path} -> {symlink_target}')
    return symlink_path


if __name__ == '__main__':
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    output_tifs: list[Path] = []
    symlinks: list[Path] = []

    input_tifs = INPUT_DIR.glob('*.tif')
    for input_tif in input_tifs:
        print()
        print(f'Processing input file {input_tif}')
        output_tif = make_cloud_optimized(input_tif)
        symlink = update_symlink(output_tif)

        output_tifs.append(output_tif)
        symlinks.append(symlink)

    output_dir_contents = OUTPUT_DIR.glob('*.tif')
    output_dir_contents_to_clean = (
        set(output_dir_contents)
        - set(output_tifs)
        - set(symlinks)
    )
    for f in output_dir_contents_to_clean:
        f.unlink()
        print(f'Removed {f}')
