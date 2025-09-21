"""
Schema utilities for the Rose Python SDK.

This module provides functions for building schemas from sample data,
validating data against schemas, and managing schema information.
"""

from typing import Dict, Any, List, Tuple, Set
from datetime import datetime, date, time
from ..models.field import FieldType, Field
from ..exceptions import RoseAPIError


class SchemaValidationError(RoseAPIError):
    """Exception raised when data doesn't match the expected schema."""

    pass


# ============================================================================
# Schema Building Functions
# ============================================================================


def infer_field_type(value: Any) -> FieldType:
    """
    Infer the field type from a sample value.

    Args:
        value: Sample value to analyze

    Returns:
        Inferred FieldType
    """
    if value is None:
        return FieldType.STRING
    elif isinstance(value, bool):
        return FieldType.BOOLEAN
    elif isinstance(value, int):
        return FieldType.INTEGER
    elif isinstance(value, float):
        return FieldType.FLOAT
    elif isinstance(value, str):
        if _is_datetime_string(value):
            return FieldType.STRING  # Keep as string for datetime
        elif _is_date_string(value):
            return FieldType.STRING  # Keep as string for date
        elif _is_time_string(value):
            return FieldType.STRING  # Keep as string for time
        elif _is_timestamp_string(value):
            return FieldType.INTEGER  # Convert to int for timestamp
        else:
            return FieldType.STRING
    elif isinstance(value, list):
        return FieldType.LIST
    elif isinstance(value, dict):
        return FieldType.MAP
    elif isinstance(value, (datetime, date, time)):
        return FieldType.STRING  # Convert datetime objects to string
    else:
        return FieldType.STRING


def _is_datetime_string(value: str) -> bool:
    """Check if string is a datetime format."""
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def _is_date_string(value: str) -> bool:
    """Check if string is a date format."""
    try:
        datetime.strptime(value, "%Y-%m-%d").date()
        return True
    except (ValueError, TypeError):
        return False


def _is_time_string(value: str) -> bool:
    """Check if string is a time format."""
    try:
        datetime.strptime(value, "%H:%M:%S").time()
        return True
    except (ValueError, TypeError):
        return False


