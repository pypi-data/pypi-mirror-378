#!/usr/bin/env python3
"""
Batch Append Examples

Simple examples showing how to append records to datasets using the Rose API.
Requires API access - set ROSE_ACCESS_TOKEN environment variable.
"""

import os
import time
from rose_sdk import RoseClient
from rose_sdk.utils import convert_records_to_rose_format
from rose_sdk.exceptions import RoseAPIError


def create_sample_records():
    """Create sample records for batch append."""
    print("🔹 CREATING SAMPLE RECORDS")
    print("=" * 40)
    
    records = []
    base_time = int(time.time())
    
    # Create 20 sample records
    for i in range(20):
        record = {
            "user_id": f"user_{i % 10:03d}",  # 10 unique users
            "item_id": f"item_{i % 15:03d}",  # 15 unique items
            "item_type": ["music", "video", "podcast"][i % 3],
            "play_amount_second": (i * 30) % 300,  # 0-300 seconds
            "interaction": ["play", "pause", "complete"][i % 3],
            "client_upload_timestamp": base_time - (20 - i) * 60,
            "server_upload_timestamp": base_time - (20 - i) * 60 + 5
        }
        records.append(record)
    
    print(f"📋 Created {len(records)} sample records")
    for i, record in enumerate(records[:5], 1):  # Show first 5
        print(f"   {i}. User {record['user_id']} {record['interaction']}ed {record['item_id']}")
    print(f"   ... and {len(records) - 5} more records")
    print()
    
    return records


def find_interaction_dataset(client):
    """Find the interaction dataset."""
    print("🔹 FINDING INTERACTION DATASET")
    print("=" * 40)
    
    try:
        datasets = client.datasets.list()
        interaction_dataset = None
        
        for dataset in datasets:
            if dataset.dataset_name == "interaction":
                interaction_dataset = dataset
                break
        
        if not interaction_dataset:
            print("❌ Interaction dataset not found. Please create it first.")
            return None
        
        print(f"📋 Found interaction dataset:")
        print(f"   Name: {interaction_dataset.dataset_name}")
        print(f"   ID: {interaction_dataset.dataset_id}")
        print()
        
        return interaction_dataset
        
    except Exception as e:
        print(f"❌ Failed to find interaction dataset: {e}")
        return None


def append_records(client, dataset_id, records):
    """Append records to the dataset."""
    print("🔹 APPENDING RECORDS")
    print("=" * 40)
    
    try:
        # Convert records to Rose server format
        rose_records = convert_records_to_rose_format(records)
        
        # Append records using regular records service
        client.datasets.records.create(dataset_id, rose_records)
        
        print(f"✅ Successfully appended {len(records)} records")
        return True
        
    except RoseAPIError as e:
        print(f"❌ Failed to append records: {e.message}")
        return False


def main():
    """Run the batch append examples."""
    print("🚀 Rose Python SDK - Batch Append Examples")
    print("=" * 50)
    print("These examples show how to append records to datasets.")
    print()
    
    # Check for API access
    BASE_URL = os.getenv('ROSE_BASE_URL', 'https://admin-test.rose.blendvision.com')
    ACCESS_TOKEN = os.getenv('ROSE_ACCESS_TOKEN')
    
    if not ACCESS_TOKEN:
        print("❌ Please set ROSE_ACCESS_TOKEN environment variable")
        print("   Example: export ROSE_ACCESS_TOKEN='your_token_here'")
        return
    
    try:
        # Initialize the client
        print(f"Connecting to Rose API at: {BASE_URL}")
        client = RoseClient(
            base_url=BASE_URL,
            access_token=ACCESS_TOKEN
        )
        
        # Find the interaction dataset
        dataset = find_interaction_dataset(client)
        if not dataset:
            return
        
        # Create sample records
        records = create_sample_records()
        
        # Demonstrate append operations
        print("🔹 DEMONSTRATING APPEND OPERATIONS")
        print("=" * 50)
        
        # 1. Simple append
        print("1️⃣ SIMPLE APPEND")
        append_success = append_records(client, dataset.dataset_id, records[:10])
              
        print("🎉 Batch append examples completed!")
        print("\nSummary:")
        print(f"  ✅ Simple Append: {'Success' if append_success else 'Failed'}")
    
        print("\nKey takeaways:")
        print("1. Use append mode to add new records to existing datasets")
        print("2. Always convert data using convert_records_to_rose_format()")
        print("3. Use chunking for better error handling with large datasets")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
