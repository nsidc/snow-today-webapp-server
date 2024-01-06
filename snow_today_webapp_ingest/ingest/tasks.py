from dataclasses import dataclass
from pathlib import Path
from typing import Any, ParamSpec, Protocol, TypeVar

from loguru import logger

from snow_today_webapp_ingest.constants.paths import (
    INCOMING_PLOT_JSON_DIR,
    INCOMING_REGIONS_DIR,
    INCOMING_REGIONS_ROOT_JSON,
    INCOMING_SHAPES_DIR,
    INCOMING_SWE_POINTS_DIR,
    INCOMING_TIF_DIR,
    OUTPUT_LEGENDS_SUBDIR,
    OUTPUT_PLOTS_SUBDIR,
    OUTPUT_POINTS_SUBDIR,
    OUTPUT_REGIONS_COGS_SUBDIR,
    OUTPUT_REGIONS_SHAPES_SUBDIR,
    OUTPUT_REGIONS_SUBDIR,
    REPO_STATIC_COLORMAPS_INDEX_FP,
    REPO_STATIC_VARIABLES_INDEX_FP,
)
from snow_today_webapp_ingest.constants.schemas import (
    COLORMAPS_INDEX_SCHEMA_FP,
    VARIABLES_INDEX_SCHEMA_FP,
)
from snow_today_webapp_ingest.ingest.cogs import ingest_cogs
from snow_today_webapp_ingest.ingest.copy_files import copy_files
from snow_today_webapp_ingest.ingest.legends import generate_legends
from snow_today_webapp_ingest.ingest.plot_json import ingest_plot_json
from snow_today_webapp_ingest.ingest.region_metadata import ingest_region_metadata
from snow_today_webapp_ingest.ingest.swe_json import ingest_swe_json
from snow_today_webapp_ingest.ingest.validate_and_copy_json import (
    validate_and_copy_json,
)

P = ParamSpec("P")
FromPath = TypeVar("FromPath", Path, dict[str, Path], contravariant=True)


class IngestFunc(Protocol[FromPath, P]):
    def __call__(
        self,
        # TODO: I would really love for these to be keyword-only arguments, but PEP612
        #       forbids that when using ParamSpec: https://peps.python.org/pep-0612/#id2
        from_path: FromPath,
        to_path: Path,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        pass


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
        logger.success(f"✅✅✅ Completed task: {self.name} ✅✅✅")


# TODO: _Snow Surface Properties_ ingest tasks, really. Still need to do SWE...
# NOTE: Tasks will run in the order they are specified in the dict.
ssp_ingest_tasks: dict[str, IngestTask] = {
    # We ingest some static data every day because we want the ingests to be idempotent.
    # The previous model wrote dynamic data next to static data in the final output
    # location, and didn't account for the possibility of static data getting
    # clobbered.
    "colormaps": IngestTask(
        name="Ingest metadata: version-controlled colormaps JSON",
        from_path=REPO_STATIC_COLORMAPS_INDEX_FP,
        to_relative_path=REPO_STATIC_COLORMAPS_INDEX_FP.name,
        ingest_func=validate_and_copy_json,
        ingest_kwargs={
            "schema_path": COLORMAPS_INDEX_SCHEMA_FP,
        },
    ),
    "variables": IngestTask(
        name="Ingest metadata: version-controlled variable JSON",
        from_path=REPO_STATIC_VARIABLES_INDEX_FP,
        to_relative_path=REPO_STATIC_VARIABLES_INDEX_FP.name,
        # TODO: Filter to only the variables that we care about (based on
        #       what are shown in `regions/root.json`)
        ingest_func=validate_and_copy_json,
        ingest_kwargs={"schema_path": VARIABLES_INDEX_SCHEMA_FP},
    ),
    # TODO: Consider generating legends in JS. These are generated entirely based on
    #       data available to the webapp already.
    "legends": IngestTask(
        name=(
            "Ingest metadata: legends (static and dynamic) SVG for each"
            "super-region/variable"
        ),
        from_path=INCOMING_REGIONS_ROOT_JSON,
        to_relative_path=OUTPUT_LEGENDS_SUBDIR,
        ingest_func=generate_legends,
    ),
    "region-metadata": IngestTask(
        name="Ingest metadata: region JSON",
        from_path=INCOMING_REGIONS_DIR,
        to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ingest_func=ingest_region_metadata,
    ),
    # TODO: Should shape data be ingested based on the contents of `regions/root.json`
    #       and `regions/[0-9]+.json`? E.g. look at those files, build up a plan, then
    #       ingest? Mark any extra shapes as warning, missing shapes as error.
    # TODO: Should shape data outputs be validated as GeoJSON?
    "region-shapes": IngestTask(
        name="Ingest metadata: region GeoJSON shapes",
        from_path=INCOMING_SHAPES_DIR,
        to_relative_path=OUTPUT_REGIONS_SHAPES_SUBDIR,
        ingest_func=copy_files,
    ),
    # TODO: Should COGs be ingested based on the contents of regions/root.json, as
    #       opposed to globbing for files?
    "cogs": IngestTask(
        name="Ingest data: Cloud-Optimized GeoTIFFs for each super-region/variable",
        from_path=INCOMING_TIF_DIR,
        to_relative_path=OUTPUT_REGIONS_COGS_SUBDIR,
        ingest_func=ingest_cogs,
    ),
    # NOTE: Plot JSON files are not referenced anywhere, but they exist for each region
    #       (super- or sub-) and variable combination.
    # TODO: Update some metadata file so it references these files.
    "plot-json": IngestTask(
        name="Ingest data: Plot JSON for each region/variable",
        from_path=INCOMING_PLOT_JSON_DIR,
        to_relative_path=OUTPUT_PLOTS_SUBDIR,
        ingest_func=ingest_plot_json,
    ),
}

swe_ingest_tasks = {
    "swe-point-json": IngestTask(
        name="Ingest data: Snow Water Equivalent Point JSON",
        from_path=INCOMING_SWE_POINTS_DIR,
        to_relative_path=OUTPUT_POINTS_SUBDIR,
        ingest_func=ingest_swe_json,
    ),
}
