from typing import Literal

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

from constants.misc import CURRENT_DOWY
from constants.paths import REPO_LEGENDS_DIR, STORAGE_DYNAMIC_LEGENDS_DIR


ColormapExtendChoice = Literal['both', 'neither', 'min', 'max']

LEGEND_DIMENSIONS = (5, 0.5)
LEGEND_COLORBAR_BOTTOM = 0.5
LEGEND_FONT_SIZE = 8


def legend_from_variable(variable_id: str, variable: dict) -> str:
    """Write a legend based on `variable` and return its _relative_ path."""
    mpl.rcParams.update({
        'font.size': LEGEND_FONT_SIZE,
        # Make internal SVG unique IDs deterministic for better diffing:
        # https://matplotlib.org/stable/tutorials/introductory/customizing.html
        'svg.hashsalt': 'snow-today',
    })

    label = variable['label_map_legend']
    cmap_range = _colormap_range(variable)
    # matplotlib colormaps use float values ranging [0.0, 1.0], but our JSON data uses
    # 8-bit RGB values [0, 255]
    cmap_values = [
        tuple([v / 255.0 for v in rgb_color_8bit])
        for rgb_color_8bit in variable['colormap']
    ]

    fig, ax = plt.subplots(figsize=LEGEND_DIMENSIONS)
    fig.subplots_adjust(bottom=LEGEND_COLORBAR_BOTTOM)

    cmap = LinearSegmentedColormap.from_list('custom_colormap', cmap_values)
    norm = mpl.colors.Normalize(vmin=cmap_range[0], vmax=cmap_range[1])

    # NOTE: The top and bottom values may not always be displayed on the colorbar.
    # Should we address this?
    # https://stackoverflow.com/questions/54201881/add-top-and-bottom-value-label-to-color-bar
    fig.colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
        cax=ax,
        orientation='horizontal',
        label=label,
        extend=_extend(variable),
    )

    output_fn = f'{variable_id}.svg'
    is_dynamic = is_dynamic_legend(variable)
    if is_dynamic:
        STORAGE_DYNAMIC_LEGENDS_DIR.mkdir(exist_ok=True)
        output_dir = STORAGE_DYNAMIC_LEGENDS_DIR
    else:
        output_dir = REPO_LEGENDS_DIR

    output_path = output_dir / output_fn

    plt.savefig(
        output_path,

        # Reduce the whitespace on the edges:
        bbox_inches='tight',
        pad_inches=0.05,

        # Prevent SVG raster element (color gradient) from being misaligned from vector
        # elements:
        dpi=200,

        # Make the outputs more diffable:
        metadata={'Date': None},
    )
    if is_dynamic:
        return f'legends/dynamic/{output_fn}'
    else:
        return f'legends/{output_fn}'


def is_dynamic_legend(variable: dict) -> bool:
    if any(isinstance(v, str) for v in variable['colormap_value_range']):
        return True

    return False


def _eval_cmap_var(cmap_var: str | int) -> int:
    if isinstance(cmap_var, int):
        return cmap_var

    if cmap_var == '$DOWY':
        return CURRENT_DOWY
    else:
        raise RuntimeError(f'Unexpected colormap variable: {cmap_var}.')


def _colormap_range(variable: dict) -> tuple[int, int]:
    cmap_range_in = variable['colormap_value_range'].copy()

    cmap_range = (
        _eval_cmap_var(cmap_range_in[0]),
        _eval_cmap_var(cmap_range_in[1]),
    )
    return cmap_range


def _extend_str(left: bool, right: bool) -> ColormapExtendChoice:
    if left and right:
        return 'both'
    if left:
        return 'min'
    if right:
        return 'max'
    return 'neither'


def _extend(variable: dict) -> ColormapExtendChoice:
    if is_dynamic_legend(variable):
        return 'neither'

    cmap_range = _colormap_range(variable)
    data_range = variable['value_range'].copy()

    if cmap_range[0] == 1 and variable['transparent_zero']:
        cmap_range = (0, cmap_range[1])

    return _extend_str(
        left=data_range[0] < cmap_range[0],
        right=data_range[1] > cmap_range[1],
    )
