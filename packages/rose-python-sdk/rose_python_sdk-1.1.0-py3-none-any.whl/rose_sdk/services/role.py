"""
Role service for the Rose Python SDK.
"""

from typing import List, Optional
from ..models.role import Role, RoleWithToken, CreateRoleRequest, UpdateRoleRequest


class RoleService:
    """Service for role management operations."""

    def __init__(self, client):
        self.client = client

    def list(self) -> List[Role]:
        """
        List all roles of the account.

        Returns:
            List of Role objects
        """
        response = self.client.get("/roles")
        return [Role(**role_data) for role_data in response["data"]]

    def create(
        self,
        role_name: str,
        permission: Optional[str] = None,
        with_token: Optional[bool] = False,
        token_expiration: Optional[int] = None,
    ) -> Role:
        """
        Create a new role.

        Args:
            role_name: The name of the role
            permission: The permission in hex string
            with_token: Whether to issue a token for the role
            token_expiration: The expiration time of the access token in seconds
        Returns:
            Role object
        """
        data = CreateRoleRequest(role_name=role_name, permission=permission)
        response = self.client.post("/roles", data=data.model_dump())
        if with_token:
            try:
                return self.issue_token(response["data"]["role_id"], expiration=token_expiration)
            except Exception as e:
                print(f"Failed to issue token: {e}")
                return Role(**response["data"])
        return Role(**response["data"])

    def get(self, role_id: str) -> Role:
        """
        Get a specific role.

        Args:
            role_id: The role ID

        Returns:
            Role object
        """
        response = self.client.get(f"/roles/{role_id}")
        return Role(**response["data"])

    def update(self, role_id: str, permission: str) -> Role:
        """
        Update a specific role.

        Args:
            role_id: The role ID
            permission: The new permission in hex string

        Returns:
            Updated Role object
        """
        data = UpdateRoleRequest(permission=permission)
        response = self.client.put(f"/roles/{role_id}", data=data.model_dump())
        return Role(**response["data"])

    def delete(self, role_id: str) -> None:
        """
        Delete a specific role.

        Args:
            role_id: The role ID
        """
        self.client.delete(f"/roles/{role_id}")

    def issue_token(
        self, role_id: str, expired_at: Optional[int] = None, expiration: Optional[int] = None, tenant_id: Optional[str] = None
    ) -> RoleWithToken:
        """
        Issue a new access token to a specific role.

        Args:
            role_id: The role ID
            expired_at: The expiration time of the access token in seconds from now, can not be used with expiration
            expiration: The expiration time of the access token in seconds from now, can not be used with expired_at
            tenant_id: The tenant ID (account ID) for the X-KK-Tenant-Id header

        Returns:
            RoleWithToken object containing the access token
        """
        # Don't send expiration parameter if not specified (like curl command)
        import time

        params = {}
        if expired_at is not None and expired_at > 0:
            params["expiration"] = expired_at
        elif expiration is not None and expiration > 0:
            # Convert duration in seconds to Unix timestamp
            expired_at = int(time.time()) + expiration
            params["expiration"] = expired_at
        else:
            raise ValueError("Either expired_at or expiration must be provided")

        # Add tenant ID header for token issuance if provided
        headers = {}
        if tenant_id:
            headers["X-KK-Tenant-Id"] = tenant_id
            response = self.client.post_with_basic_auth(f"/roles/{role_id}/token", params=params, headers=headers)
        else:
            response = self.client.post(f"/roles/{role_id}/token", params=params)

        return RoleWithToken(**response["data"])

    def revoke_token(self, role_id: str) -> None:
        """
        Revoke an access token of a specific role.

        Args:
            role_id: The role ID
        """
        self.client.delete(f"/roles/{role_id}/token")
