"""
High-level helper functions for the Rose Python SDK.
These functions provide a simplified interface for common operations.
"""

from typing import Dict, Any, List, Optional
from .client import RoseClient
from .utils import (
    build_schema_from_sample,
    convert_records_to_rose_format,
    convert_rose_records_to_simple,
)


def quick_create_dataset(
    client: RoseClient,
    name: str,
    sample_records: List[Dict[str, Any]],
    identifier_fields: Optional[List[str]] = None,
    required_fields: Optional[List[str]] = None,
    enable_housekeeping: bool = True,
) -> str:
    """
    Quickly create a dataset from sample records.

    Args:
        client: RoseClient instance
        name: Dataset name
        sample_records: Sample records to infer schema from
        identifier_fields: List of field names that should be identifiers
        required_fields: List of field names that should be required
        enable_housekeeping: Whether to enable housekeeping

    Returns:
        Dataset ID
    """
    # Build schema from sample records
    schema = build_schema_from_sample(
        sample_records=sample_records, identifier_fields=identifier_fields, required_fields=required_fields
    )

    # Create dataset
    dataset_response = client.datasets.create(name=name, schema=schema, enable_housekeeping=enable_housekeeping)

    return dataset_response.dataset_id


def quick_add_records(client: RoseClient, dataset_id: str, records: List[Dict[str, Any]]) -> None:
    """
    Quickly add records to a dataset, automatically converting format.

    Args:
        client: RoseClient instance
        dataset_id: Dataset ID
        records: List of simple dictionary records
    """
    # Convert records to Rose format
    rose_records = convert_records_to_rose_format(records)

    # Add records
    client.datasets.records.create(dataset_id, rose_records)


