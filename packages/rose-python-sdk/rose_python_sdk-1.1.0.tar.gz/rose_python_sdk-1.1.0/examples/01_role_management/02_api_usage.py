#!/usr/bin/env python3
"""
API Usage Examples

Examples showing how to create and manage roles using the Rose API.
Requires API access - set ROSE_ACCESS_TOKEN environment variable.
"""

import os
import sys
from rose_sdk import RoseClient
from rose_sdk.models.permission import (
    create_read_only_role, create_data_client_role, create_admin_role,
    create_custom_role, PermissionBuilder, PermissionValidator, Permission
)


def create_simple_roles(client):
    """Create simple roles using the API."""
    print("🔹 CREATING SIMPLE ROLES")
    print("=" * 40)
    
    # Create a read-only role
    try:
        read_only_permissions = create_read_only_role()
        read_only_role = client.roles.create(
            role_name="Read-Only User",
            permission=hex(read_only_permissions.value)
        )
        print(f"✅ Created Read-Only User (ID: {read_only_role.role_id})")
    except Exception as e:
        print(f"❌ Failed to create Read-Only User: {e}")
        return
    
    # Create a data client role
    try:
        data_client_permissions = create_data_client_role()
        data_client_role = client.roles.create(
            role_name="Data Client",
            permission=hex(data_client_permissions.value)
        )
        print(f"✅ Created Data Client (ID: {data_client_role.role_id})")
    except Exception as e:
        print(f"❌ Failed to create Data Client: {e}")
        return
    
    return read_only_role, data_client_role


def create_custom_roles(client):
    """Create custom roles using different methods."""
    print("\n🔹 CREATING CUSTOM ROLES")
    print("=" * 40)
    
    # Method 1: Using create_custom_role()
    try:
        analyst_permissions = create_custom_role(
            record_read=True,
            dataset_read=True,
            pipeline_read=True,
            recommendation=True
        )
        analyst_role = client.roles.create(
            role_name="Business Analyst",
            permission=hex(analyst_permissions.value)
        )
        print(f"✅ Created Business Analyst (ID: {analyst_role.role_id})")
    except Exception as e:
        print(f"❌ Failed to create Business Analyst: {e}")
        analyst_role = None
    
    # Method 2: Using PermissionBuilder
    try:
        engineer_permissions = (PermissionBuilder()
                               .add_record_full()
                               .add_dataset_full()
                               .add_pipeline_read()
                               .build())
        engineer_role = client.roles.create(
            role_name="Data Engineer",
            permission=hex(engineer_permissions.value)
        )
        print(f"✅ Created Data Engineer (ID: {engineer_role.role_id})")
    except Exception as e:
        print(f"❌ Failed to create Data Engineer: {e}")
        engineer_role = None
    
    return analyst_role, engineer_role


def create_role_with_token(client):
    """Create a role and issue a token for it."""
    print("\n🔹 CREATING ROLE WITH TOKEN")
    print("=" * 40)
    
    try:
        # Create a role with token
        api_client_permissions = create_custom_role(
            record_read=True,
            recommendation=True
        )
        
        role_with_token = client.roles.create(
            role_name="API Client",
            permission=hex(api_client_permissions.value),
            with_token=True,
            token_expiration=3600  # 1 hour
        )
        
        print(f"✅ Created API Client with token (ID: {role_with_token.role_id})")
        print(f"   Token: {role_with_token.token[:20]}...")
        print(f"   Expires in: 3600 seconds")
        
        return role_with_token
        
    except Exception as e:
        print(f"❌ Failed to create role with token: {e}")
        return None


def list_and_manage_roles(client):
    """List and manage existing roles."""
    print("\n🔹 ROLE MANAGEMENT")
    print("=" * 40)
    
    try:
        # List all roles
        roles = client.roles.list()
        print(f"📋 Found {len(roles)} roles:")
        
        for role in roles:
            print(f"   - {role.role_name} (ID: {role.role_id})")
            
    except Exception as e:
        print(f"❌ Failed to list roles: {e}")


def demonstrate_permission_validation():
    """Demonstrate permission validation with real roles."""
    print("\n🔹 PERMISSION VALIDATION")
    print("=" * 40)
    
    # Create test permissions
    test_permissions = create_custom_role(
        record_read=True,
        dataset_read=True,
        recommendation=True
    )
    
    print(f"📋 Test Role Permissions: {PermissionValidator.get_permission_names(test_permissions)}")
    
    # Test various capabilities
    capabilities = [
        ("Can read records", PermissionValidator.has_permission(test_permissions, Permission.GET_RECORDS)),
        ("Can create records", PermissionValidator.has_permission(test_permissions, Permission.CREATE_RECORDS)),
        ("Can get recommendations", PermissionValidator.has_permission(test_permissions, Permission.GET_RECOMMENDATIONS)),
        ("Can manage roles", PermissionValidator.has_permission(test_permissions, Permission.LIST_ROLES))
    ]
    
    print("\n🔍 Capability Check:")
    for capability, has_it in capabilities:
        status = "✅" if has_it else "❌"
        print(f"   {status} {capability}")


def main():
    """Run all API examples."""
    print("🚀 Rose Python SDK - API Usage Examples")
    print("=" * 60)
    print("These examples show how to create and manage roles using the Rose API.")
    print()
    
    # Check for API access
    BASE_URL = os.getenv('ROSE_BASE_URL', 'https://admin-test.rose.blendvision.com')
    ACCESS_TOKEN = os.getenv('ROSE_ACCESS_TOKEN')
    
    if not ACCESS_TOKEN:
        print("❌ Please set ROSE_ACCESS_TOKEN environment variable")
        print("   Example: export ROSE_ACCESS_TOKEN='your_token_here'")
        print()
        print("For demonstration purposes, showing permission validation only:")
        demonstrate_permission_validation()
        return
    
    try:
        # Initialize the client
        print(f"Connecting to Rose API at: {BASE_URL}")
        client = RoseClient(
            base_url=BASE_URL,
            access_token=ACCESS_TOKEN
        )
        
        # Run examples
        create_simple_roles(client)
        create_custom_roles(client)
        create_role_with_token(client)
        list_and_manage_roles(client)
        demonstrate_permission_validation()
        
        print("\n🎉 API examples completed successfully!")
        print("\nKey takeaways:")
        print("1. Use predefined roles for common use cases")
        print("2. Use create_custom_role() for simple custom roles")
        print("3. Use PermissionBuilder for complex custom roles")
        print("4. Always validate permissions before creating roles")
        print("5. Use with_token=True to automatically issue tokens")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")
        print()
        print("For demonstration purposes, showing permission validation only:")
        demonstrate_permission_validation()


if __name__ == "__main__":
    main()