def _is_timestamp_string(value: str) -> bool:
    """Check if string is a timestamp (numeric)."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def create_field_definition(field_name: str, value: Any, is_required: bool = True, is_identifier: bool = False) -> Field:
    """
    Create a field definition from a sample value.

    Args:
        field_name: Name of the field
        value: Sample value
        is_required: Whether the field is required
        is_identifier: Whether the field is an identifier

    Returns:
        Field definition
    """
    field_type = infer_field_type(value)

    # Create list properties if it's a list
    list_props = None
    if field_type == FieldType.LIST and isinstance(value, list) and value:
        # Infer element type from first non-None item
        element_type = None
        for item in value:
            if item is not None:
                element_type = infer_field_type(item)
                break

        if element_type:
            list_props = {
                "children": {"field_type": element_type.value, "is_identifier": False, "is_required": False},
                "unique": False,
            }

    return Field(field_type=field_type, is_required=is_required, is_identifier=is_identifier, list_props=list_props)


def build_schema_from_sample(
    sample_records: List[Dict[str, Any]], identifier_fields: List[str] | None = None, required_fields: List[str] | None = None
) -> Dict[str, Field]:
    """
    Build a schema from sample records.

    Args:
        sample_records: List of sample records
        identifier_fields: List of field names that are identifiers
        required_fields: List of field names that are required

    Returns:
        Dictionary mapping field names to Field definitions
    """
    if not sample_records:
        return {}

    # Collect all unique field names
    all_fields: Set[str] = set()
    for record in sample_records:
        all_fields.update(record.keys())

    # Set defaults
    if identifier_fields is None:
        identifier_fields = []
    if required_fields is None:
        required_fields = list(all_fields)

    schema = {}

    for field_name in all_fields:
        # Collect all values for this field
        field_values = []
        for record in sample_records:
            if field_name in record:
                field_values.append(record[field_name])

        if not field_values:
            continue

        # Determine if field is required and identifier
        is_required = field_name in required_fields
        is_identifier = field_name in identifier_fields

        # Get most common non-None value for type inference
        non_none_values = [v for v in field_values if v is not None]
        if non_none_values:
            # Use the most common type
            sample_value = _get_most_common_type({type(v) for v in non_none_values}, non_none_values)
        else:
            sample_value = None

        # Create field definition
        schema[field_name] = create_field_definition(field_name, sample_value, is_required, is_identifier)

    return schema


def _get_most_common_type(types: set, values: list) -> type:
    """Get the most common type from a set of types and values."""
    if len(types) == 1:
        return list(types)[0]

    # Count occurrences of each type
    type_counts: Dict[str, int] = {}
    for value in values:
        value_type = type(value)
        type_counts[value_type] = type_counts.get(value_type, 0) + 1

    # Return the most common type
    return max(type_counts.items(), key=lambda x: x[1])[0]


def build_schema_from_dict(schema_dict: Dict[str, Any]) -> Dict[str, Field]:
    """
    Build a schema from a dictionary definition.

    Args:
        schema_dict: Dictionary with field definitions

    Returns:
        Dictionary mapping field names to Field definitions
    """
    schema = {}

    for field_name, field_config in schema_dict.items():
        if isinstance(field_config, dict):
            field_type = FieldType(field_config.get("field_type", "string"))
            is_required = field_config.get("is_required", True)
            is_identifier = field_config.get("is_identifier", False)
            list_props = field_config.get("list_props")

            schema[field_name] = Field(
                field_type=field_type, is_required=is_required, is_identifier=is_identifier, list_props=list_props
            )

    return schema


# ============================================================================
# Schema Validation Functions
# ============================================================================


def validate_and_align_records(
    records: List[Dict[str, Any]], dataset_schema: Dict[str, Any], strict_validation: bool = True
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Validate and align records against a dataset schema.

    This function checks if the user's data matches the dataset schema requirements
    and provides helpful feedback for alignment.

    Args:
        records: List of records to validate and align
        dataset_schema: The dataset schema definition
        strict_validation: If True, enforce strict validation. If False, provide warnings.

    Returns:
        Tuple of (aligned_records, validation_warnings)

    Raises:
        SchemaValidationError: If validation fails
    """
    if not records:
        return [], []

    aligned_records = []
    all_warnings = []

    # Extract field information from schema
    schema_fields = {}

    # Handle different schema types
    if hasattr(dataset_schema, "model_extra") and dataset_schema.model_extra:
        # Pydantic model with extra fields
        for field_name, field_config in dataset_schema.model_extra.items():
            if isinstance(field_config, dict):
                schema_fields[field_name] = {
                    "type": field_config.get("field_type", "string"),
                    "required": field_config.get("is_required", False),
                    "identifier": field_config.get("is_identifier", False),
                }
    elif hasattr(dataset_schema, "items"):
        # Use items() method for both Schema objects and dictionaries
        for field_name, field_config in dataset_schema.items():
            if isinstance(field_config, dict):
                schema_fields[field_name] = {
                    "type": field_config.get("field_type", "string"),
                    "required": field_config.get("is_required", False),
                    "identifier": field_config.get("is_identifier", False),
                }
    else:
        # Fallback for other types
        for field_name in dir(dataset_schema):
            if not field_name.startswith("_"):
                field_config = getattr(dataset_schema, field_name)
                if isinstance(field_config, dict):
                    schema_fields[field_name] = {
                        "type": field_config.get("field_type", "string"),
                        "required": field_config.get("is_required", False),
                        "identifier": field_config.get("is_identifier", False),
                    }

    for i, record in enumerate(records):
        try:
            aligned_record, warnings = _align_record_to_schema(record, schema_fields, strict_validation)
            aligned_records.append(aligned_record)
            all_warnings.extend([f"Record {i+1}: {w}" for w in warnings])
        except Exception as e:
            if strict_validation:
                raise SchemaValidationError(f"Record {i+1} validation failed: {e}")
            else:
                all_warnings.append(f"Record {i+1}: {e}")
                # Include the record as-is with warnings
                aligned_records.append(record)

    return aligned_records, all_warnings


