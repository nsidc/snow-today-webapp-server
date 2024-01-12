"""Classes of data that this application deals with.

NOT to be confused with dataclasses (no underscore).

TODO: Better name! "Data types" isn't much better. "Data kinds"?
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal, ParamSpec, Protocol, TypeVar

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
from snow_today_webapp_ingest.ingest.cogs import ingest_cogs
from snow_today_webapp_ingest.ingest.copy_files import copy_files
from snow_today_webapp_ingest.ingest.legends import generate_legends
from snow_today_webapp_ingest.ingest.plot_json import ingest_plot_json
from snow_today_webapp_ingest.ingest.swe_json import ingest_swe_json
from snow_today_webapp_ingest.ingest.validate_and_copy_json import (
    validate_and_copy_json,
)
from snow_today_webapp_ingest.types_.base import BaseModel, RootModel
from snow_today_webapp_ingest.types_.colormaps import ColormapsIndex
from snow_today_webapp_ingest.types_.data_sources import DataSource
from snow_today_webapp_ingest.types_.plot import PlotPayload
from snow_today_webapp_ingest.types_.regions import (
    SubRegionCollectionsIndex,
    SubRegionsIndex,
    SuperRegionsIndex,
)
from snow_today_webapp_ingest.types_.subregion_hierarchy import (
    SubRegionsHierarchy,
)
from snow_today_webapp_ingest.types_.swe import SwePayload
from snow_today_webapp_ingest.types_.variables import VariablesIndex

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


# TODO: Keep track of all tasks created with an `instances` class variable? Then we
# can save info about execution (e.g. time, errors messages, warnings, successes)
# and generate a report? This feels like writing a task management tool...
@dataclass
class OutputDataClassIngestTask:
    """Information needed to ingest a class of data."""

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


@dataclass
class OutputDataClassValidationMetadata:
    """Information needed to validate a JSON output data file."""

    model: type[BaseModel] | type[RootModel]
    filename_pattern: re.Pattern


@dataclass
class OutputDataClassMetadata:
    description: str
    data_source: DataSource
    ingest_task: OutputDataClassIngestTask
    # TODO: Express this as a type so the type system can narrow on whether a class of
    #       data is validatable?
    validation_metadata: OutputDataClassValidationMetadata | None = None

    def ingest(
        self,
        *,
        ingest_tmpdir: Path,
    ) -> None:
        ingest_kwargs: dict = self.ingest_task.ingest_kwargs or {}

        logger.info(f"🏃🏃🏃 Executing task - {self.description} 🏃🏃🏃")
        self.ingest_func(
            from_path=self.ingest_task.from_path,
            to_path=ingest_tmpdir / self.ingest_task.to_relative_path,
            **ingest_kwargs,
        )
        # TODO: Validation of output using self.model? Pass self.model in to
        # self.ingest_func? Run self._validate() if validation_metadata present?
        logger.success(f"✅✅✅ Completed task - {self.description} ✅✅✅")


_ValidationMetadata = OutputDataClassValidationMetadata
_IngestTask = OutputDataClassIngestTask
OutputDataClassName = Literal[
    "colormapsIndex",
    "variablesIndex",
    "superRegionsIndex",
    "subRegionsIndex",
    "subRegionCollectionsIndex",
    "subRegionsHierarchy",
    "swePoints",
    "plots",
    "regionShapes",
    "cogs",
    "legends",
]
OUTPUT_DATA_CLASSES: Final[dict[OutputDataClassName, OutputDataClassMetadata]] = {
    # NOTE: We ingest some static data every day, like colormaps and variables, because
    # we want the ingests to be idempotent. The previous model wrote dynamic data next
    # to static data in the final output location, and didn't account for the
    # possibility of static data getting clobbered.
    "colormapsIndex": OutputDataClassMetadata(
        description="Ingest metadata: version-controlled colormaps JSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=validate_and_copy_json,
            from_path=REPO_STATIC_COLORMAPS_INDEX_FP,
            to_relative_path=REPO_STATIC_COLORMAPS_INDEX_FP.name,
        ),
        validation_metadata=_ValidationMetadata(
            model=ColormapsIndex,
            filename_pattern=re.compile(r'^colormaps.json$'),
        ),
    ),
    "variablesIndex": OutputDataClassMetadata(
        description="Ingest metadata: version-controlled variable JSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            # TODO: Filter to only the variables that we care about (based on what are
            #       shown in `regions/root.json`). This means passing in additional
            #       `from_path`s and using a more complex `ingest_func`.
            ingest_func=validate_and_copy_json,
            from_path=REPO_STATIC_VARIABLES_INDEX_FP,
            to_relative_path=REPO_STATIC_VARIABLES_INDEX_FP.name,
        ),
        validation_metadata=_ValidationMetadata(
            model=VariablesIndex,
            filename_pattern=re.compile(r'^variables.json$'),
        ),
    ),
    "superRegionsIndex": OutputDataClassMetadata(
        description="Ingest metadata: index of super-regions JSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            # TODO: ingest_func... paths wrong...
            ingest_func=...,
            from_path=INCOMING_REGIONS_DIR,
            to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ),
        validation_metadata=_ValidationMetadata(
            model=SuperRegionsIndex,
            filename_pattern=re.compile(fr'^{INCOMING_REGIONS_ROOT_JSON.name}$'),
        ),
    ),
    "subRegionsIndex": OutputDataClassMetadata(
        description="Ingest metadata: index of sub-regions within a super-region",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            # TODO: ingest_func... paths wrong...
            ingest_func=...,
            from_path=INCOMING_REGIONS_DIR,
            to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ),
        validation_metadata=_ValidationMetadata(
            model=SubRegionsIndex,
            filename_pattern=re.compile(r'^\d+.json$'),
        ),
    ),
    "subRegionCollectionsIndex": OutputDataClassMetadata(
        description="Ingest metadata: index of sub-region collections",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            # TODO: ingest_func... paths wrong...
            ingest_func=...,
            from_path=INCOMING_REGIONS_DIR,
            to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ),
        validation_metadata=_ValidationMetadata(
            model=SubRegionCollectionsIndex,
            filename_pattern=re.compile(r'^collections.json$'),
        ),
    ),
    "subRegionsHierarchy": OutputDataClassMetadata(
        description=(
            "Ingest metadata: hierarchical structure of sub-regions in a super-region"
        ),
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            # TODO: ingest_func... paths wrong...
            ingest_func=...,
            from_path=INCOMING_REGIONS_DIR,
            to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ),
        validation_metadata=_ValidationMetadata(
            model=SubRegionsHierarchy,
            filename_pattern=re.compile(r'^\d+_hierarchy.json$'),
        ),
    ),
    "swePointsJson": OutputDataClassMetadata(
        description="Ingest data: Snow Water Equivalent points JSON",
        data_source="snow-water-equivalent",
        ingest_task=_IngestTask(
            from_path=INCOMING_SWE_POINTS_DIR,
            to_relative_path=OUTPUT_POINTS_SUBDIR,
            ingest_func=ingest_swe_json,
        ),
        validation_metadata=_ValidationMetadata(
            model=SwePayload,
            filename_pattern=re.compile(r'^swe.json$'),
        ),
    ),
    # NOTE: Plot JSON files are not referenced anywhere, but they exist for each region
    #       (super- or sub-) and variable combination.
    # TODO: Update some metadata file so it references these files.
    "plotsJson": OutputDataClassMetadata(
        description="Ingest data: Plot JSON for each region/variable",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            from_path=INCOMING_PLOT_JSON_DIR,
            to_relative_path=OUTPUT_PLOTS_SUBDIR,
            ingest_func=ingest_plot_json,
        ),
        validation_metadata=_ValidationMetadata(
            model=PlotPayload,
            # WARNING: This pattern is pretty brittle; this could be anything related to
            # a region and variable, not necessarily a plot! See other TODOs about
            # replacing filename_pattern (e.g. cli.py)...
            filename_pattern=re.compile(r'^\d{5}_\d{2}.json$'),
        ),
    ),
    # TODO: Should shape data be ingested based on the contents of `regions/root.json`
    #       and `regions/[0-9]+.json`? E.g. look at those files, build up a plan, then
    #       ingest? Mark any extra shapes as warning, missing shapes as error.
    # TODO: Should shape data outputs be validated as GeoJSON?
    "regionShapes": OutputDataClassMetadata(
        description="Ingest data: Region shapes GeoJSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            from_path=INCOMING_SHAPES_DIR,
            to_relative_path=OUTPUT_REGIONS_SHAPES_SUBDIR,
            ingest_func=copy_files,
        ),
    ),
    # TODO: Should COGs be ingested based on the contents of regions/root.json, as
    #       opposed to globbing for files?
    "cogs": OutputDataClassMetadata(
        description=(
            "Ingest data: Cloud-Optimized GeoTIFFs for each super-region/variable"
        ),
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            from_path=INCOMING_TIF_DIR,
            to_relative_path=OUTPUT_REGIONS_COGS_SUBDIR,
            ingest_func=ingest_cogs,
        ),
    ),
    # TODO: Consider generating legends in JS. These are generated entirely based on
    #       data available to the webapp already.
    "legends": OutputDataClassMetadata(
        description=(
            "Ingest metadata: legends (static and dynamic) SVG for each"
            " super-region/variable"
        ),
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            from_path=INCOMING_REGIONS_ROOT_JSON,
            to_relative_path=OUTPUT_LEGENDS_SUBDIR,
            ingest_func=generate_legends,
        ),
    ),
}
VALIDATABLE_OUTPUT_DATA_CLASSES = {
    k: v for k, v in OUTPUT_DATA_CLASSES.items() if v.validation_metadata is not None
}
OUTPUT_DATA_CLASS_NAMES = list(OUTPUT_DATA_CLASSES.keys())
VALIDATABLE_OUTPUT_DATA_CLASS_NAMES = list(VALIDATABLE_OUTPUT_DATA_CLASSES)
