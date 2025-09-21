"""
Base models for the Rose Python SDK.
"""

# Base model for all data models
from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(populate_by_name=True, validate_assignment=True, use_enum_values=True)


class BaseResponse(BaseModel):
    """Base response model."""

    message: str


class OKResponse(BaseResponse):
    """OK response model."""

    message: str = "OK"


class AcceptedResponse(BaseResponse):
    """Accepted response model."""

    message: str = "Accepted"


class MultiStatusResponse(BaseResponse):
    """Multi-status response model."""

    message: str = "Multi-Status"


class ErrorResponse(BaseResponse):
    """Error response model."""

    error: str