def _align_record_to_schema(
    record: Dict[str, Any], schema_fields: Dict[str, Dict[str, Any]], strict_validation: bool = True
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Align a single record to the schema.

    Args:
        record: Record to align
        schema_fields: Schema field definitions
        strict_validation: Whether to enforce strict validation

    Returns:
        Tuple of (aligned_record, warnings)
    """
    warnings = []
    aligned_record = {}

    # Check for missing required fields
    for field_name, field_info in schema_fields.items():
        if field_info["required"] and field_name not in record:
            error_msg = f"Required field '{field_name}' is missing"
            if strict_validation:
                raise ValueError(error_msg)
            else:
                warnings.append(error_msg)
                aligned_record[field_name] = ""  # Default empty value

    # Process existing fields
    for field_name, value in record.items():
        if field_name in schema_fields:
            field_info = schema_fields[field_name]
            expected_type = field_info["type"]

            # Basic type checking and conversion suggestions
            if expected_type == "string" and not isinstance(value, str):
                if not strict_validation:
                    warnings.append(f"Field '{field_name}' should be string, got {type(value).__name__}")
                aligned_record[field_name] = str(value)
            elif expected_type == "int" and not isinstance(value, int):
                if not strict_validation:
                    warnings.append(f"Field '{field_name}' should be integer, got {type(value).__name__}")
                try:
                    aligned_record[field_name] = int(value)
                except (ValueError, TypeError):
                    if strict_validation:
                        raise ValueError(f"Cannot convert '{value}' to integer for field '{field_name}'")
                    aligned_record[field_name] = str(value)
            elif expected_type == "float" and not isinstance(value, (int, float)):
                if not strict_validation:
                    warnings.append(f"Field '{field_name}' should be float, got {type(value).__name__}")
                try:
                    aligned_record[field_name] = float(value)
                except (ValueError, TypeError):
                    if strict_validation:
                        raise ValueError(f"Cannot convert '{value}' to float for field '{field_name}'")
                    aligned_record[field_name] = str(value)
            else:
                aligned_record[field_name] = value
        else:
            # Field not in schema
            if not strict_validation:
                warnings.append(f"Field '{field_name}' not in schema, will be included")
            aligned_record[field_name] = value

    return aligned_record, warnings


def get_schema_summary(dataset_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of the dataset schema for user reference.

    Args:
        dataset_schema: The dataset schema definition

    Returns:
        Dictionary with schema summary
    """
    summary = {"total_fields": 0, "required_fields": [], "identifier_fields": [], "field_types": {}, "field_descriptions": {}}

    # Handle different schema types
    if hasattr(dataset_schema, "model_extra") and dataset_schema.model_extra:
        # Pydantic model with extra fields
        for field_name, field_config in dataset_schema.model_extra.items():
            if isinstance(field_config, dict):
                summary["total_fields"] += 1

                field_type = field_config.get("field_type", "string")
                summary["field_types"][field_name] = field_type

                if field_config.get("is_required", False):
                    summary["required_fields"].append(field_name)

                if field_config.get("is_identifier", False):
                    summary["identifier_fields"].append(field_name)

                if "description" in field_config:
                    summary["field_descriptions"][field_name] = field_config["description"]
    elif hasattr(dataset_schema, "items"):
        # Use items() method for both Schema objects and dictionaries
        for field_name, field_config in dataset_schema.items():
            if isinstance(field_config, dict):
                summary["total_fields"] += 1

                field_type = field_config.get("field_type", "string")
                summary["field_types"][field_name] = field_type

                if field_config.get("is_required", False):
                    summary["required_fields"].append(field_name)

                if field_config.get("is_identifier", False):
                    summary["identifier_fields"].append(field_name)

                if "description" in field_config:
                    summary["field_descriptions"][field_name] = field_config["description"]
    else:
        # Fallback for other types
        for field_name in dir(dataset_schema):
            if not field_name.startswith("_"):
                field_config = getattr(dataset_schema, field_name)
                if isinstance(field_config, dict):
                    summary["total_fields"] += 1

                    field_type = field_config.get("field_type", "string")
                    summary["field_types"][field_name] = field_type

                    if field_config.get("is_required", False):
                        summary["required_fields"].append(field_name)

                    if field_config.get("is_identifier", False):
                        summary["identifier_fields"].append(field_name)

                    if "description" in field_config:
                        summary["field_descriptions"][field_name] = field_config["description"]

    return summary


def print_schema_summary(dataset_schema: Dict[str, Any]) -> None:
    """
    Print a user-friendly summary of the dataset schema.

    Args:
        dataset_schema: The dataset schema definition
    """
    summary = get_schema_summary(dataset_schema)

    print("📋 Dataset Schema Summary")
    print("=" * 30)
    print(f"Total fields: {summary['total_fields']}")
    print(f"Required fields: {', '.join(summary['required_fields']) or 'None'}")
    print(f"Identifier fields: {', '.join(summary['identifier_fields']) or 'None'}")
    print()

    print("Field Details:")
    for field_name, field_type in summary["field_types"].items():
        required_marker = " (REQUIRED)" if field_name in summary["required_fields"] else ""
        identifier_marker = " (IDENTIFIER)" if field_name in summary["identifier_fields"] else ""

        print(f"  • {field_name}: {field_type}{required_marker}{identifier_marker}")

        if field_name in summary["field_descriptions"]:
            print(f"    Description: {summary['field_descriptions'][field_name]}")

    print()
