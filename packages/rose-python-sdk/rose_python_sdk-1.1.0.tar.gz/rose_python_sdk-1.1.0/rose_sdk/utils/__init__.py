"""
Utility functions for the Rose Python SDK.

This module provides organized utility functions for common operations:
- Record conversion and validation
- Schema building and validation
- Batch data processing
- Pipeline creation and management
- Account management utilities
"""

# ============================================================================
# Record Conversion and Validation
# ============================================================================
from .record import (
    convert_record_to_rose_format,
    convert_records_to_rose_format,
    convert_rose_record_to_simple,
    convert_rose_records_to_simple,
    convert_timestamp_to_rose_format,
    convert_list_to_rose_format,
    convert_map_to_rose_format,
    validate_rose_record_format,
)

# ============================================================================
# Schema Building and Validation
# ============================================================================
from .schema import (
    # Schema building
    infer_field_type,
    create_field_definition,
    build_schema_from_sample,
    build_schema_from_dict,
    # Schema validation
    validate_and_align_records,
    get_schema_summary,
    print_schema_summary,
    SchemaValidationError,
)

# ============================================================================
# Batch Data Processing
# ============================================================================
from .batch import prepare_batch_data, get_batch_headers, validate_batch_records, split_batch_records, estimate_batch_size

# ============================================================================
# Pipeline Creation and Management
# ============================================================================
from .pipeline import (
    PipelineBuilder,
    create_pipeline,
    create_telasa_pipeline,
    create_realtime_leaderboard_pipeline,
    create_custom_pipeline,
    get_supported_scenarios,
)

# ============================================================================
# Account Management
# ============================================================================
from .account import (
    generate_unique_account_id,
    create_account_with_conflict_handling,
    create_account_and_token_with_conflict_handling,
)

# ============================================================================
# Public API
# ============================================================================
__all__ = [
    # Record conversion and validation
    "convert_record_to_rose_format",
    "convert_records_to_rose_format",
    "convert_rose_record_to_simple",
    "convert_rose_records_to_simple",
    "convert_timestamp_to_rose_format",
    "convert_list_to_rose_format",
    "convert_map_to_rose_format",
    "validate_rose_record_format",
    # Schema building and validation
    "infer_field_type",
    "create_field_definition",
    "build_schema_from_sample",
    "build_schema_from_dict",
    "validate_and_align_records",
    "get_schema_summary",
    "print_schema_summary",
    "SchemaValidationError",
    # Batch data processing
    "prepare_batch_data",
    "get_batch_headers",
    "validate_batch_records",
    "split_batch_records",
    "estimate_batch_size",
    # Pipeline creation and management
    "PipelineBuilder",
    "create_pipeline",
    "create_telasa_pipeline",
    "create_realtime_leaderboard_pipeline",
    "create_custom_pipeline",
    "get_supported_scenarios",
    # Account management
    "generate_unique_account_id",
    "create_account_with_conflict_handling",
    "create_account_and_token_with_conflict_handling",
]
