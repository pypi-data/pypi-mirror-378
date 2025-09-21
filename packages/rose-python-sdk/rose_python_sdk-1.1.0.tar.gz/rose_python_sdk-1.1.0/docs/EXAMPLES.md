# Examples Guide

This guide provides comprehensive examples for using the Rose Python SDK.

## Table of Contents

1. [Role Management](#role-management)
2. [Dataset Management](#dataset-management)
3. [Records Management](#records-management)
4. [Batch Data Management](#batch-data-management)
5. [Pipeline Management](#pipeline-management)
6. [Advanced Usage](#advanced-usage)

## Role Management

### Basic Permission Setup

```python
from rose_sdk import RoseClient, Permission, PermissionBuilder, PredefinedRoles

# Initialize client
client = RoseClient(
    base_url="https://admin.rose.blendvision.com",
    access_token="your_token"
)

# Create a role with specific permissions
role = client.roles.create(
    name="Data Analyst",
    permissions=[
        Permission.DATASET_READ,
        Permission.DATASET_WRITE,
        Permission.RECOMMENDATION_READ
    ]
)

print(f"Created role: {role.role_id}")
```

### Using Predefined Roles

```python
# Use predefined role templates
role = client.roles.create(
    name="Admin",
    permissions=PredefinedRoles.ADMIN.permissions
)

# Issue token for the role
token_response = client.roles.issue_token(
    role_id=role.role_id,
    expiration=3600  # 1 hour
)

print(f"Access token: {token_response.token}")
```

### Advanced Permission Building

```python
# Build complex permissions using the builder
permissions = (PermissionBuilder()
    .add_permission(Permission.DATASET_READ)
    .add_permission(Permission.DATASET_WRITE)
    .add_permission(Permission.PIPELINE_READ)
    .add_permission(Permission.RECOMMENDATION_READ)
    .build())

role = client.roles.create(
    name="Power User",
    permissions=permissions
)
```

## Dataset Management

### Create Dataset with Schema

```python
from rose_sdk import RoseClient, FieldType

# Define schema
schema = {
    "user_id": {
        "field_type": FieldType.STRING,
        "is_identifier": True,
        "is_required": True
    },
    "item_id": {
        "field_type": FieldType.STRING,
        "is_identifier": True,
        "is_required": True
    },
    "rating": {
        "field_type": FieldType.FLOAT,
        "is_required": True
    },
    "timestamp": {
        "field_type": FieldType.TIMESTAMP,
        "is_required": False
    }
}

# Create dataset
dataset = client.datasets.create(
    name="user_ratings",
    schema=schema,
    enable_housekeeping=True
)

print(f"Created dataset: {dataset.dataset_id}")
```

### Quick Dataset Creation

```python
from rose_sdk import quick_create_dataset_with_data

# Sample data
sample_data = [
    {"user_id": "user1", "item_id": "item1", "rating": 4.5, "timestamp": "2024-01-01T10:00:00Z"},
    {"user_id": "user1", "item_id": "item2", "rating": 3.0, "timestamp": "2024-01-01T11:00:00Z"},
    {"user_id": "user2", "item_id": "item1", "rating": 5.0, "timestamp": "2024-01-01T12:00:00Z"}
]

# Create dataset with data
dataset_id = quick_create_dataset_with_data(
    client=client,
    name="user_ratings",
    records=sample_data,
    identifier_fields=["user_id", "item_id"],
    required_fields=["rating"]
)
```

### Schema Validation

```python
from rose_sdk.utils import validate_and_align_records

# Validate records against existing dataset schema
validated_records = validate_and_align_records(
    dataset_id=dataset_id,
    records=new_records,
    client=client
)

# Add validated records
client.datasets.records.create(dataset_id, validated_records)
```

## Records Management

### Add Records

```python
# Prepare records in Rose format
records = [
    {
        "user_id": {"str": "user1"},
        "item_id": {"str": "item1"},
        "rating": {"float": 4.5},
        "timestamp": {"str": "2024-01-01T10:00:00Z"}
    },
    {
        "user_id": {"str": "user2"},
        "item_id": {"str": "item2"},
        "rating": {"float": 3.0},
        "timestamp": {"str": "2024-01-01T11:00:00Z"}
    }
]

# Add records to dataset
client.datasets.records.create(dataset_id, records)
```

### Update Records

```python
# Update existing records
updated_records = [
    {
        "user_id": {"str": "user1"},
        "item_id": {"str": "item1"},
        "rating": {"float": 5.0}  # Updated rating
    }
]

client.datasets.records.update(dataset_id, updated_records)
```

### Delete Records

```python
# Delete specific records
records_to_delete = [
    {
        "user_id": {"str": "user1"},
        "item_id": {"str": "item1"}
    }
]

client.datasets.records.delete(dataset_id, records_to_delete)
```

## Batch Data Management

### Batch Append

```python
from rose_sdk import quick_batch_upload

# Large dataset
large_records = [
    {"user_id": f"user{i}", "item_id": f"item{j}", "rating": 4.0}
    for i in range(1000)
    for j in range(10)
]

# Upload in batch
quick_batch_upload(
    client=client,
    dataset_id=dataset_id,
    records=large_records,
    mode="append"
)
```

### Batch Overwrite

```python
# Start batch upload
batch_id = client.datasets.batch.start_upload(dataset_id)

# Upload data
client.datasets.batch.upload_batch(dataset_id, batch_id, large_records)

# Complete upload
client.datasets.batch.complete_upload(dataset_id, batch_id)
```

## Pipeline Management

### Create Simple Pipeline

```python
from rose_sdk.utils import create_pipeline

# Create pipeline with dataset mapping
pipeline_response = create_pipeline(
    client=client,
    account_id="your_account",
    pipeline_name="recommendation_pipeline",
    scenario="realtime_leaderboard",
    dataset_mapping={
        "interaction": dataset_id,
        "metadata": metadata_dataset_id
    }
)

print(f"Created pipeline: {pipeline_response.pipeline_id}")
```

### Advanced Pipeline Building

```python
from rose_sdk.utils import PipelineBuilder

# Build complex pipeline configuration
pipeline_config = (PipelineBuilder("account", "pipeline_name", "realtime_leaderboard")
    .add_dataset("interaction", dataset_id)
    .add_dataset("metadata", metadata_dataset_id)
    .set_custom_property("custom_setting", "value")
    .build())

# Create pipeline
pipeline_response = client.pipelines.create(
    name="advanced_pipeline",
    properties=pipeline_config
)
```

### Monitor Pipeline Status

```python
import time

# Check pipeline status
pipeline = client.pipelines.get(pipeline_response.pipeline_id)

while pipeline.status not in ["CREATE SUCCESSFUL", "CREATE FAILED"]:
    time.sleep(10)
    pipeline = client.pipelines.get(pipeline_response.pipeline_id)
    print(f"Pipeline status: {pipeline.status}")

if pipeline.status == "CREATE SUCCESSFUL":
    print("Pipeline is ready!")
    
    # List available queries
    queries = client.pipelines.list_queries(pipeline_response.pipeline_id)
    for query in queries:
        print(f"Query: {query.query_name} (ID: {query.query_id})")
```

### Update Pipeline

```python
# Update pipeline properties
client.pipelines.update(
    pipeline_id=pipeline_response.pipeline_id,
    properties={
        "custom_setting": "new_value",
        "datasets": {
            "interaction": new_dataset_id
        }
    }
)
```

### Delete Pipeline

```python
# Delete pipeline
client.pipelines.delete(pipeline_response.pipeline_id)
```

## Advanced Usage

### Complete Recommendation System Setup

```python
from rose_sdk import quick_setup_recommendation_system

# Set up complete system
dataset_id, pipeline_id, query_ids = quick_setup_recommendation_system(
    client=client,
    dataset_name="user_interactions",
    records=sample_data,
    pipeline_name="recommendation_system",
    pipeline_properties={
        "scenario": "realtime_leaderboard",
        "datasets": {
            "interaction": "placeholder"  # Will be replaced
        }
    },
    identifier_fields=["user_id", "item_id"],
    required_fields=["rating"]
)

print(f"Dataset: {dataset_id}")
print(f"Pipeline: {pipeline_id}")
print(f"Queries: {query_ids}")
```

### Get Recommendations

```python
# Get recommendations for a single user
recommendations = client.recommendations.get(
    query_id=query_ids[0],
    parameters={"user_id": "user1"}
)

print(f"Recommendations: {recommendations.data}")

# Batch recommendations for multiple users
batch_recommendations = client.recommendations.batch_query(
    query_id=query_ids[0],
    parameters_list=[
        {"user_id": "user1"},
        {"user_id": "user2"},
        {"user_id": "user3"}
    ]
)

for rec in batch_recommendations:
    print(f"User {rec.parameters['user_id']}: {rec.data}")
```

### Error Handling

```python
from rose_sdk import (
    RoseAPIError,
    RoseAuthenticationError,
    RoseNotFoundError,
    RoseValidationError
)

try:
    dataset = client.datasets.get("invalid_id")
except RoseNotFoundError:
    print("Dataset not found")
except RoseAuthenticationError:
    print("Authentication failed")
except RoseValidationError as e:
    print(f"Validation error: {e}")
except RoseAPIError as e:
    print(f"API error: {e}")
```

### Working with Large Datasets

```python
from rose_sdk.utils import split_batch_records, estimate_batch_size

# Estimate batch size
size_info = estimate_batch_size(large_records)
print(f"Estimated size: {size_info['total_size_mb']:.2f} MB")

# Split into manageable batches
batches = split_batch_records(large_records, max_batch_size=1000)

for i, batch in enumerate(batches):
    print(f"Uploading batch {i+1}/{len(batches)}")
    quick_batch_upload(client, dataset_id, batch, mode="append")
```

### Schema Management

```python
from rose_sdk.utils import get_schema_summary, print_schema_summary

# Get dataset summary
dataset = client.datasets.get(dataset_id)
summary = get_schema_summary(dataset.schema)

print(f"Schema summary: {summary}")

# Print detailed schema information
print_schema_summary(dataset.schema)
```

## Best Practices

### 1. Use Helper Functions
Prefer helper functions for common operations:

```python
# Good
dataset_id = quick_create_dataset_with_data(client, "name", records)

# Avoid
schema = build_schema_from_sample(records)
dataset = client.datasets.create("name", schema)
client.datasets.records.create(dataset.dataset_id, records)
```

### 2. Handle Errors Gracefully
Always wrap API calls in try-catch blocks:

```python
try:
    result = client.datasets.create(name, schema)
except RoseValidationError as e:
    print(f"Invalid data: {e}")
    # Handle validation error
except RoseAPIError as e:
    print(f"API error: {e}")
    # Handle API error
```

### 3. Use Batch Operations for Large Data
For large datasets, use batch operations:

```python
# For large datasets
quick_batch_upload(client, dataset_id, large_records, mode="append")

# For small datasets
client.datasets.records.create(dataset_id, small_records)
```

### 4. Monitor Pipeline Status
Always monitor pipeline creation:

```python
# Wait for pipeline to be ready
while pipeline.status not in ["CREATE SUCCESSFUL", "CREATE FAILED"]:
    time.sleep(10)
    pipeline = client.pipelines.get(pipeline_id)
```

### 5. Validate Data Before Upload
Use schema validation for data integrity:

```python
# Validate before upload
validated_records = validate_and_align_records(
    dataset_id=dataset_id,
    records=records,
    client=client
)
```
