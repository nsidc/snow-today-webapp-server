from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from loguru import logger

from snow_today_webapp_ingest.constants.paths import (
    INCOMING_REGIONS_DIR,
    INCOMING_REGIONS_ROOT_JSON,
    INCOMING_TIF_DIR,
    OUTPUT_LEGENDS_SUBDIR,
    OUTPUT_REGIONS_COGS_SUBDIR,
    OUTPUT_REGIONS_SUBDIR,
    REPO_STATIC_COLORMAPS_INDEX_FP,
    REPO_STATIC_SCHEMAS_DIR,
    REPO_STATIC_VARIABLES_INDEX_FP,
)
from snow_today_webapp_ingest.ingest.cogs import ingest_cogs
from snow_today_webapp_ingest.ingest.legends import generate_legends
from snow_today_webapp_ingest.ingest.region_metadata import ingest_region_metadata
from snow_today_webapp_ingest.ingest.validate_and_copy_json import (
    validate_and_copy_json,
)


class IngestFunc(Protocol):
    def __call__(self, *, from_path: Path, to_path: Path, **kwargs: Any) -> None:
        ...


@dataclass
class IngestTask:
    # TODO: Keep track of all tasks created with an `instances` class variable? Then we
    # can save info about execution (e.g. time, errors messages, warnings, successes)
    # and generate a report? This feels like writing a task management tool...

    # Name of task. Displayed before it runs.
    name: str

    # Source to ingest from; if multiple, pass by name in a dict.
    from_path: Path | dict[str, Path]

    # Data will be ingested to a tempdir. Which subdir _within that tmpdir_ should this
    # task write to?
    to_relative_path: str

    # The function that is executed to ingest data.
    ingest_func: IngestFunc

    # Extra kwargs to the ingest func (TODO: Are creating partial functions a better
    # solution, less complex? :shrug:)
    ingest_kwargs: dict[str, Any] | None = None

    def run(
        self,
        *,
        ingest_tmpdir: Path,
    ) -> None:
        ingest_kwargs: dict = self.ingest_kwargs or {}

        logger.info(f"🏃🏃🏃 Executing task: {self.name} 🏃🏃🏃")
        self.ingest_func(
            from_path=self.from_path,
            to_path=ingest_tmpdir / self.to_relative_path,
            **ingest_kwargs,
        )
        logger.info(f"✅✅✅ Completed task: {self.name} ✅✅✅")


# TODO: _Snow Surface Properties_ ingest tasks, really. Still need to do SWE...
# NOTE: Tasks will run in the order they are specified in the dict.
ingest_tasks: dict[str, IngestTask] = {
    # We ingest some static data every day because we want the ingests to be idempotent.
    # The previous model wrote dynamic data next to static data in the final output
    # location, and didn't account for the possibility of static data getting
    # clobbered.
    "colormaps": IngestTask(
        name="Ingest static colormaps metadata JSON",
        from_path=REPO_STATIC_COLORMAPS_INDEX_FP,
        to_relative_path=REPO_STATIC_COLORMAPS_INDEX_FP.name,
        ingest_func=validate_and_copy_json,
        ingest_kwargs={
            "schema_path": REPO_STATIC_SCHEMAS_DIR / "colormapsIndex.json",
        },
    ),
    "variables": IngestTask(
        name="Ingest static variable metadata JSON",
        from_path=REPO_STATIC_VARIABLES_INDEX_FP,
        to_relative_path=REPO_STATIC_VARIABLES_INDEX_FP.name,
        # TODO: Filter to only the variables that we care about (based on
        #       what are shown in `regions/root.json`)
        ingest_func=validate_and_copy_json,
        ingest_kwargs={
            "schema_path": REPO_STATIC_SCHEMAS_DIR / "variablesIndex.json",
        },
    ),
    # TODO: Legends: Ingest dynamic legends and _copy_ static legends from this repo? Or
    #       generate the static legends at runtime and never store them? I feel the
    #       latter would provide more consistency in how the data is managed.
    #       Legends should be generated based on the variables.json and
    #       regions/root.json. e.g. legends/{region_id}_{variable_id}.svg (because snow
    #       cover days legends will be different based on region). OR legends can be
    #       generated in JS!!! That would be way simpler...
    "legends": IngestTask(
        name="Generate (static and dynamic) legends",
        from_path=INCOMING_REGIONS_ROOT_JSON,
        to_relative_path=OUTPUT_LEGENDS_SUBDIR,
        ingest_func=generate_legends,
    ),
    "region_metadata": IngestTask(
        name="Ingest daily region metadata JSON",
        from_path=INCOMING_REGIONS_DIR,
        to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ingest_func=ingest_region_metadata,
    ),
    # TODO: Should COGs be ingested based on the contents of regions/root.json, as
    # opposed to globbing for files?
    "region_cogs": IngestTask(
        name="Ingest daily Cloud-Optimized GeoTIFFs",
        from_path=INCOMING_TIF_DIR,
        to_relative_path=OUTPUT_REGIONS_COGS_SUBDIR,
        ingest_func=ingest_cogs,
    ),
    # TODO: Should shape data be ingested based on the contents of `regions/root.json`
    #       and `regions/[0-9]+.json`? E.g. look at those files, build up a plan, then
    #       ingest? Mark any extra shapes as warning, missing shapes as error.
    # TODO: Shape data
    # "region_shapes": IngestTask(
    #     name="Ingest region GeoJSON shapes",
    #     from_path=INCOMING_TIF_DIR,
    #     to_relative_path=OUTPUT_REGIONS_COGS_SUBDIR,
    #     ingest_func=ingest_shapes,
    # ),
    # TODO: Plot data
    # "region_plots": IngestTask(
    #     name="Ingest region plot JSON",
    #     from_path=...,
    #     to_relative_path=...,
    #     ingest_func=ingest_plot_json,
    # ),
}