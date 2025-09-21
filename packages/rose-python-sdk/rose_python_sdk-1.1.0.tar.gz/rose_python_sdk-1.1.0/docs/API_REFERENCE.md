# API Reference

Complete reference for the Rose Python SDK.

## RoseClient

The main client class for interacting with the Rose Recommendation Service.

### Constructor

```python
RoseClient(base_url: str, access_token: str)
```

**Parameters:**
- `base_url` (str): The base URL of the Rose API
- `access_token` (str): Your API access token

### Properties

- `datasets`: DatasetService instance
- `pipelines`: PipelineService instance  
- `roles`: RoleService instance
- `recommendations`: RecommendationService instance
- `accounts`: AccountService instance

## DatasetService

Manages datasets and their data.

### Methods

#### `list() -> List[Dataset]`
List all datasets for the account.

#### `get(dataset_id: str) -> Dataset`
Get a specific dataset by ID.

#### `create(name: str, schema: Dict[str, Any], enable_housekeeping: bool = True) -> CreateDatasetResponse`
Create a new dataset.

**Parameters:**
- `name` (str): Dataset name
- `schema` (Dict[str, Any]): Dataset schema definition
- `enable_housekeeping` (bool): Whether to enable housekeeping

#### `update(dataset_id: str, name: str = None, schema: Dict[str, Any] = None) -> None`
Update an existing dataset.

#### `delete(dataset_id: str) -> None`
Delete a dataset.

### Records Management

#### `records.create(dataset_id: str, records: List[Dict[str, Any]]) -> None`
Add records to a dataset.

#### `records.list(dataset_id: str, size: int = None) -> List[Record]`
List records from a dataset.

#### `records.update(dataset_id: str, records: List[Dict[str, Any]]) -> None`
Update existing records.

#### `records.delete(dataset_id: str, records: List[Dict[str, Any]]) -> None`
Delete records from a dataset.

### Batch Operations

#### `batch.upload_append(dataset_id: str, records: List[Dict[str, Any]]) -> None`
Append records to a dataset using batch upload.

#### `batch.start_upload(dataset_id: str) -> str`
Start a batch upload session.

#### `batch.upload_batch(dataset_id: str, batch_id: str, records: List[Dict[str, Any]]) -> None`
Upload a batch of records.

#### `batch.complete_upload(dataset_id: str, batch_id: str) -> None`
Complete a batch upload session.

## PipelineService

Manages recommendation pipelines.

### Methods

#### `list() -> List[Pipeline]`
List all pipelines for the account.

#### `get(pipeline_id: str) -> Pipeline`
Get a specific pipeline by ID.

#### `create(name: str, properties: Dict[str, Any]) -> CreatePipelineResponse`
Create a new pipeline.

#### `update(pipeline_id: str, properties: Dict[str, Any]) -> None`
Update an existing pipeline.

#### `delete(pipeline_id: str) -> None`
Delete a pipeline.

#### `list_queries(pipeline_id: str) -> List[Query]`
List queries for a pipeline (requires "CREATE SUCCESSFUL" status).

## RoleService

Manages user roles and permissions.

### Methods

#### `list() -> List[Role]`
List all roles for the account.

#### `get(role_id: str) -> Role`
Get a specific role by ID.

#### `create(name: str, permissions: List[Permission], with_token: bool = False) -> RoleWithToken`
Create a new role.

#### `update(role_id: str, name: str = None, permissions: List[Permission] = None) -> None`
Update an existing role.

#### `delete(role_id: str) -> None`
Delete a role.

#### `issue_token(role_id: str, expiration: int) -> RoleWithToken`
Issue an access token for a role.

## RecommendationService

Gets recommendations and query results.

### Methods

#### `get(query_id: str, parameters: Dict[str, Any]) -> RecommendationResponse`
Get recommendations for a single query.

#### `batch_query(query_id: str, parameters_list: List[Dict[str, Any]]) -> List[RecommendationResponse]`
Get recommendations for multiple queries in batch.

## Utility Functions

### Record Conversion

#### `convert_record_to_rose_format(record: Dict[str, Any]) -> Dict[str, Any]`
Convert a Python record to Rose format.

