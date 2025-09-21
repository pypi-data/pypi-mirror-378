"""
Pipeline models for the Rose Python SDK.
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from enum import StrEnum


class CreatePipelineRequest(BaseModel):
    """Request model for creating a pipeline."""

    pipeline_name: str
    properties: Dict[str, Any]


class UpdatePipelineRequest(BaseModel):
    """Request model for updating a pipeline."""

    properties: Dict[str, Any]


class CreatePipelineResponse(BaseModel):
    """Response model for creating a pipeline."""

    pipeline_id: str


class Pipeline(BaseModel):
    """Pipeline model."""

    account_id: str
    pipeline_name: str
    pipeline_id: str
    status: Optional[str] = None
    properties: Dict[str, Any]


class PipelineStatus(StrEnum):
    CREATE_FAILED = "CREATE FAILED"
    CREATE_SUCCESSFUL = "CREATE SUCCESSFUL"
    DELETE_FAILED = "DELETE FAILED"
    DELETE_SUCCESSFUL = "DELETE SUCCESSFUL"
    UPDATE_FAILED = "UPDATE FAILED"
    UPDATE_SUCCESSFUL = "UPDATE SUCCESSFUL"
