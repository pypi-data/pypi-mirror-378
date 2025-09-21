"""
Query models for the Rose Python SDK.
"""

from typing import Optional
from .base import BaseModel


class Query(BaseModel):
    """Query model."""

    pipeline_id: Optional[str] = None
    query_name: Optional[str] = None
    query_id: Optional[str] = None
    is_static: Optional[bool] = None
