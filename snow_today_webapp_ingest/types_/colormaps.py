from snow_today_webapp_ingest.types_.base import BaseModel, RootModel
from snow_today_webapp_ingest.types_.misc import NumericIdentifier

ColormapIdentifier = NumericIdentifier


class ColormapColors(RootModel):
    """A list of RGB (3-tuple) or RGBA (4-tuple) colors in this colormap."""

    # TODO: Represent as constraints instead of union?
    root: list[tuple[int, int, int] | tuple[int, int, int, int]]


class Colormap(BaseModel):
    """A colormap."""

    name: str
    colors: ColormapColors


class ColormapsIndex(RootModel):
    """An index of colormaps by numeric identifier."""

    root: dict[ColormapIdentifier, Colormap]
