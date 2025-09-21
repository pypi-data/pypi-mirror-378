"""
Dataset models for the Rose Python SDK.
"""

from typing import Optional
from .base import BaseModel
from .schema import Schema


class CreateDatasetRequest(BaseModel):
    """Request model for creating a dataset."""

    dataset_name: str
    schema: Schema
    enable_housekeeping: Optional[bool] = True


class CreateDatasetResponse(BaseModel):
    """Response model for creating a dataset."""

    dataset_id: str


class Dataset(BaseModel):
    """Dataset model."""

    account_id: str
    dataset_name: str
    dataset_id: str
    schema: Schema
    status: Optional[str] = None
    enable_housekeeping: Optional[bool] = True
