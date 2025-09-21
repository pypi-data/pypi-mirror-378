"""
Batch data processing utilities for the Rose Python SDK.

This module provides functions for preparing and processing batch data
for efficient upload to the Rose API.
"""

import json
import gzip
from typing import List, Dict, Any


def prepare_batch_data(records: List[Dict[str, Any]]) -> bytes:
    """
    Converts a list of records to NDJSON format and compresses it with gzip.
    The records are expected to be in the Rose server's Value format.

    Args:
        records: List of records in Rose API format

    Returns:
        Compressed NDJSON data as bytes
    """
    ndjson_data = "\n".join(json.dumps(record) for record in records)
    compressed_data = gzip.compress(ndjson_data.encode("utf-8"))
    return compressed_data


def get_batch_headers() -> Dict[str, str]:
    """
    Returns the required headers for batch upload operations.

    Returns:
        Dictionary of headers for batch upload
    """
    return {"Content-Type": "application/x-ndjson", "Content-Encoding": "gzip"}


def validate_batch_records(records: List[Dict[str, Any]]) -> List[str]:
    """
    Validate batch records for common issues.

    Args:
        records: List of records to validate

    Returns:
        List of validation warnings/errors
    """
    warnings = []

    if not records:
        warnings.append("No records provided for batch upload")
        return warnings

    # Check for empty records
    for i, record in enumerate(records):
        if not record:
            warnings.append(f"Record {i+1} is empty")
        elif not isinstance(record, dict):
            warnings.append(f"Record {i+1} is not a dictionary")

    # Check for very large batches
    if len(records) > 10000:
        warnings.append(f"Large batch size ({len(records)} records) - consider splitting into smaller batches")

    return warnings


def split_batch_records(records: List[Dict[str, Any]], max_batch_size: int = 1000) -> List[List[Dict[str, Any]]]:
    """
    Split a large batch of records into smaller chunks.

    Args:
        records: List of records to split
        max_batch_size: Maximum number of records per batch

    Returns:
        List of record batches
    """
    if not records:
        return []

    batches = []
    for i in range(0, len(records), max_batch_size):
        batch = records[i : i + max_batch_size]
        batches.append(batch)

    return batches


def estimate_batch_size(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Estimate the size of a batch for upload planning.

    Args:
        records: List of records to analyze

    Returns:
        Dictionary with size estimates
    """
    if not records:
        return {"record_count": 0, "estimated_size_bytes": 0, "estimated_size_mb": 0.0}

    # Calculate average record size
    total_chars = 0
    for record in records:
        total_chars += len(json.dumps(record))

    avg_record_size = total_chars / len(records)
    total_size = total_chars

    # Estimate compressed size (typically 60-80% of original)
    compressed_size = int(total_size * 0.7)

    return {
        "record_count": len(records),
        "estimated_size_bytes": compressed_size,
        "estimated_size_mb": round(compressed_size / (1024 * 1024), 2),
        "average_record_size_bytes": int(avg_record_size),
    }
