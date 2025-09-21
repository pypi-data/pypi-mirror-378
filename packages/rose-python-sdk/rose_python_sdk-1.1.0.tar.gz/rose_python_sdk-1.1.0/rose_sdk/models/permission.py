"""
Permission models for the Rose Python SDK.

This module provides an intuitive way to manage role permissions based on the Go design.
"""

from enum import IntFlag
from typing import List


class Permission(IntFlag):
    """Permission flags using bitwise operations for efficient permission management."""

    # 01-08: recommendation result retrieval
    GET_RECOMMENDATIONS = 1 << 0
    # Reserved slots 1-7

    # 09-16: data record management
    LIST_RECORDS = 1 << 8
    GET_RECORDS = 1 << 9
    CREATE_RECORDS = 1 << 10
    UPDATE_RECORDS = 1 << 11
    DELETE_RECORDS = 1 << 12
    # Reserved slots 13-15

    # 17-24: data batch records process
    LIST_BATCH_RECORDS_PROCESSES = 1 << 16
    GET_BATCH_RECORDS_PROCESS = 1 << 17
    EXECUTE_BATCH_RECORDS_APPEND = 1 << 18
    EXECUTE_BATCH_RECORDS_OVERWRITE = 1 << 19
    # Reserved slots 20-23

    # 25-32: dataset management
    LIST_DATASETS = 1 << 24
    GET_DATASET = 1 << 25
    CREATE_DATASET = 1 << 26
    UPDATE_DATASET = 1 << 27
    DELETE_DATASET = 1 << 28
    # Reserved slots 29-31

    # 33-40: pipeline management
    LIST_PIPELINES = 1 << 32
    GET_PIPELINE = 1 << 33
    CREATE_PIPELINE = 1 << 34
    UPDATE_PIPELINE = 1 << 35
    DELETE_PIPELINE = 1 << 36
    # Reserved slots 37-39

    # 41-48: (reserved)

    # 49-56: (reserved)

    # 57-64: role management
    LIST_ROLES = 1 << 56
    GET_ROLE = 1 << 57
    CREATE_ROLE = 1 << 58
    UPDATE_ROLE = 1 << 59
    DELETE_ROLE = 1 << 60
    REFRESH_ACCESS_TOKEN = 1 << 61
    REVOKE_ACCESS_TOKEN = 1 << 62

    # Admin permissions (separate group)
    CREATE_ACCOUNT = 1 << 63
    UPDATE_ACCOUNT = 1 << 64
    DELETE_ACCOUNT = 1 << 65


class PermissionCategory:
    """Permission categories for better organization and intuitive setup."""

    # Basic permissions
    BABY = Permission(0)
    ROOT = Permission(0xFFFFFFFFFFFFFFFF)  # All permissions

    # Recommendation permissions
    RECOMMENDATION = Permission.GET_RECOMMENDATIONS

    # Data record permissions
    RECORD_READ = Permission.LIST_RECORDS | Permission.GET_RECORDS
    RECORD_WRITE = Permission.CREATE_RECORDS | Permission.UPDATE_RECORDS | Permission.DELETE_RECORDS
    RECORD_FULL = RECORD_READ | RECORD_WRITE

    # Batch processing permissions
    BATCH_READ = Permission.LIST_BATCH_RECORDS_PROCESSES | Permission.GET_BATCH_RECORDS_PROCESS
    BATCH_WRITE = Permission.EXECUTE_BATCH_RECORDS_APPEND | Permission.EXECUTE_BATCH_RECORDS_OVERWRITE
    BATCH_FULL = BATCH_READ | BATCH_WRITE

    # Dataset permissions
    DATASET_READ = Permission.LIST_DATASETS | Permission.GET_DATASET
    DATASET_WRITE = Permission.CREATE_DATASET | Permission.UPDATE_DATASET | Permission.DELETE_DATASET
    DATASET_FULL = DATASET_READ | DATASET_WRITE

    # Pipeline permissions
    PIPELINE_READ = Permission.LIST_PIPELINES | Permission.GET_PIPELINE
    PIPELINE_WRITE = Permission.CREATE_PIPELINE | Permission.UPDATE_PIPELINE | Permission.DELETE_PIPELINE
    PIPELINE_FULL = PIPELINE_READ | PIPELINE_WRITE

    # Role management permissions
    ROLE_READ = Permission.LIST_ROLES | Permission.GET_ROLE
    ROLE_WRITE = Permission.CREATE_ROLE | Permission.UPDATE_ROLE | Permission.DELETE_ROLE
    ROLE_TOKEN = Permission.REFRESH_ACCESS_TOKEN | Permission.REVOKE_ACCESS_TOKEN
    ROLE_FULL = ROLE_READ | ROLE_WRITE | ROLE_TOKEN

    # Account management permissions
    ACCOUNT_WRITE = Permission.CREATE_ACCOUNT | Permission.UPDATE_ACCOUNT | Permission.DELETE_ACCOUNT


