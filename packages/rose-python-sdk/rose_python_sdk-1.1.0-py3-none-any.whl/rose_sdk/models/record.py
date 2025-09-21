"""
Record models for the Rose Python SDK.
"""

from typing import List, Any
from pydantic import ConfigDict
from .base import BaseModel


class Record(BaseModel):
    """Record model."""

    model_config = ConfigDict(extra="allow")

    def __getitem__(self, key: str) -> Any:
        """Get value by field name."""
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set value by field name."""
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        """Check if field exists."""
        return hasattr(self, key)

    def keys(self):
        """Get all field names."""
        return [k for k in self.__dict__.keys() if not k.startswith("_")]

    def values(self):
        """Get all values."""
        return [getattr(self, k) for k in self.keys()]

    def items(self):
        """Get all field name-value pairs."""
        return [(k, getattr(self, k)) for k in self.keys()]

    def get(self, key: str, default=None):
        """Get value with default value."""
        return getattr(self, key, default)


class Records(BaseModel):
    """Records model."""

    model_config = ConfigDict(extra="allow")

    def __init__(self, **data):
        super().__init__(**data)
        if "records" not in data:
            self.records = []

    def __getitem__(self, index: int) -> Record:
        """Get record by index."""
        return self.records[index]

    def __setitem__(self, index: int, value: Record) -> None:
        """Set record by index."""
        self.records[index] = value

    def __len__(self) -> int:
        """Get number of records."""
        return len(self.records)

    def append(self, record: Record) -> None:
        """Append a record."""
        self.records.append(record)

    def extend(self, records: List[Record]) -> None:
        """Extend with more records."""
        self.records.extend(records)
