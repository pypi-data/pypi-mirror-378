"""
Batch models for the Rose Python SDK.
"""

from typing import Dict
from .base import BaseModel
from pydantic import Field


class BatchIDInfo(BaseModel):
    """Batch ID info model."""

    updated_at: int
    index: str


class BatchRecordsImportInfo(BaseModel):
    """Batch records import info model."""

    import_: Dict[str, Dict[str, str]] = Field(alias="import")
