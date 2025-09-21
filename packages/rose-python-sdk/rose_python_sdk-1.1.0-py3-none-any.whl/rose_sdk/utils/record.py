"""
Record conversion utilities for the Rose Python SDK.

This module provides functions for converting between simple Python data structures
and the Rose API format, as well as validation utilities for record data.
"""

from typing import Dict, Any, List, Union, Optional
from datetime import datetime, date, time

# Time import removed


def convert_record_to_rose_format(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a simple Python dictionary record to Rose API format.

    Args:
        record: Simple dictionary record

    Returns:
        Dict in Rose API format

    Example:
        Input: {"user_id": "user123", "rating": 4.5, "active": True}
        Output: {
            "user_id": {"str": "user123"},
            "rating": {"float": 4.5},
            "active": {"bool": True}
        }
    """
    rose_record = {}

    for field_name, value in record.items():
        rose_record[field_name] = _convert_value_to_rose_format(value)

    return rose_record


def convert_records_to_rose_format(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of simple Python dictionary records to Rose API format.

    Args:
        records: List of simple dictionary records

    Returns:
        List of records in Rose API format
    """
    return [convert_record_to_rose_format(record) for record in records]


def _convert_value_to_rose_format(value: Any) -> Dict[str, Any]:
    """
    Convert a single value to Rose API format.

    Args:
        value: The value to convert

    Returns:
        Dict in Rose API format
    """
    if value is None:
        return {"str": ""}  # Empty string for None values

    if isinstance(value, bool):
        return {"bool": value}
    elif isinstance(value, int):
        return {"int": value}
    elif isinstance(value, float):
        return {"float": value}
    elif isinstance(value, str):
        return {"str": value}
    elif isinstance(value, datetime):
        return {"str": value.isoformat()}
    elif isinstance(value, date):
        return {"str": value.isoformat()}
    elif isinstance(value, time):
        return {"str": value.isoformat()}
    elif isinstance(value, list):
        return {"list": [_convert_value_to_rose_format(item) for item in value]}
    elif isinstance(value, dict):
        return {"map": {k: _convert_value_to_rose_format(v) for k, v in value.items()}}
    else:
        # Convert to string as fallback
        return {"str": str(value)}


def convert_rose_record_to_simple(rose_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a Rose API format record to a simple Python dictionary.

    Args:
        rose_record: Record in Rose API format

    Returns:
        Simple dictionary record

    Example:
        Input: {
            "user_id": {"str": "user123"},
            "rating": {"float": 4.5},
            "active": {"bool": True}
        }
        Output: {"user_id": "user123", "rating": 4.5, "active": True}
    """
    simple_record = {}

    for field_name, rose_value in rose_record.items():
        simple_record[field_name] = _convert_rose_value_to_simple(rose_value)

    return simple_record


def convert_rose_records_to_simple(rose_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of Rose API format records to simple Python dictionaries.

    Args:
        rose_records: List of records in Rose API format

    Returns:
        List of simple dictionary records
    """
    return [convert_rose_record_to_simple(record) for record in rose_records]


def _convert_rose_value_to_simple(rose_value: Any) -> Any:
    """
    Convert a single Rose API format value to a simple Python value.

    Args:
        rose_value: The value in Rose API format

    Returns:
        Simple Python value
    """
    if not isinstance(rose_value, dict):
        return rose_value

    # Check for type-specific values
    if "bool" in rose_value:
        return rose_value["bool"]
    elif "int" in rose_value:
        return rose_value["int"]
    elif "float" in rose_value:
        return rose_value["float"]
    elif "str" in rose_value:
        return rose_value["str"]
    elif "list" in rose_value:
        return [_convert_rose_value_to_simple(item) for item in rose_value["list"]]
    elif "map" in rose_value:
        return {k: _convert_rose_value_to_simple(v) for k, v in rose_value["map"].items()}
    else:
        # If it's a dict but doesn't match Rose format, return as-is
        return rose_value


def convert_timestamp_to_rose_format(timestamp: Union[int, float, str, datetime]) -> Dict[str, Any]:
    """
    Convert various timestamp formats to Rose API format.

    Args:
        timestamp: Timestamp in various formats

    Returns:
        Dict in Rose API format with "int" key
    """
    if isinstance(timestamp, datetime):
        return {"int": int(timestamp.timestamp())}
    elif isinstance(timestamp, (int, float)):
        return {"int": int(timestamp)}
    elif isinstance(timestamp, str):
        try:
            # Try to parse as ISO format
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return {"int": int(dt.timestamp())}
        except ValueError:
            try:
                # Try to parse as Unix timestamp string
                return {"int": int(float(timestamp))}
            except ValueError:
                # Fallback to string
                return {"str": timestamp}
    else:
        return {"str": str(timestamp)}


def convert_list_to_rose_format(value_list: List[Any], element_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert a Python list to Rose API format with optional type specification.

    Args:
        value_list: List of values to convert
        element_type: Optional type hint for list elements

    Returns:
        Dict in Rose API format with "list" key
    """
    if element_type:
        # Convert with specific type
        converted_list = []
        for item in value_list:
            if element_type == "str":
                converted_list.append({"str": str(item)})
            elif element_type == "int":
                converted_list.append({"int": str(int(item))})
            elif element_type == "float":
                converted_list.append({"float": str(float(item))})
            elif element_type == "bool":
                converted_list.append({"bool": str(bool(item))})
            else:
                converted_list.append(_convert_value_to_rose_format(item))
    else:
        # Auto-convert based on element types
        converted_list = [_convert_value_to_rose_format(item) for item in value_list]

    return {"list": converted_list}


def convert_map_to_rose_format(value_map: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a Python dictionary to Rose API format.

    Args:
        value_map: Dictionary to convert

    Returns:
        Dict in Rose API format with "map" key
    """
    converted_map = {}
    for key, value in value_map.items():
        converted_map[key] = _convert_value_to_rose_format(value)

    return {"map": converted_map}


def validate_rose_record_format(record: Dict[str, Any]) -> bool:
    """
    Validate that a record is in proper Rose API format.

    Args:
        record: Record to validate

    Returns:
        True if valid, False otherwise
    """
    for field_name, value in record.items():
        if not isinstance(value, dict):
            return False

        # Check that it has exactly one of the valid type keys
        valid_keys = {"bool", "int", "float", "str", "list", "map"}
        if not any(key in value for key in valid_keys):
            return False

        # Recursively validate nested structures
        if "list" in value:
            if not isinstance(value["list"], list):
                return False
            for item in value["list"]:
                if not validate_rose_record_format({"_": item}):
                    return False

        if "map" in value:
            if not isinstance(value["map"], dict):
                return False
            for nested_value in value["map"].values():
                if not validate_rose_record_format({"_": nested_value}):
                    return False

    return True
