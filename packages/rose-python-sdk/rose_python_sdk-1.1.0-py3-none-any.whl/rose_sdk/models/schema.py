"""
Schema models for the Rose Python SDK.
"""

from typing import Any
from pydantic import ConfigDict
from .base import BaseModel

# Field import removed


class Schema(BaseModel):
    """Schema model defining dataset structure."""

    model_config = ConfigDict(extra="allow")

    def __getitem__(self, key: str) -> Any:
        """Get field by name."""
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set field by name."""
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        """Check if field exists."""
        return hasattr(self, key)

    def keys(self):
        """Get all field names."""
        return [k for k in self.__dict__.keys() if not k.startswith("_")]

    def values(self):
        """Get all fields."""
        return [getattr(self, k) for k in self.keys()]

    def items(self):
        """Get all field name-value pairs."""
        return [(k, getattr(self, k)) for k in self.keys()]

    def get(self, key: str, default=None):
        """Get field with default value."""
        return getattr(self, key, default)
