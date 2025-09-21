"""
Recommendation models for the Rose Python SDK.
"""

from typing import List, Dict, Any
from .base import BaseModel


class Recommendation(BaseModel):
    """Recommendation model."""

    data: List[Dict[str, Any]]


class RecommendationFileInfo(BaseModel):
    """Recommendation file info model."""

    url: str


class RecommendationExportInfo(BaseModel):
    """Recommendation export info model."""

    export: Dict[str, RecommendationFileInfo]


class BulkRequest(BaseModel):
    """Bulk request model."""

    payload: List[Dict[str, Any]]
