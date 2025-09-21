#!/usr/bin/env python3
"""
Schema Validation Examples

Examples showing how to validate and align user data against dataset schemas.
This helps ensure data integrity before uploading to the Rose API.
"""

import os
from rose_sdk import RoseClient
from rose_sdk.utils import (
    validate_and_align_records,
    get_schema_summary,
    print_schema_summary,
    SchemaValidationError,
    convert_records_to_rose_format
)
from rose_sdk.exceptions import RoseMultiStatusError, RoseAPIError


def show_schema_validation():
    """Show how to validate data against a dataset schema."""
    print("🔹 SCHEMA VALIDATION")
    print("=" * 40)
    
    # Check for API access
    BASE_URL = os.getenv('ROSE_BASE_URL', 'https://admin-test.rose.blendvision.com')
    ACCESS_TOKEN = os.getenv('ROSE_ACCESS_TOKEN')
    
    if not ACCESS_TOKEN:
        print("❌ Please set ROSE_ACCESS_TOKEN environment variable")
        print("   Example: export ROSE_ACCESS_TOKEN='your_token_here'")
        return
    
    try:
        # Initialize the client
        client = RoseClient(
            base_url=BASE_URL,
            access_token=ACCESS_TOKEN
        )
        
        # Find the interaction dataset
        datasets = client.datasets.list()
        interaction_dataset = None
        
        for dataset in datasets:
            if dataset.dataset_name == "interaction":
                interaction_dataset = dataset
                break
        
        if not interaction_dataset:
            print("❌ Interaction dataset not found. Please create it first.")
            return
        
        print(f"📋 Found dataset: {interaction_dataset.dataset_name}")
        print(f"   Dataset ID: {interaction_dataset.dataset_id}")
        print()
        
        # Show schema information
        print_schema_summary(interaction_dataset.schema)
        
        # Example 1: Valid data
        print("🔹 EXAMPLE 1: Valid Data")
        print("=" * 30)
        
        valid_records = [
            {
                "user_id": "user_001",
                "item_id": "song_001",
                "item_type": "music",
                "play_amount_second": 180,
                "interaction": "play",
                "client_upload_timestamp": 1705123456,
                "server_upload_timestamp": 1705123460
            },
            {
                "user_id": "user_002",
                "item_id": "video_001",
                "item_type": "video",
                "play_amount_second": 45,
                "interaction": "pause",
                "client_upload_timestamp": 1705123500,
                "server_upload_timestamp": 1705123505
            }
        ]
        
        print("📋 Input records:")
        for i, record in enumerate(valid_records, 1):
            print(f"   Record {i}: {record}")
        print()
        
        # Validate and align
        aligned_records, warnings = validate_and_align_records(
            valid_records, 
            interaction_dataset.schema,
            strict_validation=True
        )
        
        print("✅ Validation result:")
        print(f"   Aligned records: {len(aligned_records)}")
        print(f"   Warnings: {len(warnings)}")
        
        if warnings:
            print("   Warnings:")
            for warning in warnings:
                print(f"     • {warning}")
        print()
        
        # Example 2: Data with type mismatches
        print("🔹 EXAMPLE 2: Data with Type Mismatches")
        print("=" * 40)
        
        problematic_records = [
            {
                "user_id": "user_003",
                "item_id": "song_002",
                "item_type": "music",
                "play_amount_second": "180",  # String instead of int
                "interaction": "play",
                "client_upload_timestamp": "1705123600",  # String instead of int
                "server_upload_timestamp": 1705123605
            },
            {
                "user_id": "user_004",
                "item_id": "video_002",
                "item_type": "video",
                "play_amount_second": 45.5,  # Float instead of int
                "interaction": "pause",
                "client_upload_timestamp": 1705123700,
                "server_upload_timestamp": 1705123705
            }
        ]
        
        print("📋 Input records with type issues:")
        for i, record in enumerate(problematic_records, 1):
            print(f"   Record {i}: {record}")
        print()
        
        # Validate with strict=False to show warnings
        aligned_records, warnings = validate_and_align_records(
            problematic_records, 
            interaction_dataset.schema,
            strict_validation=False
        )
        
        print("⚠️  Validation result (non-strict):")
        print(f"   Aligned records: {len(aligned_records)}")
        print(f"   Warnings: {len(warnings)}")
        
        if warnings:
            print("   Warnings:")
            for warning in warnings:
                print(f"     • {warning}")
        print()
        
        # Example 3: Missing required fields
        print("🔹 EXAMPLE 3: Missing Required Fields")
        print("=" * 40)
        
        incomplete_records = [
            {
                "user_id": "user_005",
                "item_id": "song_003",
                # Missing item_type, play_amount_second, etc.
                "interaction": "play"
            }
        ]
        
        print("📋 Input records with missing fields:")
        for i, record in enumerate(incomplete_records, 1):
            print(f"   Record {i}: {record}")
        print()
        
        try:
            # This should fail with strict validation
            aligned_records, warnings = validate_and_align_records(
                incomplete_records, 
                interaction_dataset.schema,
                strict_validation=True
            )
        except SchemaValidationError as e:
            print(f"❌ Validation failed (strict mode): {e}")
            print()
            
            # Try with non-strict mode
            print("📋 Trying with non-strict mode:")
            aligned_records, warnings = validate_and_align_records(
                incomplete_records, 
                interaction_dataset.schema,
                strict_validation=False
            )
            
            print(f"⚠️  Validation result (non-strict):")
            print(f"   Aligned records: {len(aligned_records)}")
            print(f"   Warnings: {len(warnings)}")
            
            if warnings:
                print("   Warnings:")
                for warning in warnings:
                    print(f"     • {warning}")
        print()
        
        # Example 4: Convert to Rose format and upload
        print("🔹 EXAMPLE 4: Convert and Upload")
        print("=" * 35)
        
        # Use the aligned records from example 1
        if aligned_records:
            print("📋 Converting aligned records to Rose format...")
            rose_records = convert_records_to_rose_format(aligned_records)
            
            print(f"✅ Converted {len(rose_records)} records to Rose format")
            print("   Sample converted record:")
            if rose_records:
                sample_record = rose_records[0]
                for field, value in sample_record.items():
                    print(f"     {field}: {value}")
            print()
            
            # Upload the records
            print("📤 Uploading records to dataset...")
            try:
                response = client.datasets.records.create(
                    dataset_id=interaction_dataset.dataset_id,
                    records=rose_records
                )
                print(f"✅ Successfully uploaded {len(rose_records)} records")
                
            except RoseMultiStatusError as e:
                print(f"⚠️  Partial success: Some records failed")
                e.print_errors()
                
            except RoseAPIError as e:
                print(f"❌ Upload failed: {e}")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")


