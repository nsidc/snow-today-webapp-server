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
