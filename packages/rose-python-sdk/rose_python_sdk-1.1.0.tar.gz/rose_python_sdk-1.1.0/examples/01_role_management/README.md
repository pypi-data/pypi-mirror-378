# Role Management Examples

Simple examples demonstrating how to create and manage roles using the Rose Python SDK.

## Quick Start

1. **Set up your environment:**
   ```bash
   export ROSE_ACCESS_TOKEN='your_token_here'
   export ROSE_BASE_URL='https://admin-test.rose.blendvision.com'  # Optional
   ```

2. **Run the examples:**
   ```bash
   # Basic concepts (no API required)
   python 01_basic_permissions.py

   # API operations (requires token)
   python 02_api_usage.py
   ```

## Examples Overview

### 01_basic_permissions.py
**Basic permission concepts and role creation**
- Predefined roles (ReadOnlyAdmin, DataClient, Admin)
- Custom role creation
- Permission validation
- No API access required

### 02_api_usage.py
**Complete role management with the Rose API**
- Create roles via API
- Issue access tokens
- List and manage roles
- Error handling

## Core Rose SDK Usage

### 1. Initialize the Client
```python
from rose_sdk import RoseClient

client = RoseClient(
    base_url='https://admin-test.rose.blendvision.com',
    access_token='your_token_here'
)
```

### 2. Create Predefined Roles
```python
from rose_sdk.models.permission import create_read_only_role, create_admin_role

# Use predefined roles
read_only_role = create_read_only_role()
admin_role = create_admin_role()

# Create via API
role = client.roles.create(
    role_name='Read Only User',
    permission=hex(read_only_role.value)
)
```

### 3. Create Custom Roles

#### Method 1: Simple Custom Role
```python
from rose_sdk.models.permission import create_custom_role

# Create custom role with specific permissions
analyst_role = create_custom_role(
    record_read=True,
    dataset_read=True,
    recommendation=True
)

# Create via API
role = client.roles.create(
    role_name='Data Analyst',
    permission=hex(analyst_role.value)
)
```

#### Method 2: Complex Custom Role
```python
from rose_sdk.models.permission import PermissionBuilder

# Build complex role step by step
engineer_role = (PermissionBuilder()
                .add_record_full()
                .add_dataset_full()
                .add_pipeline_read()
                .build())

# Create via API
role = client.roles.create(
    role_name='ML Engineer',
    permission=hex(engineer_role.value)
)
```

### 4. Create Roles with Tokens
```python
# Create role and issue token in one call
role_with_token = client.roles.create(
    role_name='API Client',
    permission=hex(analyst_role.value),
    with_token=True,
    token_expiration=3600  # 1 hour
)

print(f"Role ID: {role_with_token.role_id}")
print(f"Access Token: {role_with_token.token}")
```

### 5. Issue Tokens for Existing Roles
```python
# Issue token for existing role
role_with_token = client.roles.issue_token(
    role_id=role.role_id,
    expiration=3600  # 1 hour
)
```

### 6. Use Tokens
```python
# Create client with the issued token
client_with_token = RoseClient(
    base_url='https://admin-test.rose.blendvision.com',
    access_token=role_with_token.token
)
```

### 7. Role Management Operations

#### List Roles
```python
# Get all roles
roles = client.roles.list()
for role in roles:
    print(f"{role.role_name}: {role.role_id}")
```

#### Update Roles
```python
# Update role permissions
updated_role = client.roles.update(
    role_id=role.role_id,
    permission=hex(new_permissions.value)
)
```

#### Delete Roles
```python
# Delete a role
client.roles.delete(role_id=role.role_id)
```

### 8. Permission Validation
```python
from rose_sdk.models.permission import PermissionValidator, Permission

# Check specific permission
can_read = PermissionValidator.has_permission(
    user_permissions, 
    Permission.GET_RECORDS
)

# Check multiple permissions
required_permissions = [Permission.GET_RECORDS, Permission.LIST_RECORDS]
has_all = PermissionValidator.has_all_permissions(
    user_permissions, 
    required_permissions
)

# Find missing permissions
missing = PermissionValidator.get_missing_permissions(
    user_permissions, 
    required_permissions
)
```

## Common Role Patterns

### E-commerce System
```python
# Customer-facing API
customer_role = create_custom_role(recommendation=True)

# Data ingestion service
ingestion_role = create_custom_role(
    record_full=True,
    batch_full=True
)

# Analytics dashboard
analytics_role = create_custom_role(
    record_read=True,
    dataset_read=True,
    pipeline_read=True,
    recommendation=True
)
```

### ML Pipeline System
```python
# Data scientist
scientist_role = create_custom_role(
    record_read=True,
    dataset_full=True,
    pipeline_full=True,
    batch_read=True,
    recommendation=True
)

# ML engineer
engineer_role = create_custom_role(
    record_full=True,
    dataset_full=True,
    pipeline_full=True,
    batch_full=True
)

# Model serving
serving_role = create_custom_role(
    recommendation=True,
    pipeline_read=True
)
```

## Available Permissions

The Rose SDK supports these permission categories:

- **Record Operations**: `record_read`, `record_write`, `record_full`
- **Dataset Operations**: `dataset_read`, `dataset_write`, `dataset_full`
- **Pipeline Operations**: `pipeline_read`, `pipeline_write`, `pipeline_full`
- **Batch Operations**: `batch_read`, `batch_write`, `batch_full`
- **Recommendation**: `recommendation`
- **Account Management**: `account_read`, `account_write`, `account_full`

## Error Handling

```python
from rose_sdk.exceptions import RoseAPIError

try:
    role = client.roles.create(
        role_name='My Role',
        permission=hex(permissions.value)
    )
    print("✅ Role created successfully")
    
except RoseAPIError as e:
    print(f"❌ Failed to create role: {e.message}")
    print(f"   Status: {e.status_code}")
    if e.details:
        print(f"   Details: {e.details}")
```

## Key Takeaways

1. **Use predefined roles** for common use cases
2. **Create custom roles** for specific requirements
3. **Issue tokens** for API access
4. **Validate permissions** before operations
5. **Handle errors** gracefully with try-catch blocks
6. **Use PermissionBuilder** for complex role creation
7. **Store tokens securely** and respect expiration times
