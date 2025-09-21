"""
Rose Python SDK

A Python SDK for interacting with the Rose Recommendation Service API.
"""

from .client import RoseClient
from .exceptions import (
    RoseAPIError,
    RoseAuthenticationError,
    RosePermissionError,
    RoseNotFoundError,
    RoseValidationError,
    RoseConflictError,
    RoseServerError,
    RoseTimeoutError,
)
from .utils import (
    build_schema_from_sample,
    build_schema_from_dict,
    convert_record_to_rose_format,
    convert_records_to_rose_format,
    convert_rose_record_to_simple,
    convert_rose_records_to_simple,
    generate_unique_account_id,
    create_account_with_conflict_handling,
    create_account_and_token_with_conflict_handling,
)
from .helpers import (
    quick_create_dataset,
    quick_add_records,
    quick_get_records,
    quick_create_dataset_with_data,
    quick_batch_upload,
    quick_get_recommendations,
    quick_setup_recommendation_system,
    get_dataset_summary,
)

__version__ = "1.1.0"
__all__ = [
    "RoseClient",
    "RoseAPIError",
    "RoseAuthenticationError",
    "RosePermissionError",
    "RoseNotFoundError",
    "RoseValidationError",
    "RoseConflictError",
    "RoseServerError",
    "RoseTimeoutError",
    "build_schema_from_sample",
    "build_schema_from_dict",
    "convert_record_to_rose_format",
    "convert_records_to_rose_format",
    "convert_rose_record_to_simple",
    "convert_rose_records_to_simple",
    "generate_unique_account_id",
    "create_account_with_conflict_handling",
    "create_account_and_token_with_conflict_handling",
    "quick_create_dataset",
    "quick_add_records",
    "quick_get_records",
    "quick_create_dataset_with_data",
    "quick_batch_upload",
    "quick_get_recommendations",
    "quick_setup_recommendation_system",
    "get_dataset_summary",
]