def quick_get_records(client: RoseClient, dataset_id: str, size: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Quickly get records from a dataset, automatically converting format.

    Args:
        client: RoseClient instance
        dataset_id: Dataset ID
        size: Number of records to retrieve

    Returns:
        List of simple dictionary records
    """
    # Get records in Rose format
    rose_records = client.datasets.records.list(dataset_id, size=size)

    # Convert to simple format
    return convert_rose_records_to_simple(rose_records)


def quick_create_dataset_with_data(
    client: RoseClient,
    name: str,
    records: List[Dict[str, Any]],
    identifier_fields: Optional[List[str]] = None,
    required_fields: Optional[List[str]] = None,
    enable_housekeeping: bool = True,
) -> str:
    """
    Create a dataset and immediately add data to it.

    Args:
        client: RoseClient instance
        name: Dataset name
        records: Records to add to the dataset
        identifier_fields: List of field names that should be identifiers
        required_fields: List of field names that should be required
        enable_housekeeping: Whether to enable housekeeping

    Returns:
        Dataset ID
    """
    # Create dataset
    dataset_id = quick_create_dataset(
        client=client,
        name=name,
        sample_records=records,
        identifier_fields=identifier_fields,
        required_fields=required_fields,
        enable_housekeeping=enable_housekeeping,
    )

    # Add records
    quick_add_records(client, dataset_id, records)

    return dataset_id


def quick_batch_upload(
    client: RoseClient, dataset_id: str, records: List[Dict[str, Any]], mode: str = "append"
) -> Optional[str]:
    """
    Quickly upload a batch of records.

    Args:
        client: RoseClient instance
        dataset_id: Dataset ID
        records: Records to upload
        mode: Upload mode ("append" or "overwrite")

    Returns:
        Batch ID if mode is "overwrite", None if "append"
    """
    # Convert records to Rose format
    rose_records = convert_records_to_rose_format(records)

    if mode == "append":
        client.datasets.batch.upload_append(dataset_id, rose_records)
        return None
    elif mode == "overwrite":
        batch_id = client.datasets.batch.start_upload(dataset_id)
        client.datasets.batch.upload_batch(dataset_id, batch_id, rose_records)
        client.datasets.batch.complete_upload(dataset_id, batch_id)
        return batch_id
    else:
        raise ValueError("Mode must be 'append' or 'overwrite'")


def quick_get_recommendations(
    client: RoseClient, query_id: str, user_ids: List[str], batch: bool = False
) -> List[Dict[str, Any]]:
    """
    Quickly get recommendations for multiple users.

    Args:
        client: RoseClient instance
        query_id: Query ID
        user_ids: List of user IDs
        batch: Whether to use batch query (more efficient for multiple users)

    Returns:
        List of recommendation results
    """
    if batch and len(user_ids) > 1:
        # Use batch query
        payload = [{"user_id": user_id} for user_id in user_ids]
        recommendations = client.recommendations.batch_query(query_id, payload)
        return [rec.data for rec in recommendations]
    else:
        # Use individual queries
        results = []
        for user_id in user_ids:
            recommendation = client.recommendations.get(query_id=query_id, parameters={"user_id": user_id})
            results.append(recommendation.data)
        return results


def quick_setup_recommendation_system(
    client: RoseClient,
    dataset_name: str,
    records: List[Dict[str, Any]],
    pipeline_name: str,
    pipeline_properties: Dict[str, Any],
    identifier_fields: Optional[List[str]] = None,
    required_fields: Optional[List[str]] = None,
) -> tuple[str, str, List[str]]:
    """
    Quickly set up a complete recommendation system.

    Args:
        client: RoseClient instance
        dataset_name: Name for the dataset
        records: Training data records
        pipeline_name: Name for the pipeline
        pipeline_properties: Pipeline configuration
        identifier_fields: List of field names that should be identifiers
        required_fields: List of field names that should be required

    Returns:
        Tuple of (dataset_id, pipeline_id, query_ids)
    """
    # Create dataset with data
    dataset_id = quick_create_dataset_with_data(
        client=client, name=dataset_name, records=records, identifier_fields=identifier_fields, required_fields=required_fields
    )

    # Create pipeline
    pipeline_response = client.pipelines.create(name=pipeline_name, properties=pipeline_properties)
    pipeline_id = pipeline_response.pipeline_id

    # Get queries from pipeline
    queries = client.pipelines.list_queries(pipeline_id)
    query_ids = [query.query_id for query in queries]

    return dataset_id, pipeline_id, query_ids


def validate_and_convert_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and convert records to Rose format.

    Args:
        records: List of simple dictionary records

    Returns:
        List of records in Rose format

    Raises:
        ValueError: If records are invalid
    """
    if not records:
        raise ValueError("Records list cannot be empty")

    # Convert to Rose format
    rose_records = convert_records_to_rose_format(records)

    # Basic validation
    for i, record in enumerate(rose_records):
        if not record:
            raise ValueError(f"Record {i} is empty")

        for field_name, value in record.items():
            if not isinstance(value, dict):
                raise ValueError(f"Record {i}, field '{field_name}' is not in Rose format")

            # Check for valid type keys
            valid_keys = {"bool", "int", "float", "str", "list", "map"}
            if not any(key in value for key in valid_keys):
                raise ValueError(f"Record {i}, field '{field_name}' has no valid type key")

    return rose_records


def get_dataset_summary(client: RoseClient, dataset_id: str) -> Dict[str, Any]:
    """
    Get a summary of a dataset including schema and record count.

    Args:
        client: RoseClient instance
        dataset_id: Dataset ID

    Returns:
        Dictionary with dataset summary
    """
    # Get dataset info
    dataset = client.datasets.get(dataset_id)

    # Get sample records
    sample_records = client.datasets.records.list(dataset_id, size=5)
    simple_records = convert_rose_records_to_simple(sample_records)

    return {
        "dataset_id": dataset.dataset_id,
        "dataset_name": dataset.dataset_name,
        "status": dataset.status,
        "schema": dataset.schema,
        "sample_records": simple_records,
        "sample_count": len(simple_records),
    }
