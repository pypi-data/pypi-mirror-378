# Pipeline Management Examples

Simple examples showing how to create, update, and delete recommendation pipelines using the Rose Python SDK.

## Quick Start

1. **Set up your environment:**
   ```bash
   export ROSE_ACCESS_TOKEN='your_token_here'
   export ROSE_BASE_URL='https://admin-test.rose.blendvision.com'  # Optional
   ```

2. **Run the examples:**
   ```bash
   # Create a pipeline
   python 01_create_pipeline.py

   # Update a pipeline  
   python 02_update_pipeline.py

   # Delete a pipeline
   python 04_delete_pipeline.py

   # List pipeline queries
   python 05_list_queries.py
   ```

## Examples Overview

### 01_create_pipeline.py
**Create a recommendation pipeline**
- Simple pipeline creation with dataset mapping
- Shows how to use the SDK for basic pipeline setup

### 02_update_pipeline.py
**Update pipeline properties**
- Update existing pipeline properties
- Monitor update progress
- Handle different types of updates

### 04_delete_pipeline.py
**Delete a pipeline**
- Simple pipeline deletion demo
- Verify deletion was successful

### 05_list_queries.py
**List pipeline queries**
- List queries from successful pipelines
- Only works for "CREATE SUCCESSFUL" status
- Shows query details and information

## Core SDK Usage

### 1. Initialize the Client
```python
from rose_sdk import RoseClient

client = RoseClient(
    base_url='https://admin-test.rose.blendvision.com',
    access_token='your_token_here'
)
```

### 2. Create a Pipeline
```python
from rose_sdk.utils import create_pipeline

# Create pipeline with dataset mapping
pipeline_config = create_pipeline(
    account_id="user123",
    pipeline_name="my_pipeline",
    scenario="realtime_leaderboard",
    dataset_mapping={
        "interaction": "your_interaction_dataset_id",
        "metadata": "your_metadata_dataset_id"
    }
)

# Create via API
response = client.pipelines.create(
    name=pipeline_config["pipeline_name"],
    properties=pipeline_config["properties"]
)
```

### 3. List Pipelines
```python
# Get all pipelines
pipelines = client.pipelines.list()

for pipeline in pipelines:
    print(f"Name: {pipeline.pipeline_name}")
    print(f"Status: {pipeline.status}")
    print(f"Scenario: {pipeline.properties.get('scenario')}")
```

### 4. Update a Pipeline
```python
# Update pipeline properties
client.pipelines.update(
    pipeline_id="your_pipeline_id",
    properties={
        "new_property": "new_value",
        "updated_config": {"batch_size": 1000}
    }
)

# Monitor update progress
pipeline = client.pipelines.get(pipeline_id)
print(f"Status: {pipeline.status}")
```

### 5. Delete a Pipeline
```python
# Delete a pipeline
client.pipelines.delete("your_pipeline_id")

# Verify deletion
try:
    pipeline = client.pipelines.get("your_pipeline_id")
    print("Pipeline still exists")
except:
    print("Pipeline deleted successfully")
```

### 6. List Pipeline Queries
```python
# List queries (only works for "CREATE SUCCESSFUL" pipelines)
queries = client.pipelines.list_queries(pipeline_id)

for query in queries:
    print(f"Query: {query.query_name}")
    print(f"Type: {query.query_type}")
    print(f"Status: {query.status}")
```

## Understanding Dataset Mapping

Pipelines require specific dataset keys, but you can use your own dataset names:

```python
# Your datasets
my_datasets = {
    "user_interactions": "abc123",  # Your dataset name → System ID
    "item_catalog": "def456"        # Your dataset name → System ID
}

# Pipeline scenario needs
pipeline_keys = ["interaction", "metadata"]

# Mapping
dataset_mapping = {
    "interaction": "abc123",  # Pipeline key → Your dataset ID
    "metadata": "def456"      # Pipeline key → Your dataset ID
}
```

## Supported Scenarios

| Scenario | Required Dataset Keys | Description |
|----------|----------------------|-------------|
| `realtime_leaderboard` | `interaction`, `metadata` | Real-time item ranking and user favorites |
| `telasa` | `interaction-log`, `item-metadata` | Personalized and hybrid recommendations |

## Common Patterns

### Create and Monitor Pipeline
```python
# Create pipeline
response = client.pipelines.create(name="my_pipeline", properties=config)

# Monitor creation
pipeline_id = response.pipeline_id
while True:
    pipeline = client.pipelines.get(pipeline_id)
    if pipeline.status in ["CREATE SUCCESSFUL", "UPDATE SUCCESSFUL"]:
        print("Pipeline ready!")
        break
    elif pipeline.status in ["CREATE FAILED", "UPDATE FAILED"]:
        print("Pipeline failed!")
        break
    time.sleep(5)
```

### Working with Multiple Pipelines
```python
# List all pipelines
pipelines = client.pipelines.list()

# Process each pipeline
for pipeline in pipelines:
    print(f"Pipeline: {pipeline.pipeline_name}")
    print(f"Status: {pipeline.status}")
    
    # Update if needed
    if pipeline.status == "waiting":
        client.pipelines.update(pipeline.pipeline_id, {"processed": True})
```

## Error Handling

```python
try:
    pipeline = client.pipelines.get("invalid_id")
except Exception as e:
    if "not found" in str(e).lower():
        print("Pipeline does not exist")
    else:
        print(f"Error: {e}")

try:
    client.pipelines.create(name="test", properties={})
except Exception as e:
    print(f"Creation failed: {e}")
```

## Best Practices

1. **Always check pipeline status** after creation/updates
2. **Use descriptive pipeline names** that indicate purpose
3. **Map datasets correctly** - check required keys for each scenario
4. **Handle errors gracefully** - pipelines can fail during processing
5. **Monitor progress** - operations are asynchronous
6. **Clean up unused pipelines** - delete old or test pipelines

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Pipeline stuck in "waiting" | Check Lambda logs, may be backend issue |
| Dataset mapping error | Verify dataset IDs exist and are accessible |
| Update not working | Known issue - check backend Lambda code |
| Pipeline not found | Verify pipeline ID is correct |

### Getting Help

- Check pipeline status in Rose dashboard
- Verify your datasets exist and have correct schema
- Ensure you have required permissions
- Check server logs for detailed error messages
