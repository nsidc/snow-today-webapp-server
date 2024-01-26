"""Classes of data that this application deals with.

NOT to be confused with dataclasses (no underscore). I'm sorry.

TODO: Better name! "Data types" isn't much better. "Data kinds"?
"""
import re
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Final, Literal, ParamSpec, Protocol, TypeVar

from loguru import logger

from snow_today_webapp_ingest.constants.paths import (
    INCOMING_PLOT_JSON_DIR,
    INCOMING_REGIONS_COLLECTIONS_JSON,
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
from snow_today_webapp_ingest.ingest.swe_json import ingest_swe_json
from snow_today_webapp_ingest.ingest.validate_and_copy_json import (
    validate_and_copy_json,
    validate_and_copy_json_matching_pattern,
)
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
from snow_today_webapp_ingest.types_.variables import VariablesIndex
from snow_today_webapp_ingest.util.misc import partition_dict_on_key

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

    # Data will be ingested to a tempdir. This attribute defines which subdir _within
    # that tmpdir_ this class of data will be written.
    to_relative_path: Path | str

    # The function that is executed to ingest data.
    ingest_func: IngestFunc


@dataclass
class OutputDataClass:
    """A class, or type, of output data.

    Often a single class of output data consists of a single file, but some classes
    consist of many files following a naming pattern.

    Most classes of data are received from an external source and copied in to place,
    but some are stored in the version control repository alongside this code, and some
    are generated or derived.

    Most classes of data can be validated, but that's not appropriate for all.
    """

    description: str
    data_source: DataSource
    ingest_task: OutputDataClassIngestTask

    def ingest(self, *, ingest_tmpdir: Path) -> None:
        """Run the ingest task associated with this data class.

        Expects to be passed a temporary directory in which to write outputs.
        """
        logger.info(f"🏃🏃🏃 Executing task - {self.description} 🏃🏃🏃")
        self.ingest_task.ingest_func(
            from_path=self.ingest_task.from_path,
            to_path=ingest_tmpdir / self.ingest_task.to_relative_path,
        )
        logger.success(f"✅✅✅ Completed task - {self.description} ✅✅✅")


_IngestTask = OutputDataClassIngestTask
OutputDataClassName = Literal[
    "colormapsIndex",
    "variablesIndex",
    "superRegionsIndex",
    "subRegionsIndex",
    "subRegionCollectionsIndex",
    "subRegionsHierarchy",
    "swePointsJson",
    "plotsJson",
    "regionShapes",
    "cogs",
    "legends",
]
OUTPUT_DATA_CLASSES: Final[dict[OutputDataClassName, OutputDataClass]] = {
    # NOTE: We ingest some static data every day, like colormaps and variables, because
    # we want the ingests to be idempotent. The previous model wrote dynamic data next
    # to static data in the final output location, and didn't account for the
    # possibility of static data getting clobbered.
    "colormapsIndex": OutputDataClass(
        description="Ingest metadata: version-controlled colormaps JSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=partial(
                validate_and_copy_json,
                model=ColormapsIndex,
            ),
            from_path=REPO_STATIC_COLORMAPS_INDEX_FP,
            to_relative_path=REPO_STATIC_COLORMAPS_INDEX_FP.name,
        ),
    ),
    "variablesIndex": OutputDataClass(
        description="Ingest metadata: version-controlled variable JSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            # TODO: Filter to only the variables that we care about (based on what are
            #       shown in `regions/root.json`). This means passing in additional
            #       `from_path`s and using a more complex `ingest_func`.
            ingest_func=partial(
                validate_and_copy_json,
                model=VariablesIndex,
            ),
            from_path=REPO_STATIC_VARIABLES_INDEX_FP,
            to_relative_path=REPO_STATIC_VARIABLES_INDEX_FP.name,
        ),
    ),
    "superRegionsIndex": OutputDataClass(
        description="Ingest metadata: index of super-regions JSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=partial(
                validate_and_copy_json,
                model=SuperRegionsIndex,
            ),
            from_path=INCOMING_REGIONS_ROOT_JSON,
            to_relative_path=OUTPUT_REGIONS_SUBDIR / INCOMING_REGIONS_ROOT_JSON.name,
        ),
    ),
    "subRegionsIndex": OutputDataClass(
        # TODO: Mention JSON format in description
        description="Ingest metadata: indexes of sub-regions within each super-region",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=partial(
                validate_and_copy_json_matching_pattern,
                model=SubRegionsIndex,
                pattern=re.compile(r'^\d+.json$'),
            ),
            from_path=INCOMING_REGIONS_DIR,
            to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ),
    ),
    "subRegionCollectionsIndex": OutputDataClass(
        # TODO: Mention JSON format in description
        description="Ingest metadata: index of sub-region collections",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=partial(
                validate_and_copy_json,
                model=SubRegionCollectionsIndex,
            ),
            from_path=INCOMING_REGIONS_COLLECTIONS_JSON,
            to_relative_path=(
                OUTPUT_REGIONS_SUBDIR / INCOMING_REGIONS_COLLECTIONS_JSON.name
            ),
        ),
    ),
    "subRegionsHierarchy": OutputDataClass(
        # TODO: Mention JSON format in description
        description=(
            "Ingest metadata: hierarchical structure of sub-regions in a super-region"
        ),
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=partial(
                validate_and_copy_json_matching_pattern,
                model=SubRegionsHierarchy,
                pattern=re.compile(r'^\d+_hierarchy.json$'),
            ),
            from_path=INCOMING_REGIONS_DIR,
            to_relative_path=OUTPUT_REGIONS_SUBDIR,
        ),
    ),
    "swePointsJson": OutputDataClass(
        description="Ingest data: Snow Water Equivalent points JSON",
        data_source="snow-water-equivalent",
        ingest_task=_IngestTask(
            ingest_func=ingest_swe_json,
            from_path=INCOMING_SWE_POINTS_DIR,
            to_relative_path=OUTPUT_POINTS_SUBDIR,
        ),
    ),
    # NOTE: Plot JSON files are not referenced anywhere, but they exist for each region
    #       (super- or sub-) and variable combination.
    # TODO: Update some metadata file so it references these files.
    "plotsJson": OutputDataClass(
        description="Ingest data: Plot JSON for each region/variable",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=partial(
                validate_and_copy_json_matching_pattern,
                model=PlotPayload,
                pattern=re.compile(r'\d+_\d{2}.json'),
            ),
            from_path=INCOMING_PLOT_JSON_DIR,
            to_relative_path=OUTPUT_PLOTS_SUBDIR,
        ),
    ),
    # TODO: Should shape data be ingested based on the contents of `regions/root.json`
    #       and `regions/[0-9]+.json`? E.g. look at those files, build up a plan, then
    #       ingest? Mark any extra shapes as warning, missing shapes as error.
    # TODO: Should shape data outputs be validated as GeoJSON?
    "regionShapes": OutputDataClass(
        description="Ingest data: Region shapes GeoJSON",
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=copy_files,
            from_path=INCOMING_SHAPES_DIR,
            to_relative_path=OUTPUT_REGIONS_SHAPES_SUBDIR,
        ),
    ),
    # TODO: Should COGs be ingested based on the contents of regions/root.json, as
    #       opposed to globbing for files?
    "cogs": OutputDataClass(
        description=(
            "Ingest data: Cloud-Optimized GeoTIFFs for each super-region/variable"
        ),
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=ingest_cogs,
            from_path=INCOMING_TIF_DIR,
            to_relative_path=OUTPUT_REGIONS_COGS_SUBDIR,
        ),
    ),
    # TODO: Consider generating legends in JS. These are generated entirely based on
    #       data available to the webapp already.
    "legends": OutputDataClass(
        description=(
            "Ingest metadata: legends (static and dynamic) SVG for each"
            " super-region/variable"
        ),
        data_source="snow-surface-properties",
        ingest_task=_IngestTask(
            ingest_func=generate_legends,
            from_path=INCOMING_REGIONS_ROOT_JSON,
            to_relative_path=OUTPUT_LEGENDS_SUBDIR,
        ),
    ),
}
SWE_OUTPUT_DATA_CLASSES, SSP_OUTPUT_DATA_CLASSES = partition_dict_on_key(
    OUTPUT_DATA_CLASSES,
    # TODO: Brittle. Add a boolean or enum field that defines the data class class?
    # Desperately need better terminology than "data class" because there are classes of
    # data classes, and that's way too confusing.
    predicate=lambda key: key.startswith("swe"),
)

OUTPUT_DATA_CLASS_NAMES, SWE_OUTPUT_DATA_CLASS_NAMES, SSP_OUTPUT_DATA_CLASS_NAMES = (
    list(dct.keys())
    for dct in (OUTPUT_DATA_CLASSES, SWE_OUTPUT_DATA_CLASSES, SSP_OUTPUT_DATA_CLASSES)
)
