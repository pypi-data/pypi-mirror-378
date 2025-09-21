#!/usr/bin/env python3
"""
Simple Records Management Examples

Examples showing how to perform CRUD operations on records using the Rose API.
Requires API access - set ROSE_ACCESS_TOKEN environment variable.
"""

import os
import time
from rose_sdk import RoseClient
from rose_sdk.utils import convert_records_to_rose_format
from rose_sdk.exceptions import RoseMultiStatusError, RoseAPIError
from rose_sdk.models.record import Record


def create_sample_records():
    """Create sample interaction records for testing."""
    print("🔹 CREATING SAMPLE RECORDS")
    print("=" * 40)
    
    # Create 5 sample interaction records
    records = [
        {
            "user_id": "user_001",
            "item_id": "song_001",
            "item_type": "music",
            "play_amount_second": 180,
            "interaction": "play",
            "client_upload_timestamp": int(time.time()) - 3600,
            "server_upload_timestamp": int(time.time()) - 3595
        },
        {
            "user_id": "user_001",
            "item_id": "video_001",
            "item_type": "video",
            "play_amount_second": 45,
            "interaction": "pause",
            "client_upload_timestamp": int(time.time()) - 3500,
            "server_upload_timestamp": int(time.time()) - 3495
        },
        {
            "user_id": "user_002",
            "item_id": "song_002",
            "item_type": "music",
            "play_amount_second": 240,
            "interaction": "complete",
            "client_upload_timestamp": int(time.time()) - 3400,
            "server_upload_timestamp": int(time.time()) - 3395
        },
        {
            "user_id": "user_002",
            "item_id": "podcast_001",
            "item_type": "podcast",
            "play_amount_second": 300,
            "interaction": "play",
            "client_upload_timestamp": int(time.time()) - 3300,
            "server_upload_timestamp": int(time.time()) - 3295
        },
        {
            "user_id": "user_003",
            "item_id": "movie_001",
            "item_type": "movie",
            "play_amount_second": 1200,
            "interaction": "play",
            "client_upload_timestamp": int(time.time()) - 3200,
            "server_upload_timestamp": int(time.time()) - 3195
        }
    ]
    
    print(f"📋 Created {len(records)} sample records")
    for i, record in enumerate(records, 1):
        print(f"   {i}. User {record['user_id']} {record['interaction']}ed {record['item_id']} ({record['item_type']})")
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
        print(f"   Status: {interaction_dataset.status}")
        print()
        
        return interaction_dataset
        
    except Exception as e:
        print(f"❌ Failed to find interaction dataset: {e}")
        return None

def create_records(client, dataset_id, records):
    """Create new records in the dataset."""
    print("🔹 CREATE RECORDS")
    print("=" * 40)
    
    try:
        # Convert records to Rose server format
        rose_records = convert_records_to_rose_format(records)
        
        # Create records
        client.datasets.records.create(
            dataset_id=dataset_id,
            records=rose_records
        )
        
        print(f"✅ Successfully created {len(records)} records")
        return True
        
    except RoseMultiStatusError as e:
        print(f"⚠️  Partial success: Some records failed to create")
        e.print_errors()
        failed_count = len(e.get_failed_records())
        success_count = len(records) - failed_count
        print(f"📊 Results: {success_count} succeeded, {failed_count} failed")
        return success_count > 0
        
    except RoseAPIError as e:
        print(f"❌ Failed to create records: {e.message}")
        return False


def list_records(client: RoseClient, dataset_id: str, size: int = 3) -> list[Record]:
    """List records from the dataset."""
    print("🔹 LIST RECORDS")
    print("=" * 40)
    
    try:
        records = client.datasets.records.list(dataset_id=dataset_id, size=size)
        
        print(f"📋 Found {len(records)} records:")
        for i, record in enumerate(records, 1):
            print(f"   {i}. {record}")
        print()
        
        return records
        
    except Exception as e:
        print(f"❌ Failed to list records: {e}")
        return []


def update_records(client: RoseClient, dataset_id: str, records: list[dict]) -> bool:
    """Update existing records in the dataset."""
    print("🔹 UPDATE RECORDS")
    print("=" * 40)
    
    try:
        # Convert records to Rose server format
        rose_records = convert_records_to_rose_format(records)
        
        # Update records
        client.datasets.records.update(
            dataset_id=dataset_id,
            records=rose_records
        )
        
        print(f"✅ Successfully updated {len(records)} records")
        return True
        
    except RoseMultiStatusError as e:
        print(f"⚠️  Partial success: Some records failed to update")
        e.print_errors()
        failed_count = len(e.get_failed_records())
        success_count = len(records) - failed_count
        print(f"📊 Results: {success_count} succeeded, {failed_count} failed")
        return success_count > 0
        
    except RoseAPIError as e:
        print(f"❌ Failed to update records: {e.message}")
        return False


def patch_records(client: RoseClient, dataset_id: str, records: list[dict]) -> bool:
    """Patch (partially update) existing records in the dataset."""
    print("🔹 PATCH RECORDS")
    print("=" * 40)
    
    try:
        # Convert records to Rose server format
        rose_records = convert_records_to_rose_format(records)
        
        # Patch records
        client.datasets.records.patch(
            dataset_id=dataset_id,
            records=rose_records
        )
        
        print(f"✅ Successfully patched {len(records)} records")
        return True
        
    except RoseMultiStatusError as e:
        print(f"⚠️  Partial success: Some records failed to patch")
        e.print_errors()
        failed_count = len(e.get_failed_records())
        success_count = len(records) - failed_count
        print(f"📊 Results: {success_count} succeeded, {failed_count} failed")
        return success_count > 0
        
    except RoseAPIError as e:
        print(f"❌ Failed to patch records: {e.message}")
        return False


