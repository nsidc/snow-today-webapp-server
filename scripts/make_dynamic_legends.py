import copy
import json

from constants.paths import VARIABLES_INDEX_FP, REPO_DATA_DIR
from util.diff import variable_index_diff_with_warning
from util.legend import (
    is_dynamic_legend,
    legend_from_variable,
)


# TODO: DRY / share / note need to sync more code with static legends
# TODO: Type for variabes_index, options
def dynamic_legends_from_variables_index(variables_index: dict, /) -> dict:
    updated_index = copy.deepcopy(variables_index)

    for variable_id, variable_opts in variables_index.items():
        if variable_opts['type'] != 'variable':
            continue

        # Skip static legends:
        if not is_dynamic_legend(variable_opts):
            continue

        rel_legend_path = legend_from_variable(variable_id, variable_opts)
        updated_index[variable_id]['legend_path'] = str(rel_legend_path)

    return updated_index


def make_dynamic_legends():
    with open(VARIABLES_INDEX_FP) as f:
        variables_index = json.loads(f.read())

    updated_index = dynamic_legends_from_variables_index(variables_index)

    if variable_index_diff_with_warning(variables_index, updated_index) != {}:
        with open(VARIABLES_INDEX_FP, 'w') as f:
            json.dump(updated_index, f, indent=2)


if __name__ == '__main__':
    make_dynamic_legends()
