from typing import Annotated

from annotated_types import Gt, Lt
from pydantic import StringConstraints

StringIdentifier = Annotated[str, StringConstraints(pattern=r"^.+$")]
NumericIdentifier = Annotated[str, StringConstraints(pattern=r"^[0-9]+$")]

Year = Annotated[int, Gt(1900), Lt(3000)]
