# Rose Python SDK Documentation

Welcome to the comprehensive documentation for the Rose Python SDK. This documentation will help you understand and use the SDK effectively.

## 📚 Documentation Structure

### Getting Started
- **[Getting Started Guide](GETTING_STARTED.md)** - Quick start guide for new users
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Examples Guide](EXAMPLES.md)** - Comprehensive examples and use cases

### Quick Links
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Core Concepts](#core-concepts)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## 🚀 Installation

```bash
pip install rose-python-sdk
```

## 🏃‍♂️ Basic Usage

### Initialize the Client

```python
from rose_sdk import RoseClient

client = RoseClient(
    base_url="https://admin.rose.blendvision.com",
    access_token="your_access_token"
)
```

### Create a Dataset

```python
from rose_sdk import quick_create_dataset_with_data

dataset_id = quick_create_dataset_with_data(
    client=client,
    name="user_ratings",
    records=[
        {"user_id": "user1", "item_id": "item1", "rating": 4.5},
        {"user_id": "user1", "item_id": "item2", "rating": 3.0}
    ],
    identifier_fields=["user_id", "item_id"],
    required_fields=["rating"]
)
```

### Create a Pipeline

```python
from rose_sdk.utils import create_pipeline

pipeline_response = create_pipeline(
    client=client,
    account_id="your_account",
    pipeline_name="recommendation_pipeline",
    scenario="realtime_leaderboard",
    dataset_mapping={"interaction": dataset_id}
)
```

### Get Recommendations

```python
recommendations = client.recommendations.get(
    query_id="your_query_id",
    parameters={"user_id": "user1"}
)
```

## 🧠 Core Concepts

### 1. Datasets
Datasets store your data and define its structure through schemas. They support:
- **Schema Definition**: Define field types, identifiers, and requirements
- **Data Ingestion**: Add, update, and delete records
- **Batch Operations**: Efficient handling of large datasets
- **Schema Validation**: Ensure data integrity

### 2. Pipelines
Pipelines process your data to generate recommendations. They include:
- **Scenario-based Configuration**: Pre-defined pipeline types
- **Dataset Mapping**: Connect your datasets to pipeline requirements
- **Query Management**: Access recommendation queries
- **Status Monitoring**: Track pipeline creation and updates

### 3. Roles and Permissions
Control access to your resources through:
- **Permission System**: Granular access control
- **Predefined Roles**: Common role templates
- **Token Management**: Issue and manage access tokens
- **Role-based Access**: Secure API access

### 4. Recommendations
Get personalized recommendations through:
- **Query Execution**: Run recommendation queries
- **Batch Processing**: Handle multiple users efficiently
- **Parameter Passing**: Customize recommendation logic
- **Result Processing**: Work with recommendation data

## 📖 Examples

### Role Management
```python
from rose_sdk import Permission, PredefinedRoles

# Create role with specific permissions
role = client.roles.create(
    name="Data Analyst",
    permissions=[Permission.DATASET_READ, Permission.DATASET_WRITE]
)

# Use predefined role
role = client.roles.create(
    name="Admin",
    permissions=PredefinedRoles.ADMIN.permissions
)
```

### Dataset Management
```python
# Create dataset with schema
dataset = client.datasets.create(
    name="user_ratings",
    schema={
        "user_id": {"field_type": "str", "is_identifier": True},
        "rating": {"field_type": "float", "is_required": True}
    }
)

# Add records
client.datasets.records.create(dataset.dataset_id, records)
```

### Pipeline Management
```python
# Create pipeline
pipeline = client.pipelines.create(
    name="recommendation_pipeline",
    properties={
        "scenario": "realtime_leaderboard",
        "datasets": {"interaction": dataset_id}
    }
)

# Monitor status
while pipeline.status not in ["CREATE SUCCESSFUL", "CREATE FAILED"]:
    time.sleep(10)
    pipeline = client.pipelines.get(pipeline.pipeline_id)
```

### Batch Operations
```python
from rose_sdk import quick_batch_upload

# Upload large dataset
quick_batch_upload(
    client=client,
    dataset_id=dataset_id,
    records=large_records,
    mode="append"
)
```

## 🔧 Advanced Features

### Schema Validation
```python
from rose_sdk.utils import validate_and_align_records

# Validate records against schema
validated_records = validate_and_align_records(
    dataset_id=dataset_id,
    records=records,
    client=client
)
```

### Pipeline Building
```python
from rose_sdk.utils import PipelineBuilder

# Build complex pipeline
pipeline_config = (PipelineBuilder("account", "name", "scenario")
    .add_dataset("interaction", dataset_id)
    .set_custom_property("setting", "value")
    .build())
```

### Error Handling
```python
from rose_sdk import RoseAPIError, RoseNotFoundError

try:
    dataset = client.datasets.get("invalid_id")
except RoseNotFoundError:
    print("Dataset not found")
except RoseAPIError as e:
    print(f"API error: {e}")
```

## 🛠️ Troubleshooting

### Common Issues

#### Authentication Errors
```python
# Check your access token
try:
    client.datasets.list()
except RoseAuthenticationError:
    print("Invalid access token")
```

#### Dataset Creation Errors
```python
# Validate your data format
try:
    dataset = client.datasets.create(name, schema)
except RoseValidationError as e:
    print(f"Validation error: {e}")
```

#### Pipeline Creation Errors
```python
# Check dataset mapping
try:
    pipeline = create_pipeline(client, account, name, scenario, mapping)
except RoseValidationError as e:
    print(f"Pipeline validation error: {e}")
```

### Debug Mode
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

- **GitHub Issues**: [Create an issue](https://github.com/your-org/rose-python-sdk/issues)
- **Email Support**: luli245683@gmail.com
- **API Documentation**: [Rose API Docs](https://raas.kkstream.tech/doc/rose/v1.1/)

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/rose-python-sdk/)
- [GitHub Repository](https://github.com/your-org/rose-python-sdk)
- [API Documentation](https://raas.kkstream.tech/doc/rose/v1.1/)

---

**Need help?** Check out the [Getting Started Guide](GETTING_STARTED.md) or browse the [Examples](EXAMPLES.md) for more detailed information.
