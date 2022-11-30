import copy
import json

from constants.paths import VARIABLES_INDEX_FP
from loguru import logger
from util.diff import variable_index_diff_with_warning
from util.legend import is_dynamic_legend, legend_from_variable


def static_legends_from_variables_index(variables_index: dict, /) -> dict:
    """Create a legend for each entry in the `variables_index`, and update the index.

    Each variable in the index (except variables with dynamic colormaps) will be updated
    with `legend_path` key.

    Variables with dynamic colormaps will be recognized by presence of a _string_ value
    in `colormap_value_range` and skipped. Use the correct script to generate them.
    """
    updated_index = copy.deepcopy(variables_index)

    for variable_id, variable_opts in variables_index.items():
        if variable_opts['type'] != 'variable':
            continue

        # Skip dynamic legends:
        if is_dynamic_legend(variable_opts):
            continue

        rel_legend_path = legend_from_variable(variable_id, variable_opts)

        updated_index[variable_id]['legend_path'] = str(rel_legend_path)

    return updated_index


def make_static_legends() -> None:
    logger.info('Generating static legends...')
    with open(VARIABLES_INDEX_FP) as f:
        variables_index = json.loads(f.read())

    updated_index = static_legends_from_variables_index(variables_index)

    if variable_index_diff_with_warning(variables_index, updated_index) != {}:
        with open(VARIABLES_INDEX_FP, 'w') as f:
            json.dump(updated_index, f, indent=2)


if __name__ == '__main__':
    make_static_legends()
