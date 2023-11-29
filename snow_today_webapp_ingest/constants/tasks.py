from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from snow_today_webapp_ingest.constants.paths import (
    INCOMING_REGIONS_DIR,
    STORAGE_REGIONS_DIR,
)
from snow_today_webapp_ingest.ingest_region_metadata import ingest_region_metadata


class IngestFunc(Protocol):
    def __call__(self, *, from_path: Path, to_path: Path) -> None:
        ...


@dataclass
class IngestTask:
    name: str
    from_path: Path
    to_path: Path
    ingest_func: IngestFunc

    def run(self) -> None:
        self.ingest_func(
            from_path=self.from_path,
            to_path=self.to_path,
        )


ingest_tasks: list[IngestTask] = [
    # {
    #     "name": "Make daily Cloud-Optimized GeoTIFFs"
    #     "from": INCOMING_TIF_DIR,
    #     "to": STORAGE_COGS_DIR,
    #     "func": make_cogs,
    # },
    IngestTask(
        name="Ingest daily region metadata JSON",
        from_path=INCOMING_REGIONS_DIR,
        to_path=STORAGE_REGIONS_DIR,
        ingest_func=ingest_region_metadata,
    ),
]

# TODO: Move out of constants dir... make a tasks subpkg?