#### `convert_records_to_rose_format(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
Convert multiple Python records to Rose format.

#### `convert_rose_record_to_simple(rose_record: Dict[str, Any]) -> Dict[str, Any]`
Convert a Rose record to simple Python format.

#### `convert_rose_records_to_simple(rose_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
Convert multiple Rose records to simple Python format.

### Schema Management

#### `build_schema_from_sample(sample_records: List[Dict[str, Any]], identifier_fields: List[str] = None, required_fields: List[str] = None) -> Dict[str, Field]`
Build a schema from sample records.

#### `build_schema_from_dict(schema_dict: Dict[str, Any]) -> Dict[str, Field]`
Build a schema from a dictionary definition.

#### `validate_and_align_records(dataset_id: str, records: List[Dict[str, Any]], client: RoseClient) -> List[Dict[str, Any]]`
Validate and align records against a dataset schema.

### Pipeline Building

#### `create_pipeline(client: RoseClient, account_id: str, pipeline_name: str, scenario: str, dataset_mapping: Dict[str, str]) -> CreatePipelineResponse`
Create a pipeline with dataset mapping.

#### `PipelineBuilder(account_id: str, pipeline_name: str, scenario: str)`
Builder class for creating complex pipeline configurations.

### Batch Processing

#### `prepare_batch_data(records: List[Dict[str, Any]]) -> bytes`
Prepare records for batch upload with compression.

#### `get_batch_headers() -> Dict[str, str]`
Get headers for batch upload requests.

## Data Models

### Dataset

```python
class Dataset:
    dataset_id: str
    dataset_name: str
    status: str
    schema: Dict[str, Any]
    created_at: int
    updated_at: int
```

### Pipeline

```python
class Pipeline:
    pipeline_id: str
    pipeline_name: str
    status: str
    properties: Dict[str, Any]
    created_at: int
    updated_at: int
```

### Role

```python
class Role:
    role_id: str
    role_name: str
    permissions: List[Permission]
    created_at: int
    updated_at: int
```

### Query

```python
class Query:
    query_id: str
    query_name: str
    query_type: str
    status: str
    created_at: int
    updated_at: int
```

## Exception Classes

### RoseAPIError
Base exception for all API-related errors.

### RoseAuthenticationError
Raised when authentication fails.

### RosePermissionError
Raised when the user lacks required permissions.

### RoseNotFoundError
Raised when a requested resource is not found.

### RoseValidationError
Raised when request data validation fails.

### RoseConflictError
Raised when there's a conflict with existing data.

### RoseServerError
Raised when the server encounters an error.

### RoseTimeoutError
Raised when a request times out.

### RoseMultiStatusError
Raised when a batch operation has mixed results (207 status).

## Helper Functions

### Quick Operations

#### `quick_create_dataset(client: RoseClient, name: str, sample_records: List[Dict[str, Any]], identifier_fields: List[str] = None, required_fields: List[str] = None, enable_housekeeping: bool = True) -> str`
Quickly create a dataset from sample records.

#### `quick_create_dataset_with_data(client: RoseClient, name: str, records: List[Dict[str, Any]], identifier_fields: List[str] = None, required_fields: List[str] = None, enable_housekeeping: bool = True) -> str`
Create a dataset and immediately add data to it.

#### `quick_batch_upload(client: RoseClient, dataset_id: str, records: List[Dict[str, Any]], mode: str = "append") -> Optional[str]`
Quickly upload a batch of records.

#### `quick_setup_recommendation_system(client: RoseClient, dataset_name: str, records: List[Dict[str, Any]], pipeline_name: str, pipeline_properties: Dict[str, Any], identifier_fields: List[str] = None, required_fields: List[str] = None) -> tuple[str, str, List[str]]`
Set up a complete recommendation system.

### Account Management

#### `generate_unique_account_id(base_id: str) -> str`
Generate a unique account ID.

#### `create_account_with_conflict_handling(client: RoseClient, account_id: str, account_name: str) -> str`
Create an account with conflict handling.

#### `create_account_and_token_with_conflict_handling(client: RoseClient, account_id: str, account_name: str, expiration: int = 3600) -> tuple[str, str]`
Create an account and issue a token with conflict handling.
