# TODO: Move out of constants dir... make a tasks subpkg?
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from loguru import logger

from snow_today_webapp_ingest.constants.paths import (
    INCOMING_REGIONS_DIR,
    INCOMING_TIF_DIR,
    OUTPUT_COGS_SUBDIR,
    OUTPUT_REGIONS_SUBDIR,
)
from snow_today_webapp_ingest.ingest.cogs import ingest_cogs
from snow_today_webapp_ingest.ingest.region_metadata import ingest_region_metadata


class IngestFunc(Protocol):
    def __call__(self, *, from_path: Path, to_path: Path, **kwargs: Any) -> None:
        ...


@dataclass
class IngestTask:
    # Name of task. Displayed before it runs.
    name: str

    # Source to ingest from
    from_path: Path

    # Data will be ingested to a tempdir. Which subdir _within that tmpdir_ should this
    # task write to?
    to_relative_path: str

    # The function that is executed to ingest data.
    ingest_func: IngestFunc

    def run(
        self,
        *,
        ingest_tmpdir: Path,
        ingest_kwargs: dict | None = None,
    ) -> None:
        if ingest_kwargs is None:
            ingest_kwargs = {}

        logger.info(f"🏃🏃🏃 Executing task: {self.name} 🏃🏃🏃")
        self.ingest_func(
            from_path=self.from_path,
            to_path=ingest_tmpdir / self.to_relative_path,
            **ingest_kwargs,
        )


ingest_tasks: list[IngestTask] = [
    IngestTask(
        name="Ingest daily region metadata JSON",
        from_path=INCOMING_REGIONS_DIR,
        to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ingest_func=ingest_region_metadata,
    ),
    # TODO: Should COGs be ingested based on the contents of regions/root.json, as
    # opposed to globbing for files? Do I need to add a parameter like "extra_kwargs" to
    # pass in the file path? Feels like I'm writing a task management tool at this
    # point...
    IngestTask(
        name="Ingest daily Cloud-Optimized GeoTIFFs",
        from_path=INCOMING_TIF_DIR,
        to_relative_path=OUTPUT_COGS_SUBDIR,
        ingest_func=ingest_cogs,
    ),
]
