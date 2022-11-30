from pprint import pformat

from deepdiff import DeepDiff
from loguru import logger


# TODO: Better function name or generalize function more
def variable_index_diff_with_warning(var_a: dict, var_b: dict, /) -> dict:
    diff = DeepDiff(var_a, var_b)
    if diff != {}:
        logger.warning('Difference detected in `variables.json`:')
        logger.warning(pformat(diff))
        print(
            'WARNING: overwrite `variables.json`? Indentation will be borked by this'
            ' process. It may be simpler to apply this change manually.'
        )
        input('Enter to continue; CTRL+C to exit without overwriting.')

    return diff
