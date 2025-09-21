# Batch Data Management Examples

Simple examples demonstrating how to perform batch operations using the Rose Python SDK.

## Quick Start

1. **Set up your environment:**
   ```bash
   export ROSE_ACCESS_TOKEN='your_token_here'
   export ROSE_BASE_URL='https://admin-test.rose.blendvision.com'  # Optional
   ```

2. **Run the examples:**
   ```bash
   # Append records to datasets
   python 01_batch_append.py

   # Overwrite entire datasets
   python 02_batch_overwrite.py
   ```

## Examples Overview

### 01_batch_append.py
**Append records to existing datasets**
- Simple append operations
- Chunked append for large datasets
- Error handling for partial failures

### 02_batch_overwrite.py
**Replace entire dataset content**
- Simple overwrite operations
- Chunked overwrite for large datasets
- Batch process management (start, upload, complete, abort)

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
Convert your data to the Rose server format:

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

### 3. Append Mode (Add Records)

#### Simple Append
```python
# Append records to existing dataset
client.datasets.batch.upload_append(
    dataset_id="your_dataset_id",
    records=rose_records
)
```

#### Chunked Append
```python
def append_in_chunks(client, dataset_id, records, chunk_size=100):
    """Append records in chunks for better error handling."""
    chunks = [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Uploading chunk {i}/{len(chunks)}...")
        
        try:
            rose_records = convert_records_to_rose_format(chunk)
            client.datasets.batch.upload_append(dataset_id, rose_records)
            print(f"✅ Chunk {i} uploaded successfully")
            
        except RoseMultiStatusError as e:
            print(f"⚠️  Chunk {i} partial failure")
            e.print_errors()
        
        # Add delay between chunks
        time.sleep(0.5)
```

### 4. Overwrite Mode (Replace Dataset)

#### Simple Overwrite
```python
# Start batch upload process
batch_id = client.datasets.batch.start_upload(dataset_id)

# Upload batch data
client.datasets.batch.upload_batch(dataset_id, batch_id, rose_records)

# Complete the upload
client.datasets.batch.complete_upload(dataset_id, batch_id)
```

#### Chunked Overwrite
```python
def overwrite_in_chunks(client, dataset_id, records, chunk_size=100):
    """Overwrite dataset by uploading data in chunks."""
    # Start batch upload process
    batch_id = client.datasets.batch.start_upload(dataset_id)
    
    # Split records into chunks
    chunks = [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Uploading chunk {i}/{len(chunks)}...")
        
        try:
            rose_records = convert_records_to_rose_format(chunk)
            client.datasets.batch.upload_batch(dataset_id, batch_id, rose_records)
            print(f"✅ Chunk {i} uploaded successfully")
            
        except RoseMultiStatusError as e:
            print(f"⚠️  Chunk {i} partial failure")
            e.print_errors()
        
        time.sleep(0.5)
    
    # Complete the upload
    client.datasets.batch.complete_upload(dataset_id, batch_id)
```

### 5. Batch Process Management

#### Abort Upload
```python
# Start a batch upload
batch_id = client.datasets.batch.start_upload(dataset_id)

# Abort the upload if needed
client.datasets.batch.abort_upload(dataset_id, batch_id)
```

### 6. Error Handling

```python
from rose_sdk.exceptions import RoseMultiStatusError, RoseAPIError

try:
    client.datasets.batch.upload_append(dataset_id, rose_records)
    print("✅ Records appended successfully")
    
except RoseMultiStatusError as e:
    print(f"⚠️  Partial success: {e.message}")
    e.print_errors()  # Show detailed error info
    
except RoseAPIError as e:
    print(f"❌ API Error: {e.message}")
```

## When to Use Each Mode

### Append Mode
- **Use for**: Adding new records to existing datasets
- **Best for**: Daily data ingestion, real-time updates
- **Example**: Adding today's user interactions to the interaction dataset

```python
# Daily data ingestion
daily_records = get_todays_interactions()
rose_records = convert_records_to_rose_format(daily_records)
client.datasets.batch.upload_append(dataset_id, rose_records)
```

### Overwrite Mode
- **Use for**: Replacing entire dataset content
- **Best for**: Full dataset refresh, data migration
- **Example**: Replacing all user data with updated information

```python
# Full dataset refresh
new_data = get_updated_dataset()
rose_records = convert_records_to_rose_format(new_data)

batch_id = client.datasets.batch.start_upload(dataset_id)
client.datasets.batch.upload_batch(dataset_id, batch_id, rose_records)
client.datasets.batch.complete_upload(dataset_id, batch_id)
```

## Common Patterns

### Daily Data Ingestion
```python
def daily_ingestion(client, dataset_id, daily_records):
    """Ingest daily data using append mode."""
    rose_records = convert_records_to_rose_format(daily_records)
    client.datasets.batch.upload_append(dataset_id, rose_records)
```

### Full Dataset Refresh
```python
def refresh_dataset(client, dataset_id, new_data):
    """Replace entire dataset using overwrite mode."""
    batch_id = client.datasets.batch.start_upload(dataset_id)
    
    # Upload in chunks for large datasets
    chunks = [new_data[i:i + 500] for i in range(0, len(new_data), 500)]
    for chunk in chunks:
        rose_records = convert_records_to_rose_format(chunk)
        client.datasets.batch.upload_batch(dataset_id, batch_id, rose_records)
    
    client.datasets.batch.complete_upload(dataset_id, batch_id)
```

### Robust Upload with Error Handling
```python
def robust_upload(client, dataset_id, records):
    """Upload with comprehensive error handling."""
    try:
        rose_records = convert_records_to_rose_format(records)
        client.datasets.batch.upload_append(dataset_id, rose_records)
        return True
        
    except RoseMultiStatusError as e:
        print("Partial failure occurred")
        e.print_errors()
        return False
        
    except RoseAPIError as e:
        print(f"Upload failed: {e.message}")
        return False
```

## Best Practices

### 1. Data Preparation
- Always validate your data before sending
- Use `convert_records_to_rose_format()` for proper conversion
- Check for required fields and data types

### 2. Chunking Strategy
- Use chunking for datasets larger than 1000 records
- Choose chunk size based on your data and network
- Add delays between chunks to avoid rate limiting

### 3. Error Handling
- Always handle `RoseMultiStatusError` for partial failures
- Implement retry logic for transient failures
- Log errors for debugging and analysis

### 4. Performance
- Monitor memory usage with large datasets
- Use appropriate chunk sizes
- Consider parallel processing for multiple datasets

## Key Takeaways

1. **Use append mode** for adding new records to existing datasets
2. **Use overwrite mode** for replacing entire dataset content
3. **Always convert data** using `convert_records_to_rose_format()`
4. **Use chunking** for large datasets to improve reliability
5. **Handle partial failures** with `RoseMultiStatusError`
6. **Implement retry logic** for transient failures
7. **Monitor batch progress** and handle errors appropriately
