from pprint import pprint

from deepdiff import DeepDiff


# TODO: Better function name or generalize function more
def variable_index_diff_with_warning(var_a: dict, var_b: dict, /) -> dict:
    diff = DeepDiff(var_a, var_b)
    if diff != {}:
        print('WARNING: Difference detected in `variables.json`:')
        pprint(diff)
        print()
        print(
            'WARNING: overwrite `variables.json`? Indentation will be borked by this'
            ' process. It may be simpler to apply this change manually.'
        )
        input('Enter to continue; CTRL+C to exit without overwriting.')

    return diff 