class PredefinedRoles:
    """Predefined role templates matching the Go constants."""

    # Account admin - can manage roles and tokens
    ACCOUNT_ADMIN = PermissionCategory.BABY | PermissionCategory.ROLE_FULL

    # Read-only admin - can view all resources
    READ_ONLY_ADMIN = (
        Permission.GET_RECOMMENDATIONS
        | Permission.GET_RECORDS
        | Permission.LIST_RECORDS
        | Permission.GET_BATCH_RECORDS_PROCESS
        | Permission.GET_DATASET
        | Permission.LIST_DATASETS
        | Permission.GET_PIPELINE
        | Permission.LIST_PIPELINES
    )

    # Read-write admin - can view and modify all resources
    READ_WRITE_ADMIN = (
        READ_ONLY_ADMIN
        | Permission.CREATE_RECORDS
        | Permission.UPDATE_RECORDS
        | Permission.DELETE_RECORDS
        | Permission.EXECUTE_BATCH_RECORDS_APPEND
        | Permission.EXECUTE_BATCH_RECORDS_OVERWRITE
        | Permission.CREATE_DATASET
        | Permission.DELETE_DATASET
        | Permission.CREATE_PIPELINE
        | Permission.UPDATE_PIPELINE
        | Permission.DELETE_PIPELINE
    )

    # Data client - can create and update data
    DATA_CLIENT = (
        PermissionCategory.BABY
        | Permission.CREATE_RECORDS
        | Permission.UPDATE_RECORDS
        | Permission.EXECUTE_BATCH_RECORDS_APPEND
        | Permission.EXECUTE_BATCH_RECORDS_OVERWRITE
    )

    # Recommendation client - can only get recommendations
    REC_CLIENT = Permission.GET_RECOMMENDATIONS


class PermissionBuilder:
    """Builder class for creating custom permission sets intuitively."""

    def __init__(self):
        self._permissions = Permission(0)

    def add_recommendation_access(self) -> "PermissionBuilder":
        """Add recommendation access permissions."""
        self._permissions |= PermissionCategory.RECOMMENDATION
        return self

    def add_record_read(self) -> "PermissionBuilder":
        """Add record read permissions."""
        self._permissions |= PermissionCategory.RECORD_READ
        return self

    def add_record_write(self) -> "PermissionBuilder":
        """Add record write permissions."""
        self._permissions |= PermissionCategory.RECORD_WRITE
        return self

    def add_record_full(self) -> "PermissionBuilder":
        """Add full record permissions (read + write)."""
        self._permissions |= PermissionCategory.RECORD_FULL
        return self

    def add_batch_read(self) -> "PermissionBuilder":
        """Add batch processing read permissions."""
        self._permissions |= PermissionCategory.BATCH_READ
        return self

    def add_batch_write(self) -> "PermissionBuilder":
        """Add batch processing write permissions."""
        self._permissions |= PermissionCategory.BATCH_WRITE
        return self

    def add_batch_full(self) -> "PermissionBuilder":
        """Add full batch processing permissions."""
        self._permissions |= PermissionCategory.BATCH_FULL
        return self

    def add_dataset_read(self) -> "PermissionBuilder":
        """Add dataset read permissions."""
        self._permissions |= PermissionCategory.DATASET_READ
        return self

    def add_dataset_write(self) -> "PermissionBuilder":
        """Add dataset write permissions."""
        self._permissions |= PermissionCategory.DATASET_WRITE
        return self

    def add_dataset_full(self) -> "PermissionBuilder":
        """Add full dataset permissions."""
        self._permissions |= PermissionCategory.DATASET_FULL
        return self

    def add_pipeline_read(self) -> "PermissionBuilder":
        """Add pipeline read permissions."""
        self._permissions |= PermissionCategory.PIPELINE_READ
        return self

    def add_pipeline_write(self) -> "PermissionBuilder":
        """Add pipeline write permissions."""
        self._permissions |= PermissionCategory.PIPELINE_WRITE
        return self

    def add_pipeline_full(self) -> "PermissionBuilder":
        """Add full pipeline permissions."""
        self._permissions |= PermissionCategory.PIPELINE_FULL
        return self

    def add_role_management(self) -> "PermissionBuilder":
        """Add role management permissions."""
        self._permissions |= PermissionCategory.ROLE_FULL
        return self

    def add_account_management(self) -> "PermissionBuilder":
        """Add account management permissions."""
        self._permissions |= PermissionCategory.ACCOUNT_WRITE
        return self

    def add_custom_permission(self, permission: Permission) -> "PermissionBuilder":
        """Add a custom permission."""
        self._permissions |= permission
        return self

    def remove_permission(self, permission: Permission) -> "PermissionBuilder":
        """Remove a specific permission."""
        self._permissions &= ~permission
        return self

    def clear_permissions(self) -> "PermissionBuilder":
        """Clear all permissions."""
        self._permissions = Permission(0)
        return self

    def build(self) -> Permission:
        """Build and return the final permission set."""
        return self._permissions

    def build_as_string(self) -> str:
        """Build and return the permission as a string (for API calls)."""
        return str(self._permissions.value)

    def build_as_hex(self) -> str:
        """Build and return the permission as a hex string."""
        return hex(self._permissions.value)

    def build_as_base64(self) -> str:
        """Build and return the permission as a base64 string."""
        import base64

        return base64.b64encode(self._permissions.value.to_bytes(8, "big")).decode("utf-8")


