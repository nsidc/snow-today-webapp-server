from typing import Annotated

from pydantic import StringConstraints

NumericIdentifier = Annotated[str, StringConstraints(pattern=r"^\d+$")]
