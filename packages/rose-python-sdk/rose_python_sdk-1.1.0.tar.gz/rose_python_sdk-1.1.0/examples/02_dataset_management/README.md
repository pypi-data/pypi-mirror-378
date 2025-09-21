# Dataset Management Examples

Simple, focused examples for managing datasets in the Rose Python SDK.

## 📁 Examples Overview

### 1. `01_basic_datasets.py` - Basic Dataset Concepts
**Perfect for beginners** - Learn the core concepts without API access.

```bash
python examples/dataset_management/01_basic_datasets.py
```

**What you'll learn:**
- How to design dataset schemas
- Common field types and properties
- Schema patterns for different use cases
- Data validation concepts

### 2. `02_api_usage.py` - Dataset Management API
**Real API integration** - Create and manage actual datasets using predefined schemas.

```bash
export ROSE_ACCESS_TOKEN='your_token_here'
python examples/dataset_management/02_api_usage.py
```

**What you'll learn:**
- How to create datasets via API using predefined schemas
- How to create interaction and metadata datasets
- How to list and manage datasets
- Error handling

## 🚀 Quick Start

### Step 1: Learn the Basics (No API Required)
```bash
python examples/dataset_management/01_basic_datasets.py
```

### Step 2: Try API Integration (Requires Token)
```bash
export ROSE_ACCESS_TOKEN='your_token_here'
python examples/dataset_management/02_api_usage.py
```

## 🔧 Core Dataset Management Operations

### Dataset Creation
```python
from rose_sdk import RoseClient

client = RoseClient(
    base_url='https://your-api-server.com',
    access_token='your_token'
)

# Create a dataset with predefined schema
interaction_schema = {
    "user_id": {
        "field_type": "str",
        "is_identifier": True,
        "is_required": True
    },
    "item_id": {
        "field_type": "str", 
        "is_identifier": True,
        "is_required": True
    },
    "play_amount_second": {
        "field_type": "int",
        "is_identifier": False,
        "is_required": True
    }
}

response = client.datasets.create(
    name="interaction",
    schema=interaction_schema,
    enable_housekeeping=True
)
```

### Dataset Listing
```python
# List all datasets
datasets = client.datasets.list()
for dataset in datasets:
    print(f"Dataset: {dataset.dataset_name} (ID: {dataset.dataset_id})")
    print(f"Status: {dataset.status}")
    print(f"Housekeeping: {dataset.enable_housekeeping}")
```

### Dataset Information
```python
# Get specific dataset details
dataset = client.datasets.get(dataset_id="your_dataset_id")
print(f"Schema type: {type(dataset.schema)}")
print(f"Account ID: {dataset.account_id}")
```

## 📊 Predefined Dataset Schemas

### Interaction Dataset
**Purpose:** User interaction tracking for recommendation systems

**Schema Fields:**
- `user_id` (str, identifier, required) - Unique user identifier
- `item_id` (str, identifier, required) - Content item identifier  
- `item_type` (str, identifier, required) - Type of content item
- `play_amount_second` (int, required) - Duration of interaction
- `interaction` (str, required) - Type of interaction (play, pause, etc.)
- `client_upload_timestamp` (int, identifier, required) - Client-side timestamp
- `server_upload_timestamp` (int, required) - Server-side timestamp

### Metadata Dataset
**Purpose:** Content metadata storage for media items

**Schema Fields:**
- `item_id` (str, identifier, required) - Unique item identifier
- `item_type` (str, identifier, required) - Type of content
- `content_rating` (str, required) - Age/content rating
- `name` (str, required) - Display name
- `description` (str, required) - Item description
- `expire_timestamp` (int, optional) - Expiration time
- `publish_timestamp` (int, optional) - Publication time
- `artists` (list<str>, required) - List of artists
- `genres` (list<str>, required) - List of genres

## 🎯 Field Types and Properties

### String Fields
```python
{
    "field_name": {
        "field_type": "str",
        "is_identifier": True,
        "is_required": True
    }
}
```

### Integer Fields
```python
{
    "field_name": {
        "field_type": "int", 
        "is_identifier": False,
        "is_required": True
    }
}
```

### List Fields
```python
{
    "field_name": {
        "field_type": "list",
        "list_props": {
            "children": {"field_type": "str"}
        },
        "is_identifier": False,
        "is_required": True
    }
}
```

## 🔍 Dataset Management Best Practices

### Schema Design
- **Use meaningful field names** that clearly describe the data
- **Set appropriate identifiers** for unique record identification
- **Mark required fields** to ensure data completeness
- **Choose correct field types** for data validation

### Dataset Naming
- **Use descriptive names** that indicate the dataset purpose
- **Follow consistent naming conventions** across your project
- **Avoid special characters** in dataset names

### Housekeeping
- **Enable housekeeping** for automatic data management
- **Monitor dataset health** regularly
- **Clean up unused datasets** to save resources

## 🛠️ Setup

### Environment Variables
```bash
export ROSE_ACCESS_TOKEN='your_access_token'
export ROSE_BASE_URL='https://your-api-server.com'
```

### Installation
```bash
pip install -e .
```

## 📚 API Reference

### Dataset Service Methods
- `client.datasets.create(name, schema, enable_housekeeping)` - Create dataset
- `client.datasets.list()` - List all datasets
- `client.datasets.get(dataset_id)` - Get dataset details
- `client.datasets.delete(dataset_id)` - Delete dataset

### Schema Structure
```python
{
    "field_name": {
        "field_type": "str|int|list|map",
        "is_identifier": bool,
        "is_required": bool,
        "list_props": {  # For list fields
            "children": {"field_type": "str"}
        }
    }
}
```

## 🚨 Error Handling

### Common Errors
- **DATA_CONFLICT** - Dataset name already exists
- **INVALID_SCHEMA** - Schema format is incorrect
- **PERMISSION_DENIED** - Insufficient permissions
- **NOT_FOUND** - Dataset doesn't exist

### Error Handling Example
```python
try:
    response = client.datasets.create(name="my_dataset", schema=schema)
    print(f"Dataset created: {response.dataset_id}")
except RoseConflictError:
    print("Dataset already exists")
except RoseAPIError as e:
    print(f"API error: {e}")
```

## 📝 Example Progression

1. **Start with `01_basic_datasets.py`** - Learn the concepts
2. **Try `02_api_usage.py`** - Practice with real API
3. **Build your own** - Use these patterns in your applications

Each example builds on the previous one, so run them in order for the best learning experience!

## 💡 Key Takeaways

### Dataset Creation
- Design schemas carefully with proper field types
- Use meaningful dataset and field names
- Enable housekeeping for automatic data management
- Handle errors gracefully

### Schema Design
- Use appropriate field types for your data
- Set identifiers for unique record identification
- Mark required fields to ensure data completeness
- Consider future requirements when designing schemas

### Management
- Monitor dataset health regularly
- Use consistent naming conventions
- Clean up unused datasets
- Document your schema designs
