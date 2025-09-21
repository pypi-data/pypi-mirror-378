"""
Account service for the Rose Python SDK.
"""

from typing import Optional
from ..models.role import Role, RoleWithToken


class AccountService:
    """Service for account management operations."""

    def __init__(self, client):
        self.client = client

    def create(self, account_id: str, expiration: Optional[int] = None) -> Role:
        """
        Create a new account with an "admin" role.

        Note: This only creates the account and admin role. No token is generated.
        Use create_with_token() to create account and get a token in one call.

        Args:
            account_id: The account ID to create
            expiration: The expiration time for future tokens in seconds

        Returns:
            Role object (without token - use issue_token to get a token)
        """
        data = {"account_id": account_id}
        params = {}
        if expiration is not None:
            params["expiration"] = expiration

        response = self.client.post_with_basic_auth("/accounts", data=data, params=params)
        return Role(**response["data"])

    def create_with_token(self, account_id: str, expiration: Optional[int] = None) -> RoleWithToken:
        """
        Create a new account with an "admin" role and immediately issue a token.

        This is a convenience method that combines create() and issue_token().

        Note: This requires RefreshAccessToken permission. If your token doesn't have
        this permission, use create() instead and issue tokens separately.

        Args:
            account_id: The account ID to create
            expiration: The expiration time of the access token in seconds

        Returns:
            RoleWithToken object with access token

        Raises:
            RosePermissionError: If the token doesn't have RefreshAccessToken permission
        """
        # First create the account (which creates the admin role)
        role = self.create(account_id, expiration)

        # Then issue a token for the admin role
        role_with_token = self.client.roles.issue_token(
            role_id=role.role_id,
            expiration=expiration or 3600,  # Default to 1 hour if not specified
            tenant_id=role.account_id,  # Pass account ID as tenant ID
        )

        return role_with_token
