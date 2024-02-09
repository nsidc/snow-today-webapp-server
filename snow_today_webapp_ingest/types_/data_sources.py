from typing import Literal

# TODO: Enum?
# See also: https://github.com/pallets/click/issues/605
# TODO: Think about the name of this type; are these really a "data source"?
#       snow-surface-properties includes data both from the supercomputer and from this
#       repo.
DataSource = Literal["snow-surface-properties", "snow-water-equivalent", "common"]
