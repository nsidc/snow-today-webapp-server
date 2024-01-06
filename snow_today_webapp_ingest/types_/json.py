from typing import Generic, TypeVar

from pydantic import BaseModel

MetadataT = TypeVar("MetadataT")
DataT = TypeVar("DataT")


class JsonMetadataAndData(BaseModel, Generic[MetadataT, DataT]):
    metadata: MetadataT
    data: DataT
