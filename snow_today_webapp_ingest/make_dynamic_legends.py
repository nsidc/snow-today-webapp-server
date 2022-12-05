import json

from loguru import logger

from snow_today_webapp_ingest.constants.paths import VARIABLES_INDEX_FP
from snow_today_webapp_ingest.util.legend import is_dynamic_legend, legend_from_variable


# TODO: DRY / share / note need to sync more code with static legends
# TODO: Type for variabes_index, options
def dynamic_legends_from_variables_index(variables_index: dict, /) -> None:
    """Create dynamic legend(s) from variables index and update index.

    Currently snow cover days has a dynamic legend based on current day-of-water-year.

    Legend is created in `legend_from_variable` function.
    """
    for variable_id, variable_opts in variables_index.items():
        if variable_opts['type'] != 'raster':
            continue

        # Skip static legends:
        if not is_dynamic_legend(variable_opts):
            continue

        rel_legend_path = legend_from_variable(variable_id, variable_opts)
        logger.info(f'Created dynamic legend: {rel_legend_path}')


def make_dynamic_legends():
    logger.info('Generating dynamic legend(s)...')
    with open(VARIABLES_INDEX_FP) as f:
        variables_index = json.loads(f.read())

    dynamic_legends_from_variables_index(variables_index)
    logger.info('Done!')


if __name__ == '__main__':
    make_dynamic_legends()
