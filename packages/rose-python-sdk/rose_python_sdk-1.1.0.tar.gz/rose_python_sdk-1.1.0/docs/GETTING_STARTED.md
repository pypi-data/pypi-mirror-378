# Getting Started with Rose Python SDK

This guide will help you get up and running with the Rose Python SDK quickly.

## Prerequisites

- Python 3.11 or higher
- Access to a Rose Recommendation Service instance
- Valid API credentials

## Installation

Install the SDK using pip:

```bash
pip install rose-python-sdk
```

## Basic Setup

### 1. Import the SDK

```python
from rose_sdk import RoseClient
```

### 2. Initialize the Client

```python
# Basic initialization
client = RoseClient(
    base_url="https://admin.rose.blendvision.com",
    access_token="your_access_token_here"
)
```

### 3. Test the Connection

```python
# Test the connection by listing datasets
try:
    datasets = client.datasets.list()
    print(f"Connected successfully! Found {len(datasets)} datasets.")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Your First Dataset

### Create a Simple Dataset

```python
from rose_sdk import quick_create_dataset_with_data

# Sample data
sample_records = [
    {"user_id": "user1", "item_id": "item1", "rating": 4.5},
    {"user_id": "user1", "item_id": "item2", "rating": 3.0},
    {"user_id": "user2", "item_id": "item1", "rating": 5.0},
    {"user_id": "user2", "item_id": "item3", "rating": 4.0}
]

# Create dataset with data
dataset_id = quick_create_dataset_with_data(
    client=client,
    name="user_ratings",
    records=sample_records,
    identifier_fields=["user_id", "item_id"],
    required_fields=["rating"]
)

print(f"Created dataset: {dataset_id}")
```

### Verify the Dataset

```python
# Get dataset information
dataset = client.datasets.get(dataset_id)
print(f"Dataset: {dataset.dataset_name}")
print(f"Status: {dataset.status}")
print(f"Schema: {dataset.schema}")
```

## Your First Pipeline

### Create a Recommendation Pipeline

```python
from rose_sdk.utils import create_pipeline

# Create a pipeline
pipeline_response = create_pipeline(
    client=client,
    account_id="your_account_id",
    pipeline_name="my_recommendation_pipeline",
    scenario="realtime_leaderboard",
    dataset_mapping={
        "interaction": dataset_id,  # Your dataset ID
        "metadata": "your_metadata_dataset_id"  # Optional metadata dataset
    }
)

print(f"Created pipeline: {pipeline_response.pipeline_id}")
```

### Monitor Pipeline Status

```python
import time

# Check pipeline status
pipeline = client.pipelines.get(pipeline_response.pipeline_id)
print(f"Pipeline status: {pipeline.status}")

# Wait for pipeline to be ready
while pipeline.status not in ["CREATE SUCCESSFUL", "CREATE FAILED"]:
    time.sleep(10)
    pipeline = client.pipelines.get(pipeline_response.pipeline_id)
    print(f"Pipeline status: {pipeline.status}")

if pipeline.status == "CREATE SUCCESSFUL":
    print("Pipeline is ready!")
else:
    print("Pipeline creation failed!")
```

## Your First Recommendation

### Get Pipeline Queries

```python
# List available queries
queries = client.pipelines.list_queries(pipeline_response.pipeline_id)
print(f"Available queries: {len(queries)}")

for query in queries:
    print(f"Query: {query.query_name} (ID: {query.query_id})")
```

### Get Recommendations

```python
# Get recommendations for a user
if queries:
    query_id = queries[0].query_id
    
    recommendations = client.recommendations.get(
        query_id=query_id,
        parameters={"user_id": "user1"}
    )
    
    print(f"Recommendations: {recommendations.data}")
```

## Next Steps

Now that you have the basics working, explore these areas:

1. **Dataset Management**: Learn about advanced dataset operations
2. **Schema Management**: Understand how to work with complex schemas
3. **Batch Operations**: Handle large datasets efficiently
4. **Role Management**: Set up proper access controls
5. **Pipeline Management**: Create and manage complex pipelines

## Common Issues

### Authentication Errors

```python
# Make sure your access token is valid
try:
    client.datasets.list()
except RoseAuthenticationError:
    print("Invalid access token. Please check your credentials.")
```

### Dataset Creation Errors

```python
# Ensure your data format is correct
try:
    dataset_id = quick_create_dataset_with_data(client, "test", records)
except RoseValidationError as e:
    print(f"Data validation error: {e}")
```

### Pipeline Creation Errors

```python
# Check that all required datasets are mapped
try:
    pipeline = create_pipeline(client, account_id, name, scenario, dataset_mapping)
except RoseValidationError as e:
    print(f"Pipeline validation error: {e}")
```

## Getting Help

- Check the [API Reference](API_REFERENCE.md) for detailed documentation
- Look at the [examples](../examples/) directory for complete examples
- Create an issue on GitHub for bugs or feature requests
- Contact support at luli245683@gmail.com

## Environment Variables

For production use, consider using environment variables:

```bash
export ROSE_BASE_URL="https://admin.rose.blendvision.com"
export ROSE_ACCESS_TOKEN="your_access_token"
```

```python
import os
from rose_sdk import RoseClient

client = RoseClient(
    base_url=os.getenv('ROSE_BASE_URL'),
    access_token=os.getenv('ROSE_ACCESS_TOKEN')
)
```