class PermissionValidator:
    """Utility class for validating and checking permissions."""

    @staticmethod
    def has_permission(user_permissions: Permission, required_permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return bool(user_permissions & required_permission)

    @staticmethod
    def has_any_permission(user_permissions: Permission, required_permissions: List[Permission]) -> bool:
        """Check if user has any of the required permissions."""
        return any(user_permissions & perm for perm in required_permissions)

    @staticmethod
    def has_all_permissions(user_permissions: Permission, required_permissions: List[Permission]) -> bool:
        """Check if user has all of the required permissions."""
        return all(user_permissions & perm for perm in required_permissions)

    @staticmethod
    def get_missing_permissions(user_permissions: Permission, required_permissions: List[Permission]) -> List[Permission]:
        """Get list of missing permissions."""
        return [perm for perm in required_permissions if not (user_permissions & perm)]

    @staticmethod
    def get_permission_names(permissions: Permission) -> List[str]:
        """Get human-readable names of all permissions in the set."""
        permission_names = []
        for permission in Permission:
            if permissions & permission and permission.name:
                permission_names.append(permission.name)
        return permission_names

    @staticmethod
    def is_admin_role(permissions: Permission) -> bool:
        """Check if the permission set represents an admin role."""
        return bool(permissions & PermissionCategory.ROLE_FULL)

    @staticmethod
    def is_read_only(permissions: Permission) -> bool:
        """Check if the permission set is read-only."""
        read_permissions = (
            PermissionCategory.RECORD_READ
            | PermissionCategory.BATCH_READ
            | PermissionCategory.DATASET_READ
            | PermissionCategory.PIPELINE_READ
            | PermissionCategory.RECOMMENDATION
        )
        write_permissions = (
            PermissionCategory.RECORD_WRITE
            | PermissionCategory.BATCH_WRITE
            | PermissionCategory.DATASET_WRITE
            | PermissionCategory.PIPELINE_WRITE
        )
        return bool(permissions & read_permissions) and not bool(permissions & write_permissions)


# Convenience functions for quick permission setup
def create_read_only_role() -> Permission:
    """Create a read-only role permission set."""
    return PredefinedRoles.READ_ONLY_ADMIN


def create_data_client_role() -> Permission:
    """Create a data client role permission set."""
    return PredefinedRoles.DATA_CLIENT


def create_recommendation_client_role() -> Permission:
    """Create a recommendation client role permission set."""
    return PredefinedRoles.REC_CLIENT


def create_admin_role() -> Permission:
    """Create an admin role permission set."""
    return PredefinedRoles.READ_WRITE_ADMIN


def create_account_admin_role() -> Permission:
    """Create an account admin role permission set."""
    return PredefinedRoles.ACCOUNT_ADMIN


def create_custom_role(**kwargs) -> Permission:
    """
    Create a custom role with specified permissions.

    Args:
        **kwargs: Permission flags to include. Use permission names as keys with True/False values.
                 Example: create_custom_role(record_read=True, dataset_write=True)

    Returns:
        Permission: Custom permission set
    """
    builder = PermissionBuilder()

    # Map permission names to builder methods
    permission_map = {
        "recommendation": builder.add_recommendation_access,
        "record_read": builder.add_record_read,
        "record_write": builder.add_record_write,
        "record_full": builder.add_record_full,
        "batch_read": builder.add_batch_read,
        "batch_write": builder.add_batch_write,
        "batch_full": builder.add_batch_full,
        "dataset_read": builder.add_dataset_read,
        "dataset_write": builder.add_dataset_write,
        "dataset_full": builder.add_dataset_full,
        "pipeline_read": builder.add_pipeline_read,
        "pipeline_write": builder.add_pipeline_write,
        "pipeline_full": builder.add_pipeline_full,
        "role_management": builder.add_role_management,
        "account_management": builder.add_account_management,
    }

    for permission_name, enabled in kwargs.items():
        if enabled and permission_name in permission_map:
            permission_map[permission_name]()

    return builder.build()
