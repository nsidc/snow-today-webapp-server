from typing import Generic, TypeVar

from snow_today_webapp_ingest.types_.base import BaseModel

MetadataT = TypeVar("MetadataT")
DataT = TypeVar("DataT")


class JsonMetadataAndData(BaseModel, Generic[MetadataT, DataT]):
    metadata: MetadataT
    data: DataT
