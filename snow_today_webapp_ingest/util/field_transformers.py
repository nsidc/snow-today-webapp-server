"""Field transformers alter the data in a field.

Currently for SWE JSON only.
"""

import math


def float_nan_normalized(inp: str) -> float | None:
    """Use None instead of NaN in floats.

    This enables standards-compliant JSON output.
    """
    flt = float(inp)
    if math.isnan(flt):
        return None
    return flt


def state_normalized(state: str) -> str:
    norm = state.removeprefix('US')
    return norm


def huc2_normalized(huc2: str) -> int | None:
    """Strip HUC prefix from each value and return integer remainder.

    Return None if value is "N/A"
    """
    if huc2 == 'N/A':
        return None

    norm = huc2.removeprefix('HUC')
    return int(norm)


def huc4_normalized(huc4: str) -> int | None:
    """Integerize value.

    Unlike HUC2 values, no prefix is attached.

    Return None if value is "N/A".
    """
    if huc4 == 'N/A':
        return None

    return int(huc4)
