#!/usr/bin/env python3
"""
Dataset API Usage Examples

Examples showing how to create and manage datasets using the Rose API.
Requires API access - set ROSE_ACCESS_TOKEN environment variable.
"""

import os
import sys
from rose_sdk import RoseClient
from rose_sdk.models.dataset import Dataset, CreateDatasetRequest
from rose_sdk.models.record import Record, Records
from rose_sdk.utils import build_schema_from_sample


def create_demo_datasets(client):
    """Create interaction and metadata datasets using predefined schemas."""
    print("\n🔹 CREATING INTERACTION AND METADATA DATASETS")
    print("=" * 40)
    
    datasets = {}
    
    # Create interaction dataset
    try:
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
            "item_type": {
                "field_type": "str",
                "is_identifier": True,
                "is_required": True
            },
            "play_amount_second": {
                "field_type": "int",
                "is_identifier": False,
                "is_required": True
            },
            "interaction": {
                "field_type": "str",
                "is_identifier": False,
                "is_required": True
            },
            "client_upload_timestamp": {
                "field_type": "int",
                "is_identifier": True,
                "is_required": True
            },
            "server_upload_timestamp": {
                "field_type": "int",
                "is_identifier": False,
                "is_required": True
            }
        }
        
        interaction_response = client.datasets.create(
            name="interaction",
            schema=interaction_schema,
            enable_housekeeping=True
        )
        
        datasets['interaction'] = interaction_response
        print(f"✅ Created interaction dataset (ID: {interaction_response.dataset_id})")
        print(f"   Schema fields: {len(interaction_schema)}")
        
    except Exception as e:
        print(f"❌ Failed to create interaction dataset: {e}")
    
    # Create metadata dataset
    try:
        metadata_schema = {
            "item_id": {
                "field_type": "str",
                "is_identifier": True,
                "is_required": True
            },
            "item_type": {
                "field_type": "str",
                "is_identifier": True,
                "is_required": True
            },
            "content_rating": {
                "field_type": "str",
                "is_identifier": False,
                "is_required": True
            },
            "name": {
                "field_type": "str",
                "is_identifier": False,
                "is_required": True
            },
            "description": {
                "field_type": "str",
                "is_identifier": False,
                "is_required": True
            },
            "expire_timestamp": {
                "field_type": "int",
                "is_identifier": False,
                "is_required": False
            },
            "publish_timestamp": {
                "field_type": "int",
                "is_identifier": False,
                "is_required": False
            },
            "artists": {
                "field_type": "list",
                "list_props": {
                    "children": {"field_type": "str"}
                },
                "is_identifier": False,
                "is_required": True
            },
            "genres": {
                "field_type": "list",
                "list_props": {
                    "children": {"field_type": "str"}
                },
                "is_identifier": False,
                "is_required": True
            }
        }
        
        metadata_response = client.datasets.create(
            name="metadata",
            schema=metadata_schema,
            enable_housekeeping=True
        )
        
        datasets['metadata'] = metadata_response
        print(f"✅ Created metadata dataset (ID: {metadata_response.dataset_id})")
        print(f"   Schema fields: {len(metadata_schema)}")
        
    except Exception as e:
        print(f"❌ Failed to create metadata dataset: {e}")
    
    return datasets


def show_dataset_details(client, datasets):
    """Show details of created datasets."""
    print("\n🔹 DATASET DETAILS")
    print("=" * 40)
    
    for dataset_name, dataset_response in datasets.items():
        try:
            print(f"📋 {dataset_name} dataset:")
            print(f"   ID: {dataset_response.dataset_id}")
            print(f"   Name: {dataset_name}")
            print(f"   Status: Created successfully")
            print()
            
        except Exception as e:
            print(f"❌ Failed to show details for {dataset_name} dataset: {e}")


def list_and_manage_datasets(client):
    """List and manage existing datasets."""
    print("\n🔹 DATASET MANAGEMENT")
    print("=" * 40)
    
    try:
        # List all datasets
        datasets = client.datasets.list()
        print(f"📋 Found {len(datasets)} datasets:")
        
        for dataset in datasets:
            print(f"   - {dataset.dataset_name} (ID: {dataset.dataset_id})")
            print(f"     Status: {dataset.status}")
            print(f"     Housekeeping: {dataset.enable_housekeeping}")
            print(f"     Schema type: {type(dataset.schema)}")
            print()
            
    except Exception as e:
        print(f"❌ Failed to list datasets: {e}")


def show_schema_analysis(datasets):
    """Show analysis of created dataset schemas."""
    print("\n🔹 SCHEMA ANALYSIS")
    print("=" * 40)
    
    for dataset_name, dataset_response in datasets.items():
        try:
            print(f"📋 {dataset_name} dataset schema analysis:")
            print(f"   Dataset ID: {dataset_response.dataset_id}")
            print(f"   Schema type: {type(dataset_response.schema)}")
            print(f"   Ready for data ingestion")
            print()
            
        except Exception as e:
            print(f"❌ Failed to analyze schema for {dataset_name} dataset: {e}")


def main():
    """Run all dataset API examples."""
    print("🚀 Rose Python SDK - Dataset API Usage Examples")
    print("=" * 60)
    print("These examples show how to create and manage datasets using the Rose API.")
    print()
    
    # Check for API access
    BASE_URL = os.getenv('ROSE_BASE_URL', 'https://admin-test.rose.blendvision.com')
    ACCESS_TOKEN = os.getenv('ROSE_ACCESS_TOKEN')
    
    if not ACCESS_TOKEN:
        print("❌ Please set ROSE_ACCESS_TOKEN environment variable")
        print("   Example: export ROSE_ACCESS_TOKEN='your_token_here'")
        print()
        print("For demonstration purposes, showing basic dataset concepts:")

        return
    
    try:
        # Initialize the client
        print(f"Connecting to Rose API at: {BASE_URL}")
        client = RoseClient(
            base_url=BASE_URL,
            access_token=ACCESS_TOKEN
        )
        
        # Run examples
        
        demo_datasets = create_demo_datasets(client)
        
        all_datasets = { **demo_datasets}
        
        show_dataset_details(client, all_datasets)
        list_and_manage_datasets(client)
        show_schema_analysis(all_datasets)
        
        print("\n🎉 Dataset API examples completed successfully!")
        print("\nKey takeaways:")
        print("1. Design schemas carefully with proper field types and validation")
        print("2. Use meaningful dataset names and field names")
        print("3. Enable housekeeping for automatic data management")
        print("4. Add sample data to test your datasets")
        print("5. Use the list operation to monitor your datasets")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
