from pathlib import Path
from typing import Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# TODO: Enum?
ColormapExtendChoice = Literal['both', 'neither', 'min', 'max']

LEGEND_DIMENSIONS = (5, 0.5)
LEGEND_COLORBAR_BOTTOM = 0.5
LEGEND_FONT_SIZE = 8


# TODO: Better types
def make_legend(
    *,
    colormap: list,
    colormap_value_range: tuple[int, int],
    data_value_range: tuple[int, int],
    label: str,
    transparent_zero: bool,
    output_fp: Path,
) -> None:
    """Write a legend based on `variable` and return its _relative_ path."""
    mpl.rcParams.update(
        {
            'font.size': LEGEND_FONT_SIZE,
            # Make internal SVG unique IDs deterministic for better diffing:
            # https://matplotlib.org/stable/tutorials/introductory/customizing.html
            'svg.hashsalt': 'snow-today',
        }
    )

    # matplotlib colormaps use float values ranging [0.0, 1.0], but our JSON data uses
    # 8-bit RGB values [0, 255]
    cmap_values = [
        tuple([v / 255.0 for v in rgb_color_8bit]) for rgb_color_8bit in colormap
    ]

    fig, ax = plt.subplots(figsize=LEGEND_DIMENSIONS)
    fig.subplots_adjust(bottom=LEGEND_COLORBAR_BOTTOM)

    cmap = LinearSegmentedColormap.from_list('custom_colormap', cmap_values)
    norm = mpl.colors.Normalize(
        vmin=colormap_value_range[0],
        vmax=colormap_value_range[1],
    )

    extend = _extend(
        colormap_value_range=colormap_value_range,
        data_value_range=data_value_range,
        transparent_zero=transparent_zero,
    )

    # NOTE: The top and bottom values may not always be displayed on the colorbar.
    # Should we address this?
    # https://stackoverflow.com/questions/54201881/add-top-and-bottom-value-label-to-color-bar
    fig.colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
        cax=ax,
        orientation='horizontal',
        label=label,
        extend=extend,
    )

    plt.savefig(
        output_fp,
        # Reduce the whitespace on the edges:
        bbox_inches='tight',
        pad_inches=0.05,
        # Prevent SVG raster element (color gradient) from being misaligned from vector
        # elements:
        dpi=200,
        # Make the outputs more diffable:
        metadata={'Date': None},
    )


def _extend_str(left: bool, right: bool) -> ColormapExtendChoice:
    """Figure out the correct string to give matplotlib for "extend" arrows."""
    if left and right:
        return 'both'
    if left:
        return 'min'
    if right:
        return 'max'
    return 'neither'


def _extend(
    *,
    colormap_value_range: tuple[int, int],
    data_value_range: tuple[int, int],
    transparent_zero: bool,
) -> ColormapExtendChoice:
    """Figure out whether, and which, "extend" arrows should go on the colormap."""
    # TODO: What is the reason for this special case?
    if colormap_value_range[0] == 1 and transparent_zero:
        colormap_value_range = (0, colormap_value_range[1])

    # Show "extend" arrows where the data range exceeds the colormap range.
    return _extend_str(
        left=data_value_range[0] < colormap_value_range[0],
        right=data_value_range[1] > colormap_value_range[1],
    )
