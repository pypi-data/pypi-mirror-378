"""
Dataset service for the Rose Python SDK.
"""

import json
from typing import List, Optional, Dict, Any
from ..models.dataset import Dataset, CreateDatasetRequest, CreateDatasetResponse
from ..models.record import Record
from ..models.batch import BatchRecordsImportInfo
from ..utils.batch import prepare_batch_data, get_batch_headers


class DatasetService:
    """Service for dataset management operations."""

    def __init__(self, client):
        self.client = client
        self.records = DatasetRecordsService(client)
        self.batch = DatasetBatchService(client)

    def list(self) -> List[Dataset]:
        """
        List all datasets of the account.

        Returns:
            List of Dataset objects
        """
        response = self.client.get("/datasets")
        return [Dataset(**dataset_data) for dataset_data in response["data"]]

    def create(self, name: str, schema: Dict[str, Any], enable_housekeeping: Optional[bool] = True) -> CreateDatasetResponse:
        """
        Create a new dataset.

        Args:
            name: The dataset name
            schema: The dataset schema
            enable_housekeeping: Whether to enable housekeeping

        Returns:
            CreateDatasetResponse object
        """
        data = CreateDatasetRequest(dataset_name=name, schema=schema, enable_housekeeping=enable_housekeeping)
        response = self.client.post("/datasets", data=data.model_dump())
        return CreateDatasetResponse(**response["data"])

    def get(self, dataset_id: str) -> Dataset:
        """
        Get a specific dataset.

        Args:
            dataset_id: The dataset ID

        Returns:
            Dataset object
        """
        response = self.client.get(f"/datasets/{dataset_id}")
        return Dataset(**response["data"])

    def delete(self, dataset_id: str) -> None:
        """
        Delete a specific dataset.

        Args:
            dataset_id: The dataset ID
        """
        self.client.delete(f"/datasets/{dataset_id}")


class DatasetRecordsService:
    """Service for dataset records operations."""

    def __init__(self, client):
        self.client = client

    def list(self, dataset_id: str, size: Optional[int] = None) -> List[Record]:
        """
        Randomly list data records of a dataset.

        Args:
            dataset_id: The dataset ID
            size: The limit of number of records to be returned

        Returns:
            List of Record objects
        """
        params = {}
        if size is not None:
            params["size"] = size

        response = self.client.get(f"/datasets/{dataset_id}/records", params=params)
        return [Record(**record_data) for record_data in response["data"]]

    def create(self, dataset_id: str, records: List[Dict[str, Any]]) -> None:
        """
        Create new data records in a dataset.

        Args:
            dataset_id: The dataset ID
            records: List of data records
        """
        # Convert records to NDJSON format
        ndjson_data = "\n".join(json.dumps(record) for record in records)

        headers = {"Content-Type": "application/x-ndjson"}
        self.client._make_request("POST", f"/datasets/{dataset_id}/records", data=ndjson_data, headers=headers)

    def update(self, dataset_id: str, records: List[Dict[str, Any]]) -> None:
        """
        Update existing data records in a dataset or create new ones.

        Args:
            dataset_id: The dataset ID
            records: List of data records
        """
        # Convert records to NDJSON format
        ndjson_data = "\n".join(json.dumps(record) for record in records)

        headers = {"Content-Type": "application/x-ndjson"}
        self.client._make_request("PUT", f"/datasets/{dataset_id}/records", data=ndjson_data, headers=headers)

    def patch(self, dataset_id: str, records: List[Dict[str, Any]]) -> None:
        """
        Patch existing data records in a dataset.

        Args:
            dataset_id: The dataset ID
            records: List of data records
        """
        # Convert records to NDJSON format
        ndjson_data = "\n".join(json.dumps(record) for record in records)

        headers = {"Content-Type": "application/x-ndjson"}
        self.client._make_request("PATCH", f"/datasets/{dataset_id}/records", data=ndjson_data, headers=headers)

    def delete(self, dataset_id: str, records: List[Dict[str, Any]]) -> None:
        """
        Delete existing data records in a dataset.

        Args:
            dataset_id: The dataset ID
            records: List of data records (only identifiers required)
        """
        # Convert records to NDJSON format
        ndjson_data = "\n".join(json.dumps(record) for record in records)

        headers = {"Content-Type": "application/x-ndjson"}
        self.client._make_request("DELETE", f"/datasets/{dataset_id}/records", data=ndjson_data, headers=headers)


