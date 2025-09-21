#!/usr/bin/env python3
"""
Delete Pipeline Example

Simple example showing how to delete a pipeline using the Rose Python SDK.
"""

import os
from rose_sdk import RoseClient


def main():
    """Delete a pipeline for demo purposes."""
    print("🚀 Rose Python SDK - Delete Pipeline Example")
    print("=" * 50)
    print("Deleting a pipeline for demo")
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
        
        # List existing pipelines
        print("🔹 LISTING PIPELINES")
        print("=" * 30)
        pipelines = client.pipelines.list()
        
        if not pipelines:
            print("📋 No pipelines found. Nothing to delete.")
            return
        
        print(f"📋 Found {len(pipelines)} pipeline(s):")
        for i, pipeline in enumerate(pipelines, 1):
            print(f"   {i}. {pipeline.pipeline_name} (ID: {pipeline.pipeline_id})")
            print(f"      Status: {pipeline.status}")
        print()
        
        # Select the first pipeline for deletion
        target_pipeline = pipelines[0]
        pipeline_id = target_pipeline.pipeline_id
        pipeline_name = target_pipeline.pipeline_name
        
        print(f"🎯 Selected pipeline for deletion:")
        print(f"   Name: {pipeline_name}")
        print(f"   ID: {pipeline_id}")
        print(f"   Status: {target_pipeline.status}")
        print()
        
        # Delete the pipeline
        print("🔹 DELETING PIPELINE")
        print("=" * 30)
        print("📤 Sending delete request...")
        
        client.pipelines.delete(pipeline_id)
        
        print("✅ Delete request sent successfully!")
        print()
        
        # Verify deletion
        print("🔹 VERIFYING DELETION")
        print("=" * 30)
        try:
            # Try to get the pipeline - it should not exist after deletion
            deleted_pipeline = client.pipelines.get(pipeline_id)
            print(f"⚠️  Pipeline still exists (Status: {deleted_pipeline.status})")
            print("   Note: Deletion may be in progress")
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                print("✅ Pipeline deleted successfully!")
            else:
                print(f"❌ Error checking deletion: {e}")
        
        print()
        print("🎉 Pipeline deletion example completed!")
        print("\nKey takeaways:")
        print("1. ✅ Use client.pipelines.delete(pipeline_id) to delete")
        print("2. ✅ Deletion is permanent and cannot be undone")
        print("3. ✅ Check if pipeline exists to verify deletion")
        print("4. ✅ Deletion may take a few seconds to process")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