def show_schema_info():
    """Show how to get schema information."""
    print("🔹 SCHEMA INFORMATION")
    print("=" * 30)
    
    # Check for API access
    BASE_URL = os.getenv('ROSE_BASE_URL', 'https://admin-test.rose.blendvision.com')
    ACCESS_TOKEN = os.getenv('ROSE_ACCESS_TOKEN')
    
    if not ACCESS_TOKEN:
        print("❌ Please set ROSE_ACCESS_TOKEN environment variable")
        return
    
    try:
        # Initialize the client
        client = RoseClient(
            base_url=BASE_URL,
            access_token=ACCESS_TOKEN
        )
        
        # Get all datasets and show their schemas
        datasets = client.datasets.list()
        
        for dataset in datasets:
            print(f"📋 Dataset: {dataset.dataset_name}")
            print(f"   ID: {dataset.dataset_id}")
            
            # Get schema summary
            summary = get_schema_summary(dataset.schema)
            print(f"   Fields: {summary['total_fields']}")
            print(f"   Required: {', '.join(summary['required_fields']) or 'None'}")
            print(f"   Identifiers: {', '.join(summary['identifier_fields']) or 'None'}")
            print()
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")


def main():
    """Run schema validation examples."""
    print("🚀 Rose Python SDK - Schema Validation Examples")
    print("=" * 55)
    print("These examples show how to validate and align data against dataset schemas.")
    print()
    
    show_schema_validation()
    print()
    show_schema_info()
    
    print("🎉 Schema validation examples completed!")
    print("\nKey takeaways:")
    print("1. ✅ Always validate data against schema before uploading")
    print("2. ✅ Use strict_validation=True for production data")
    print("3. ✅ Use strict_validation=False for data exploration")
    print("4. ✅ Check schema summary to understand field requirements")
    print("5. ✅ Convert to Rose format after validation")


if __name__ == "__main__":
    main()
