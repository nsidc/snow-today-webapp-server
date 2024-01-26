from functools import partial
from typing import Annotated

from pydantic import Field, StringConstraints

StringIdentifier = Annotated[str, StringConstraints(pattern=r"^.+$")]
NumericIdentifier = Annotated[str, StringConstraints(pattern=r"^[0-9]+$")]

# TODO: Use this?
YearField = partial(Field, int, gt=1900, le=3000)
# Year = Annotated[int, Gt(1900), Lt(3000)]