class DatasetBatchService:
    """Service for dataset batch operations."""

    def __init__(self, client):
        self.client = client

    def get_import_info(
        self, dataset_id: str, size: Optional[int] = 5, expiration: Optional[int] = 300
    ) -> BatchRecordsImportInfo:
        """
        Get batch records import information for append mode.

        Args:
            dataset_id: The dataset ID
            size: The number of import information to be returned (1-100, default: 5)
            expiration: The expiration time in seconds (default: 300)

        Returns:
            BatchRecordsImportInfo object
        """
        params = {}
        if size is not None:
            params["size"] = size
        if expiration is not None:
            params["expiration"] = expiration

        response = self.client.get(f"/datasets/{dataset_id}/batch:import", params=params)
        return BatchRecordsImportInfo(**response["data"])

    def upload_append(self, dataset_id: str, records: List[Dict[str, Any]]) -> None:
        """
        Upload a batch of records in append mode.

        Args:
            dataset_id: The dataset ID
            records: List of data records
        """
        # Prepare data with proper encoding and compression
        compressed_data = prepare_batch_data(records)
        headers = get_batch_headers()

        self.client._make_request("PUT", f"/datasets/{dataset_id}/batch:upload", data=compressed_data, headers=headers)

    def start_upload(self, dataset_id: str) -> str:
        """
        Start a batch records upload process for overwrite mode.

        Args:
            dataset_id: The dataset ID

        Returns:
            Batch ID for the upload process
        """
        response = self.client.post(f"/datasets/{dataset_id}/batch:start")
        return response["data"]["batch_id"]

    def get_batch_import_info(
        self, dataset_id: str, batch_id: str, size: Optional[int] = 5, expiration: Optional[int] = 300
    ) -> BatchRecordsImportInfo:
        """
        Get batch records import information for overwrite mode.

        Args:
            dataset_id: The dataset ID
            batch_id: The batch ID
            size: The number of import information to be returned (1-100, default: 5)
            expiration: The expiration time in seconds (default: 300)

        Returns:
            BatchRecordsImportInfo object
        """
        params = {}
        if size is not None:
            params["size"] = size
        if expiration is not None:
            params["expiration"] = expiration

        response = self.client.get(f"/datasets/{dataset_id}/batch/{batch_id}:import", params=params)
        return BatchRecordsImportInfo(**response["data"])

    def upload_batch(self, dataset_id: str, batch_id: str, records: List[Dict[str, Any]]) -> None:
        """
        Upload a batch of data records for overwrite mode.

        Args:
            dataset_id: The dataset ID
            batch_id: The batch ID
            records: List of data records
        """
        # Prepare data with proper encoding and compression
        compressed_data = prepare_batch_data(records)
        headers = get_batch_headers()

        self.client._make_request(
            "PUT", f"/datasets/{dataset_id}/batch/{batch_id}:upload", data=compressed_data, headers=headers
        )

    def abort_upload(self, dataset_id: str, batch_id: str) -> None:
        """
        Abort a batch records upload process.

        Args:
            dataset_id: The dataset ID
            batch_id: The batch ID
        """
        self.client.post(f"/datasets/{dataset_id}/batch/{batch_id}:abort")

    def complete_upload(self, dataset_id: str, batch_id: str) -> None:
        """
        Complete a batch records upload process.

        Args:
            dataset_id: The dataset ID
            batch_id: The batch ID
        """
        self.client.post(f"/datasets/{dataset_id}/batch/{batch_id}:complete")
