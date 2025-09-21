"""
Role models for the Rose Python SDK.
"""

from typing import Optional
from .base import BaseModel


class Role(BaseModel):
    """Role model."""

    account_id: str
    role_name: str
    role_id: str
    permission: Optional[str] = None
    expired_at: Optional[int] = None


class RoleWithToken(Role):
    """Role model with access token."""

    token: str


class CreateRoleRequest(BaseModel):
    """Request model for creating a role."""

    role_name: str
    permission: Optional[str] = None


class UpdateRoleRequest(BaseModel):
    """Request model for updating a role."""

    permission: str
