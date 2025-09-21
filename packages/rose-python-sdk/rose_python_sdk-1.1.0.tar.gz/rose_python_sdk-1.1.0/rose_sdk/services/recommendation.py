"""
Recommendation service for the Rose Python SDK.
"""

from typing import List, Dict, Any, Optional
from ..models.recommendation import Recommendation, RecommendationExportInfo, BulkRequest


class RecommendationService:
    """Service for recommendation operations."""

    def __init__(self, client):
        self.client = client

    def get(self, query_id: str, parameters: Optional[Dict[str, Any]] = None) -> Recommendation:
        """
        Get recommendation results from a specific query.

        Args:
            query_id: The query ID
            parameters: Parameters for the query

        Returns:
            Recommendation object
        """
        params = {}
        if parameters:
            # Flatten parameters for query string
            for key, value in parameters.items():
                params[f"parameters[{key}]"] = value

        response = self.client.get(f"/recommendations/{query_id}", params=params)
        return Recommendation(**response["data"])

    def batch_query(self, query_id: str, payload: List[Dict[str, Any]]) -> List[Recommendation]:
        """
        Batch request static (pre-computed) recommendation results.

        Args:
            query_id: The query ID
            payload: A bulk of parameter groups

        Returns:
            List of Recommendation objects
        """
        data = BulkRequest(payload=payload)
        response = self.client.post(f"/recommendations/{query_id}:batchQuery", data=data.model_dump())
        return [Recommendation(**rec_data) for rec_data in response["data"]]

    def get_export_info(self, query_id: str, expiration: Optional[int] = None) -> RecommendationExportInfo:
        """
        Get information about exported recommendation results.

        Args:
            query_id: The query ID
            expiration: The expiration time of the export information in seconds

        Returns:
            RecommendationExportInfo object
        """
        params = {}
        if expiration is not None:
            params["expiration"] = expiration

        response = self.client.get(f"/recommendations/{query_id}:export", params=params)
        return RecommendationExportInfo(**response["data"])