def delete_records(client: RoseClient, dataset_id: str, records: list[dict]) -> bool:
    """Delete records from the dataset."""
    print("🔹 DELETE RECORDS")
    print("=" * 40)
    
    try:
        # Convert records to Rose server format
        rose_records = convert_records_to_rose_format(records)
        
        # Delete records
        client.datasets.records.delete(
            dataset_id=dataset_id,
            records=rose_records
        )
        
        print(f"✅ Successfully deleted {len(records)} records")
        return True
        
    except RoseMultiStatusError as e:
        print(f"⚠️  Partial success: Some records failed to delete")
        e.print_errors()
        failed_count = len(e.get_failed_records())
        success_count = len(records) - failed_count
        print(f"📊 Results: {success_count} succeeded, {failed_count} failed")
        return success_count > 0
        
    except RoseAPIError as e:
        print(f"❌ Failed to delete records: {e.message}")
        return False



def demonstrate_crud_operations(client: RoseClient, dataset_id: str) -> None:
    """Demonstrate all CRUD operations."""
    print("🔹 DEMONSTRATING CRUD OPERATIONS")
    print("=" * 50)

    
    # 1. CREATE - Add new records
    print("1️⃣ CREATE OPERATION")
    sample_records = create_sample_records()
    create_success = create_records(client, dataset_id, sample_records)
    
    if not create_success:
        print("❌ Create operation failed, skipping other operations")
        return
    
    # 2. READ - List records
    print("2️⃣ READ OPERATION")
    existing_records = list_records(client, dataset_id, size=3)
    
    if not existing_records:
        print("❌ No records found, skipping update/patch/delete operations")
        return
    
    # 3. UPDATE - Update existing records
    print("3️⃣ UPDATE OPERATION")
    # Create updated versions of the first 2 records
    updated_records = [
        {
            "user_id": "user_001",
            "item_id": "song_001",
            "item_type": "music",
            "play_amount_second": 200,  # Updated play time
            "interaction": "complete",  # Changed from "play" to "complete"
            "client_upload_timestamp": int(time.time()) - 3600,
            "server_upload_timestamp": int(time.time()) - 3595
        },
        {
            "user_id": "user_001",
            "item_id": "video_001",
            "item_type": "video",
            "play_amount_second": 60,  # Updated play time
            "interaction": "complete",  # Changed from "pause" to "complete"
            "client_upload_timestamp": int(time.time()) - 3500,
            "server_upload_timestamp": int(time.time()) - 3495
        }
    ]
    
    update_success = update_records(client, dataset_id, updated_records)
    
    # 4. PATCH - Partially update records
    print("4️⃣ PATCH OPERATION")
    # Create partial updates using existing records (only some fields)
    patch_records_data = []
    for record in existing_records[:2]:  # Use first 2 existing records
        # Convert Record object to dict and modify specific fields
        record_dict = dict(record)
        record_dict["play_amount_second"] = 100  # Update play time
        patch_records_data.append(record_dict)
    
    patch_success = patch_records(client, dataset_id, patch_records_data)
    
    # 5. DELETE - Remove some records
    print("5️⃣ DELETE OPERATION")
    # Delete the last 2 records from existing records
    records_to_delete = []
    for record in existing_records[-2:]:  # Use last 2 existing records
        # Convert Record object to dict for deletion
        record_dict = dict(record)
        records_to_delete.append(record_dict)
    
    delete_success = delete_records(client, dataset_id, records_to_delete)
    
    # 6. Final READ - List remaining records
    print("6️⃣ FINAL READ OPERATION")
    final_records = list_records(client, dataset_id, size=5)
    
    print("🎉 CRUD operations demonstration completed!")
    print("\nSummary:")
    print(f"  ✅ Create: {'Success' if create_success else 'Failed'}")
    print(f"  ✅ Read: {'Success' if existing_records else 'Failed'}")
    print(f"  ✅ Update: {'Success' if update_success else 'Failed'}")
    print(f"  ✅ Patch: {'Success' if patch_success else 'Failed'}")
    print(f"  ✅ Delete: {'Success' if delete_success else 'Failed'}")
    print(f"  📊 Final record count: {len(final_records)}")


def main():
    """Run the records management examples."""
    print("🚀 Rose Python SDK - Simple Records Management Examples")
    print("=" * 60)
    print("These examples demonstrate CRUD operations on the interaction dataset.")
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
        
        # Demonstrate CRUD operations
        demonstrate_crud_operations(client, dataset.dataset_id)
        
        print("\nKey takeaways:")
        print("1. Use convert_records_to_rose_format() to convert data")
        print("2. Handle RoseMultiStatusError for partial failures")
        print("3. CREATE adds new records")
        print("4. READ lists existing records")
        print("5. UPDATE replaces entire records")
        print("6. PATCH updates only specified fields")
        print("7. DELETE removes records")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
