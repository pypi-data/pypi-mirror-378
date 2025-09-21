#!/usr/bin/env python3
"""
Basic Permission Examples

Simple examples showing how to work with permissions and create basic roles.
No API access required - these examples demonstrate the permission system concepts.
"""

from rose_sdk.models.permission import (
    create_read_only_role, create_data_client_role, create_admin_role,
    create_custom_role, PermissionBuilder, PermissionValidator, Permission
)


def show_predefined_roles():
    """Show how to use predefined roles."""
    print("🔹 PREDEFINED ROLES")
    print("=" * 40)
    
    # Create predefined roles
    roles = {
        "Read-Only": create_read_only_role(),
        "Data Client": create_data_client_role(), 
        "Admin": create_admin_role()
    }
    
    for name, permissions in roles.items():
        print(f"\n📋 {name}")
        print(f"   Permission value: {permissions}")
        print(f"   Permission count: {bin(permissions.value).count('1')}")
        print(f"   Is admin: {PermissionValidator.is_admin_role(permissions)}")
        print(f"   Is read-only: {PermissionValidator.is_read_only(permissions)}")


def show_custom_roles():
    """Show how to create custom roles."""
    print("\n🔹 CUSTOM ROLES")
    print("=" * 40)
    
    # Method 1: Using create_custom_role()
    print("\n📋 Method 1: Using create_custom_role()")
    analyst_role = create_custom_role(
        record_read=True,
        dataset_read=True,
        pipeline_read=True,
        recommendation=True
    )
    print(f"   Analyst Role: {PermissionValidator.get_permission_names(analyst_role)}")
    
    # Method 2: Using PermissionBuilder
    print("\n📋 Method 2: Using PermissionBuilder")
    engineer_role = (PermissionBuilder()
                    .add_record_full()
                    .add_dataset_full()
                    .add_pipeline_read()
                    .build())
    print(f"   Engineer Role: {PermissionValidator.get_permission_names(engineer_role)}")


def show_permission_validation():
    """Show how to validate permissions."""
    print("\n🔹 PERMISSION VALIDATION")
    print("=" * 40)
    
    # Create a test role
    test_role = create_custom_role(
        record_read=True,
        dataset_read=True,
        recommendation=True
    )
    
    print(f"📋 Test Role: {PermissionValidator.get_permission_names(test_role)}")
    
    # Test specific permissions
    tests = [
        ("Can read records", Permission.GET_RECORDS),
        ("Can create records", Permission.CREATE_RECORDS),
        ("Can get recommendations", Permission.GET_RECOMMENDATIONS),
        ("Can manage roles", Permission.LIST_ROLES)
    ]
    
    print("\n🔍 Permission Checks:")
    for test_name, required_permission in tests:
        has_permission = PermissionValidator.has_permission(test_role, required_permission)
        status = "✅" if has_permission else "❌"
        print(f"   {status} {test_name}")


def show_common_use_cases():
    """Show common role use cases."""
    print("\n🔹 COMMON USE CASES")
    print("=" * 40)
    
    # E-commerce roles
    print("\n📋 E-commerce System Roles:")
    
    customer_role = create_custom_role(recommendation=True)
    print(f"   Customer: {PermissionValidator.get_permission_names(customer_role)}")
    
    data_ingestion_role = create_custom_role(
        record_full=True,
        batch_full=True
    )
    print(f"   Data Ingestion: {PermissionValidator.get_permission_names(data_ingestion_role)}")
    
    analytics_role = create_custom_role(
        record_read=True,
        dataset_read=True,
        pipeline_read=True,
        recommendation=True
    )
    print(f"   Analytics: {PermissionValidator.get_permission_names(analytics_role)}")


def main():
    """Run all basic examples."""
    print("🚀 Rose Python SDK - Basic Permission Examples")
    print("=" * 60)
    print("These examples show the core permission system concepts.")
    print("No API access required - just run and learn!")
    print()
    
    show_predefined_roles()
    show_custom_roles()
    show_permission_validation()
    show_common_use_cases()
    
    print("\n🎉 Basic examples completed!")
    print("\nNext steps:")
    print("1. Try the API examples to create real roles")
    print("2. Experiment with different permission combinations")
    print("3. Use these patterns in your own applications")


if __name__ == "__main__":
    main()
