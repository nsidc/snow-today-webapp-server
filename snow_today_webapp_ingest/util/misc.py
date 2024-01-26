from collections.abc import Callable
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def partition_dict_on_key(
    dct: dict[K, V],
    *,
    predicate: Callable,
) -> tuple[dict[K, V], dict[K, V]]:
    """Partition entries in `dct` into selected and deselected dicts based on key."""
    return (
        {key: val for key, val in dct.items() if predicate(key)},
        {key: val for key, val in dct.items() if not predicate(key)},
    )
