"""
Pipeline service for the Rose Python SDK.
"""

from typing import List, Dict, Any
from ..models.pipeline import Pipeline, CreatePipelineRequest, CreatePipelineResponse, PipelineStatus
from ..models.query import Query


class PipelineService:
    """Service for pipeline management operations."""

    def __init__(self, client):
        self.client = client

    def list(self) -> List[Pipeline]:
        """
        List all pipelines of the account.

        Returns:
            List of Pipeline objects
        """
        response = self.client.get("/pipelines")
        return [Pipeline(**pipeline_data) for pipeline_data in response["data"]]

    def create(self, name: str, properties: Dict[str, Any]) -> CreatePipelineResponse:
        """
        Create a new pipeline.

        Args:
            name: The pipeline name
            properties: The pipeline properties

        Returns:
            CreatePipelineResponse object
        """
        data = CreatePipelineRequest(pipeline_name=name, properties=properties)
        response = self.client.post("/pipelines", data=data.model_dump())
        return CreatePipelineResponse(**response["data"])

    def get(self, pipeline_id: str) -> Pipeline:
        """
        Get a specific pipeline.

        Args:
            pipeline_id: The pipeline ID

        Returns:
            Pipeline object
        """
        response = self.client.get(f"/pipelines/{pipeline_id}")
        return Pipeline(**response["data"])

    def update(self, pipeline_id: str, properties: Dict[str, Any]) -> None:
        """
        Update a specific pipeline.

        Args:
            pipeline_id: The pipeline ID
            properties: The new pipeline properties
        """

        self.client.put(f"/pipelines/{pipeline_id}", data=properties)

    def delete(self, pipeline_id: str) -> None:
        """
        Delete a specific pipeline.

        Args:
            pipeline_id: The pipeline ID
        """
        self.client.delete(f"/pipelines/{pipeline_id}")

    def list_queries(self, pipeline_id: str) -> List[Query]:
        """
        List all queries of a pipeline.

        Args:
            pipeline_id: The pipeline ID

        Returns:
            List of Query objects

        Raises:
            ValueError: If pipeline status is not "CREATE SUCCESSFUL"
        """
        # First check the pipeline status
        pipeline = self.get(pipeline_id)

        if pipeline.status != PipelineStatus.CREATE_SUCCESSFUL:
            raise ValueError(
                f"Cannot list queries for pipeline {pipeline_id}. "
                f"Pipeline status is '{pipeline.status}', but must be 'CREATE SUCCESSFUL'"
            )

        response = self.client.get(f"/pipelines/{pipeline_id}/queries")
        return [Query(**query_data) for query_data in response["data"]]
