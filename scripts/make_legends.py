import copy
import json
from pathlib import Path
from pprint import pprint
from typing import Literal

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from deepdiff import DeepDiff

from constants.paths import VARIABLES_INDEX_FP, REPO_DATA_DIR, REPO_LEGENDS_DIR

LEGEND_DIMENSIONS = (5, 0.5)
LEGEND_COLORBAR_BOTTOM = 0.5
LEGEND_FONT_SIZE = 8

ColormapExtendChoice = Literal['both', 'neither', 'min', 'max']


def _extend_str(left: bool, right: bool) -> ColormapExtendChoice:
    if left and right:
        return 'both'
    if left:
        return 'min'
    if right:
        return 'max'
    return 'neither'


def _extend(variable: dict) -> ColormapExtendChoice:
    cmap_range = variable['colormap_value_range'].copy()
    data_range = variable['value_range'].copy()

    if cmap_range[0] == 1 and variable['transparent_zero']:
        cmap_range[0] = 0

    return _extend_str(
        left=data_range[0] < cmap_range[0],
        right=data_range[1] > cmap_range[1],
    )


def legend_from_variable(variable_id: str, variable: dict) -> Path:
    """Write a legend based on `variable` and return its path."""
    mpl.rcParams.update({
        'font.size': LEGEND_FONT_SIZE,
        # Make internal SVG unique IDs deterministic for better diffing:
        # https://matplotlib.org/stable/tutorials/introductory/customizing.html
        'svg.hashsalt': 'snow-today',
    })

    label = variable['label_map_legend']
    cmap_range = variable['colormap_value_range']
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
    output_path = REPO_LEGENDS_DIR / output_fn

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
    return output_path


def legends_from_variables_index(variables_index: dict) -> dict:
    """Create a legend for each entry in the `variables_index`, and update the index.

    Each variable in the index will be updated with `legend_path` key.
    """
    updated_index = copy.deepcopy(variables_index)

    for variable_id, variable_opts in variables_index.items():
        if variable_opts['type'] != 'variable':
            continue

        legend_path = legend_from_variable(variable_id, variable_opts)
        rel_legend_path = legend_path.relative_to(REPO_DATA_DIR)

        updated_index[variable_id]['legend_path'] = str(rel_legend_path)

    return updated_index


if __name__ == '__main__':
    with open(VARIABLES_INDEX_FP) as f:
        variables_index = json.loads(f.read())

    updated_index = legends_from_variables_index(variables_index)

    diff = DeepDiff(variables_index, updated_index)
    if diff != {}:
        print('WARNING: Difference detected in `variables.json`:')
        pprint(diff)
        print()
        input(
            'Press Enter to overwrite `variables.json`. NOTE: indentation will be'
            ' borked by this process. CTRL+C to exit without overwriting.'
        )
        with open(VARIABLES_INDEX_FP, 'w') as f:
            json.dump(updated_index, f, indent=2)
