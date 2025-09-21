#!/usr/bin/env python3
"""
Batch Overwrite Examples

Simple examples showing how to overwrite datasets using the Rose API.
Requires API access - set ROSE_ACCESS_TOKEN environment variable.
"""

import os
import time
from rose_sdk import RoseClient
from rose_sdk.utils import convert_records_to_rose_format
from rose_sdk.exceptions import RoseAPIError


def create_sample_records():
    """Create sample records for batch overwrite."""
    print("🔹 CREATING SAMPLE RECORDS")
    print("=" * 40)
    
    records = []
    base_time = int(time.time())
    
    # Create 30 sample records
    for i in range(30):
        record = {
            "user_id": f"user_{i % 15:03d}",  # 15 unique users
            "item_id": f"item_{i % 20:03d}",  # 20 unique items
            "item_type": ["music", "video", "podcast", "movie"][i % 4],
            "play_amount_second": (i * 20) % 400,  # 0-400 seconds
            "interaction": ["play", "pause", "complete", "skip"][i % 4],
            "client_upload_timestamp": base_time - (30 - i) * 45,
            "server_upload_timestamp": base_time - (30 - i) * 45 + 5
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


def overwrite_dataset(client, dataset_id, records):
    """Overwrite the entire dataset with new records."""
    print("🔹 OVERWRITING DATASET")
    print("=" * 40)
    
    try:
        # Convert records to Rose server format
        rose_records = convert_records_to_rose_format(records)
        
        # Start batch upload process
        print("📋 Starting batch upload process...")
        batch_id = client.datasets.batch.start_upload(dataset_id)
        print(f"   Batch ID: {batch_id}")
        
        # Upload batch data
        print("📋 Uploading batch data...")
        client.datasets.batch.upload_batch(dataset_id, batch_id, rose_records)
        print(f"   Uploaded {len(records)} records")
        
        # Complete the upload
        print("📋 Completing batch upload...")
        client.datasets.batch.complete_upload(dataset_id, batch_id)
        
        print(f"✅ Successfully overwrote dataset with {len(records)} records")
        return True
        
        
    except RoseAPIError as e:
        print(f"❌ Failed to overwrite dataset: {e.message}")
        
        # Try to abort the batch if it was started
        try:
            client.datasets.batch.abort_upload(dataset_id, batch_id)
            print("   Aborted batch upload process")
        except:
            pass
        
        return False


def overwrite_in_chunks(client, dataset_id, records, chunk_size=10):
    """Overwrite dataset by uploading data in chunks."""
    print("🔹 OVERWRITING IN CHUNKS")
    print("=" * 40)
    
    try:
        # Start batch upload process
        print("📋 Starting batch upload process...")
        batch_id = client.datasets.batch.start_upload(dataset_id)
        print(f"   Batch ID: {batch_id}")
        
        # Split records into chunks
        chunks = [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]
        
        print(f"📊 Uploading {len(records)} records in {len(chunks)} chunks of {chunk_size}")
        print()
        
        total_success = 0
        total_failed = 0
        
        for i, chunk in enumerate(chunks, 1):
            print(f"📋 Processing chunk {i}/{len(chunks)} ({len(chunk)} records)...")
            
            try:
                rose_records = convert_records_to_rose_format(chunk)
                client.datasets.batch.upload_batch(dataset_id, batch_id, rose_records)
                
                print(f"   ✅ Chunk {i} uploaded successfully")
                total_success += len(chunk)
                
            except RoseAPIError as e:
                print(f"   ❌ Chunk {i} failed: {e.message}")
                total_failed += len(chunk)
            
            # Small delay between chunks
            if i < len(chunks):
                time.sleep(0.5)
        
        # Complete the upload
        print("📋 Completing batch upload...")
        client.datasets.batch.complete_upload(dataset_id, batch_id)
        
        print()
        print(f"📊 Chunked overwrite completed:")
        print(f"   Total records: {len(records)}")
        print(f"   Successful: {total_success}")
        print(f"   Failed: {total_failed}")
        
        return total_success > 0
        
    except RoseAPIError as e:
        print(f"❌ Failed to start batch upload: {e.message}")
        return False


def demonstrate_abort_upload(client, dataset_id):
    """Demonstrate how to abort a batch upload."""
    print("🔹 DEMONSTRATING ABORT UPLOAD")
    print("=" * 40)
    
    try:
        # Start a batch upload
        print("📋 Starting batch upload process...")
        batch_id = client.datasets.batch.start_upload(dataset_id)
        print(f"   Batch ID: {batch_id}")
        
        # Abort the upload
        print("📋 Aborting batch upload...")
        client.datasets.batch.abort_upload(dataset_id, batch_id)
        
        print("✅ Successfully aborted batch upload")
        return True
        
    except RoseAPIError as e:
        print(f"❌ Failed to abort upload: {e.message}")
        return False


def main():
    """Run the batch overwrite examples."""
    print("🚀 Rose Python SDK - Batch Overwrite Examples")
    print("=" * 50)
    print("These examples show how to overwrite datasets with new data.")
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
        
        # Demonstrate overwrite operations
        print("🔹 DEMONSTRATING OVERWRITE OPERATIONS")
        print("=" * 50)
        
        # 1. Simple overwrite
        print("1️⃣ SIMPLE OVERWRITE")
        overwrite_success = overwrite_dataset(client, dataset.dataset_id, records[:15])
        
        # 2. Chunked overwrite
        print("2️⃣ CHUNKED OVERWRITE")
        chunked_success = overwrite_in_chunks(client, dataset.dataset_id, records[15:], chunk_size=5)
        
        # 3. Abort demonstration
        print("3️⃣ ABORT UPLOAD DEMONSTRATION")
        abort_success = demonstrate_abort_upload(client, dataset.dataset_id)
        
        print("🎉 Batch overwrite examples completed!")
        print("\nSummary:")
        print(f"  ✅ Simple Overwrite: {'Success' if overwrite_success else 'Failed'}")
        print(f"  ✅ Chunked Overwrite: {'Success' if chunked_success else 'Failed'}")
        print(f"  ✅ Abort Upload: {'Success' if abort_success else 'Failed'}")
        
        print("\nKey takeaways:")
        print("1. Use overwrite mode to replace entire dataset content")
        print("2. Always start with start_upload() and end with complete_upload()")
        print("3. Use abort_upload() to cancel a batch process if needed")
        print("4. Handle errors and abort incomplete batches")
        print("5. Use chunking for better error handling with large datasets")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
