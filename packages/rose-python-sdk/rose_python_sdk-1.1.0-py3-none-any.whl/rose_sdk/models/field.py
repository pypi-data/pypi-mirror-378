"""
Field models for the Rose Python SDK.
"""

from typing import Optional, List, Dict
from enum import Enum
from .base import BaseModel


class FieldType(str, Enum):
    """Field type enumeration."""

    INTEGER = "int"
    FLOAT = "float"
    STRING = "str"
    BOOLEAN = "bool"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    LIST = "list"
    MAP = "map"


class NumericProperties(BaseModel):
    """Properties for numeric fields."""

    minimum: Optional[float] = None
    maximum: Optional[float] = None
    value_in: Optional[List[float]] = None


class StringProperties(BaseModel):
    """Properties for string fields."""

    format: Optional[str] = None
    value_in: Optional[List[str]] = None


class ListProperties(BaseModel):
    """Properties for list fields."""

    children: "Field"
    unique: Optional[bool] = None


class MapProperties(BaseModel):
    """Properties for map fields."""

    fields: Dict[str, "Field"]


class Field(BaseModel):
    """Field definition model."""

    field_type: FieldType
    is_identifier: Optional[bool] = False
    is_required: Optional[bool] = False
    num_props: Optional[NumericProperties] = None
    str_props: Optional[StringProperties] = None
    list_props: Optional[ListProperties] = None
    map_props: Optional[MapProperties] = None


# Update forward references (Pydantic v2)
Field.model_rebuild()
ListProperties.model_rebuild()
MapProperties.model_rebuild()
