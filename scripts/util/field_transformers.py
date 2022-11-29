"""Field transformers alter the data in a field.

Currently for SWE JSON only.
"""
from typing import Any, Callable, TypeVar, overload

T = TypeVar('T')
V = TypeVar('V')
Transformer = Callable[[Any], Any]


@overload
def transform_value(*, value: V, transformer: None) -> V:
    ...


@overload
def transform_value(*, value: Any, transformer: Callable[[Any], T]) -> T:
    ...


def transform_value(*, value, transformer):
    if transformer is None:
        return value

    return transformer(value)


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
