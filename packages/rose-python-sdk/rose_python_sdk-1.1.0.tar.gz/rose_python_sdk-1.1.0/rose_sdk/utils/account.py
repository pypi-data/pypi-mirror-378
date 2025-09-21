"""
Utility functions for account management with conflict handling.
"""

import time
import random
from typing import Optional
from ..exceptions import RoseConflictError
from ..models.role import Role


def generate_unique_account_id(base_id: str) -> str:
    """
    Generate a unique account ID by appending timestamp and random number.

    Args:
        base_id: Base account ID

    Returns:
        Unique account ID
    """
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    return f"{base_id}_{timestamp}_{random_num}"


def create_account_with_conflict_handling(
    client, account_id: str, max_retries: int = 3, auto_generate_unique: bool = True
) -> Role:
    """
    Create an account with automatic conflict handling.

    Args:
        client: RoseClient instance
        account_id: Desired account ID
        max_retries: Maximum number of retry attempts
        auto_generate_unique: If True, automatically generate unique IDs on conflict

    Returns:
        Role object for the created account

    Raises:
        RoseConflictError: If all retry attempts fail
        RoseAPIError: For other API errors
    """

    current_account_id = account_id

    for attempt in range(max_retries):
        try:
            role = client.accounts.create(current_account_id)
            return role

        except RoseConflictError as e:
            if attempt < max_retries - 1 and auto_generate_unique:
                # Generate a new unique account ID for next attempt
                current_account_id = generate_unique_account_id(account_id)
                print(f"⚠️  Account '{account_id}' exists, retrying with: {current_account_id}")
            else:
                # Last attempt failed or auto_generate_unique is False
                raise e

    # This should never be reached, but just in case
    raise RoseConflictError(f"Failed to create account after {max_retries} attempts")


def create_account_and_token_with_conflict_handling(
    client, account_id: str, max_retries: int = 3, auto_generate_unique: bool = True, expiration: Optional[int] = None
):
    """
    Create an account and issue a token with automatic conflict handling.

    Args:
        client: RoseClient instance
        account_id: Desired account ID
        max_retries: Maximum number of retry attempts
        auto_generate_unique: If True, automatically generate unique IDs on conflict
        expiration: Token expiration time in seconds (optional)

    Returns:
        Tuple of (Role, RoleWithToken) objects

    Raises:
        RoseConflictError: If all retry attempts fail
        RoseAPIError: For other API errors
    """

    # Create account with conflict handling
    role = create_account_with_conflict_handling(client, account_id, max_retries, auto_generate_unique)

    # Issue token
    role_with_token = client.roles.issue_token(role_id=role.role_id, tenant_id=role.account_id, expiration=expiration)

    return role, role_with_token
