import json

from loguru import logger

from snow_today_webapp_ingest.constants.paths import VARIABLES_INDEX_FP
from snow_today_webapp_ingest.util.legend import is_dynamic_legend, legend_from_variable


def static_legends_from_variables_index(variables_index: dict, /) -> None:
    """Create a legend for each entry in the `variables_index`, and update the index.

    Each variable in the index (except variables with dynamic colormaps) will be updated
    with `legend_path` key.

    Variables with dynamic colormaps will be recognized by presence of a _string_ value
    in `colormap_value_range` and skipped. Use the correct script to generate them.
    """
    for variable_id, variable_opts in variables_index.items():
        if variable_opts['type'] not in ['raster', 'point_swe']:
            continue

        # Skip dynamic legends:
        if is_dynamic_legend(variable_opts):
            continue

        rel_legend_path = legend_from_variable(variable_id, variable_opts)
        logger.info(f'Created static legend: {rel_legend_path}')


def make_static_legends() -> None:
    logger.info('Generating static legends...')
    with open(VARIABLES_INDEX_FP) as f:
        variables_index = json.loads(f.read())

    static_legends_from_variables_index(variables_index)
    logger.info('Done!')


if __name__ == '__main__':
    make_static_legends()
