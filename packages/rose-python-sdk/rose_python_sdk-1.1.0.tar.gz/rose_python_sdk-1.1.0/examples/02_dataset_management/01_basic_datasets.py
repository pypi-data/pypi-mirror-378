#!/usr/bin/env python3
"""
Basic Dataset Examples

Simple examples showing how to work with datasets using the Rose Python SDK.
No API access required - these examples demonstrate the dataset concepts.
"""

from rose_sdk.models.dataset import Dataset, CreateDatasetRequest
from rose_sdk.models.field import Field, FieldType, StringProperties, NumericProperties
from rose_sdk.utils import build_schema_from_sample


def show_dataset_models():
    """Show how to work with dataset models."""
    print("🔹 DATASET MODELS")
    print("=" * 40)
    
    # Create sample records to build schema from
    sample_records = [
        {
            "user_id": "user_001",
            "product_id": "prod_001", 
            "rating": 5,
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "user_id": "user_002",
            "product_id": "prod_002",
            "rating": 4,
            "timestamp": "2024-01-15T11:15:00Z"
        }
    ]
    
    # Build schema from sample records
    schema = build_schema_from_sample(
        sample_records=sample_records,
        identifier_fields=["user_id", "product_id"],
        required_fields=["user_id", "product_id", "rating", "timestamp"]
    )
    
    print("📋 Sample Schema (built from sample records):")
    print(f"   Schema type: {type(schema)}")
    print(f"   Schema keys: {list(schema.keys()) if hasattr(schema, 'keys') else 'N/A'}")
    
    # Create a dataset request
    dataset_request = CreateDatasetRequest(
        dataset_name="user_ratings",
        schema=schema,
        enable_housekeeping=True
    )
    
    print(f"\n📋 Dataset Request:")
    print(f"   Name: {dataset_request.dataset_name}")
    print(f"   Housekeeping: {dataset_request.enable_housekeeping}")
    print(f"   Schema type: {type(dataset_request.schema)}")


def show_common_schemas():
    """Show common dataset schema patterns."""
    print("\n🔹 COMMON SCHEMA PATTERNS")
    print("=" * 40)
    
    # E-commerce recommendation schema
    ecommerce_records = [
        {
            "user_id": "user_001",
            "product_id": "prod_001",
            "category": "Electronics",
            "price": 99.99,
            "rating": 5,
            "purchase_date": "2024-01-15T10:30:00Z"
        }
    ]
    
    ecommerce_schema = build_schema_from_sample(
        sample_records=ecommerce_records,
        identifier_fields=["user_id", "product_id"],
        required_fields=["user_id", "product_id", "rating"]
    )
    
    print("📋 E-commerce Recommendation Schema:")
    print(f"   Built from sample records with fields: user_id, product_id, category, price, rating, purchase_date")
    print(f"   Schema type: {type(ecommerce_schema)}")
    
    # ML training data schema
    ml_records = [
        {
            "id": "sample_001",
            "feature_1": 1.5,
            "feature_2": 2.3,
            "feature_3": 0.8,
            "label": 1,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
    
    ml_schema = build_schema_from_sample(
        sample_records=ml_records,
        identifier_fields=["id"],
        required_fields=["id", "feature_1", "feature_2", "feature_3", "label"]
    )
    
    print("\n📋 ML Training Data Schema:")
    print(f"   Built from sample records with fields: id, feature_1, feature_2, feature_3, label, created_at")
    print(f"   Schema type: {type(ml_schema)}")
    
    # User behavior tracking schema
    behavior_records = [
        {
            "session_id": "sess_001",
            "user_id": "user_001",
            "action": "click",
            "page_url": "https://example.com/products",
            "timestamp": "2024-01-15T10:30:00Z",
            "duration": 30
        }
    ]
    
    behavior_schema = build_schema_from_sample(
        sample_records=behavior_records,
        identifier_fields=["session_id"],
        required_fields=["session_id", "user_id", "action", "timestamp"]
    )
    
    print("\n📋 User Behavior Tracking Schema:")
    print(f"   Built from sample records with fields: session_id, user_id, action, page_url, timestamp, duration")
    print(f"   Schema type: {type(behavior_schema)}")


def show_field_types():
    """Show different field types and their properties."""
    print("\n🔹 FIELD TYPES AND PROPERTIES")
    print("=" * 40)
    
    field_examples = [
        {
            "name": "user_id",
            "type": "STRING",
            "description": "Unique user identifier",
            "example": "user_001"
        },
        {
            "name": "age",
            "type": "INTEGER",
            "description": "User age",
            "example": 25
        },
        {
            "name": "price",
            "type": "FLOAT",
            "description": "Product price",
            "example": 99.99
        },
        {
            "name": "is_active",
            "type": "BOOLEAN",
            "description": "Active status flag",
            "example": True
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP",
            "description": "Creation timestamp",
            "example": "2024-01-15T10:30:00Z"
        }
    ]
    
    for field_example in field_examples:
        print(f"📋 {field_example['name']}:")
        print(f"   Type: {field_example['type']}")
        print(f"   Description: {field_example['description']}")
        print(f"   Example: {field_example['example']}")
        print()


def show_dataset_use_cases():
    """Show common dataset use cases."""
    print("\n🔹 COMMON DATASET USE CASES")
    print("=" * 40)
    
    use_cases = [
        {
            "name": "Recommendation System",
            "description": "Store user-item interactions for recommendation algorithms",
            "key_fields": ["user_id", "item_id", "rating", "timestamp"],
            "example": "E-commerce product recommendations"
        },
        {
            "name": "User Behavior Analytics",
            "description": "Track user actions and behavior patterns",
            "key_fields": ["user_id", "action", "page_url", "timestamp"],
            "example": "Website analytics and user journey tracking"
        },
        {
            "name": "ML Training Data",
            "description": "Store features and labels for machine learning models",
            "key_fields": ["id", "feature_1", "feature_2", "label"],
            "example": "Model training and validation datasets"
        },
        {
            "name": "Event Logging",
            "description": "Log system events and application activities",
            "key_fields": ["event_id", "event_type", "timestamp", "metadata"],
            "example": "Application monitoring and debugging"
        },
        {
            "name": "Time Series Data",
            "description": "Store time-stamped measurements and metrics",
            "key_fields": ["timestamp", "metric_name", "value", "tags"],
            "example": "IoT sensor data, performance metrics"
        }
    ]
    
    for use_case in use_cases:
        print(f"📋 {use_case['name']}:")
        print(f"   Description: {use_case['description']}")
        print(f"   Key fields: {', '.join(use_case['key_fields'])}")
        print(f"   Example: {use_case['example']}")
        print()


def main():
    """Run all basic dataset examples."""
    print("🚀 Rose Python SDK - Basic Dataset Examples")
    print("=" * 60)
    print("These examples show the core dataset concepts and schema design.")
    print("No API access required - just run and learn!")
    print()
    
    show_dataset_models()
    show_common_schemas()
    show_field_types()
    show_dataset_use_cases()
    
    print("🎉 Basic dataset examples completed!")
    print("\nNext steps:")
    print("1. Try the API examples to create real datasets")
    print("2. Experiment with different schema designs")
    print("3. Use these patterns in your own applications")


if __name__ == "__main__":
    main()
