# Records Management Examples

Simple examples demonstrating how to perform CRUD operations on records using the Rose Python SDK.

## Quick Start

1. **Set up your environment:**
   ```bash
   export ROSE_ACCESS_TOKEN='your_token_here'
   export ROSE_BASE_URL='https://admin-test.rose.blendvision.com'  # Optional
   ```

2. **Run the examples:**
   ```bash
   # Basic concepts (no API required)
   python 01_basic_ingestion.py

   # API operations (requires token)
   python 02_records_management.py

   # Schema validation (requires token)
   python 03_schema_validation.py
   ```

## Examples Overview

### 01_basic_ingestion.py
**Basic record concepts and data preparation**
- Record data models
- Data validation patterns
- Sample record creation
- No API access required

### 02_records_management.py
**Complete CRUD operations with the Rose API**
- **CREATE** - Add new records to datasets
- **READ** - List and retrieve records
- **UPDATE** - Replace entire records
- **PATCH** - Partially update records
- **DELETE** - Remove records from datasets

### 03_schema_validation.py
**Schema validation and data alignment**
- Validate data against dataset schemas
- Align field types and handle type mismatches
- Check for missing required fields
- Convert data to Rose format
- Schema information and summaries

## Core Rose SDK Usage

### 1. Initialize the Client
```python
from rose_sdk import RoseClient

client = RoseClient(
    base_url='https://admin-test.rose.blendvision.com',
    access_token='your_token_here'
)
```

### 2. Data Format Conversion
The Rose server expects data in a specific `{"type": value}` format:

```python
from rose_sdk.utils import convert_records_to_rose_format

# Convert Python records to Rose format
records = [
    {"user_id": "user_001", "play_amount_second": 180},
    {"user_id": "user_002", "play_amount_second": 240}
]

rose_records = convert_records_to_rose_format(records)
# Result: [{"user_id": {"str": "user_001"}, "play_amount_second": {"int": 180}}, ...]
```

### 3. CRUD Operations

#### CREATE Records
```python
# Create new records
client.datasets.records.create(
    dataset_id="your_dataset_id",
    records=rose_records
)
```

#### READ Records
```python
# List records from dataset
records = client.datasets.records.list(
    dataset_id="your_dataset_id",
    size=10  # Optional: limit number of records
)
```

#### UPDATE Records
```python
# Replace entire records
client.datasets.records.update(
    dataset_id="your_dataset_id",
    records=rose_records
)
```

#### PATCH Records
```python
# Partially update records (only specified fields)
client.datasets.records.patch(
    dataset_id="your_dataset_id",
    records=rose_records
)
```

#### DELETE Records
```python
# Remove records from dataset
client.datasets.records.delete(
    dataset_id="your_dataset_id",
    records=rose_records
)
```

### 4. Error Handling

The SDK provides specific exceptions for different error types:

```python
from rose_sdk.exceptions import RoseMultiStatusError, RoseAPIError

try:
    client.datasets.records.create(dataset_id, records)
    print("✅ Records created successfully")
    
except RoseMultiStatusError as e:
    print(f"⚠️  Partial success: {e.message}")
    e.print_errors()  # Show detailed error info
    
except RoseAPIError as e:
    print(f"❌ API Error: {e.message}")
```

## Data Types Supported

The Rose SDK automatically converts Python types to the server format:

| Python Type | Rose Format | Example |
|-------------|-------------|---------|
| `str` | `{"str": "value"}` | `"hello"` → `{"str": "hello"}` |
| `int` | `{"int": value}` | `42` → `{"int": 42}` |
| `float` | `{"float": value}` | `3.14` → `{"float": 3.14}` |
| `bool` | `{"bool": value}` | `True` → `{"bool": true}` |
| `list` | `{"list": [...]}` | `[1, 2]` → `{"list": [{"int": 1}, {"int": 2}]}` |
| `dict` | `{"map": {...}}` | `{"a": 1}` → `{"map": {"a": {"int": 1}}}` |

## Common Patterns

### Working with Existing Records
```python
# Get existing records
existing_records = client.datasets.records.list(dataset_id, size=5)

# Convert to dict for modification
for record in existing_records:
    record_dict = dict(record)
    record_dict["play_amount_second"] = 100  # Update field
    # Use record_dict for PATCH/DELETE operations
```

### Batch Operations
```python
# Process multiple records
records_to_process = []
for record in existing_records:
    record_dict = dict(record)
    record_dict["updated_field"] = "new_value"
    records_to_process.append(record_dict)

# Apply changes
client.datasets.records.update(dataset_id, records_to_process)
```

## Troubleshooting

### Status Code 207 (Multi-Status)
When some records succeed and others fail:

```python
try:
    client.datasets.records.create(dataset_id, records)
except RoseMultiStatusError as e:
    print(f"Partial success: {len(e.get_failed_records())} failed")
    e.print_errors()  # Shows detailed error for each failed record
```

### Common Issues
1. **Schema Mismatch**: Ensure all required fields are present
2. **Data Format**: Use `convert_records_to_rose_format()` for proper conversion
3. **Record Not Found**: Verify record identifiers exist before DELETE operations

## Key Takeaways

1. **Always convert data** using `convert_records_to_rose_format()`
2. **Handle partial failures** with `RoseMultiStatusError`
3. **Use existing records** for PATCH and DELETE operations
4. **Convert Record objects** to dictionaries before modification
5. **Check error details** using `e.print_errors()` for debugging
