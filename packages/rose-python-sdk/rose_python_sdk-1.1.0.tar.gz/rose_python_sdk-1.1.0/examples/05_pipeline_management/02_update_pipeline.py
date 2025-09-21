#!/usr/bin/env python3
"""
Update Pipeline Example

Example showing how to update a pipeline using the Rose Python SDK.
This example demonstrates the correct way to update pipeline properties.
"""

import os
import time
from rose_sdk import RoseClient
from rose_sdk.utils.pipeline import (
    create_pipeline,
    PipelineBuilder,
    get_supported_scenarios
)
from typing import List, Dict


def list_pipelines(client: RoseClient):
    """List all pipelines for the account."""
    print("🔹 LISTING PIPELINES")
    print("=" * 40)
    
    try:
        pipelines = client.pipelines.list()
        
        if not pipelines:
            print("📋 No pipelines found")
            return []
        
        print(f"📋 Found {len(pipelines)} pipeline(s):")
        for i, pipeline in enumerate(pipelines, 1):
            print(f"   {i}. {pipeline.pipeline_name} (ID: {pipeline.pipeline_id})")
            print(f"      Status: {pipeline.status}")
            print(f"      Scenario: {pipeline.properties.get('scenario', 'Unknown')}")
            print(f"      Datasets: {pipeline.properties.get('datasets', {})}")
            print()
        
        return pipelines
        
    except Exception as e:
        print(f"❌ Failed to list pipelines: {e}")
        return []


def update_pipeline_properties(client: RoseClient, pipeline_id: str, new_properties: Dict[str, any]):
    """Update pipeline properties and monitor the result."""
    print(f"🔹 UPDATING PIPELINE {pipeline_id}")
    print("=" * 50)
    
    try:
        # Get current pipeline state
        print("📋 Current pipeline state:")
        current_pipeline = client.pipelines.get(pipeline_id)
        print(f"   Name: {current_pipeline.pipeline_name}")
        print(f"   Status: {current_pipeline.status}")
        print(f"   Current Properties: {current_pipeline.properties}")
        print()
        
        # Update the pipeline
        print("📤 Sending update request...")
        client.pipelines.update(pipeline_id, new_properties)
        print("✅ Update request accepted")
        print()
        
        # Monitor the update
        print("⏳ Monitoring update progress...")
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(2)  # Wait 2 seconds between checks
            
            try:
                updated_pipeline = client.pipelines.get(pipeline_id)
                print(f"   Attempt {attempt + 1}: Status = {updated_pipeline.status}")
                
                # Check if update is complete
                if updated_pipeline.status in ["UPDATE SUCCESSFUL", "CREATE SUCCESSFUL"]:
                    print("✅ Pipeline update completed successfully!")
                    print(f"   Updated Properties: {updated_pipeline.properties}")
                    return True
                elif updated_pipeline.status == "UPDATE FAILED":
                    print("❌ Pipeline update failed!")
                    return False
                
                attempt += 1
                
            except Exception as e:
                print(f"   Attempt {attempt + 1}: Error checking status - {e}")
                attempt += 1
        
        print("⏰ Update monitoring timeout - check pipeline status manually")
        return False
        
    except Exception as e:
        print(f"❌ Failed to update pipeline: {e}")
        return False


def demonstrate_property_updates():
    """Demonstrate different types of property updates."""
    print("🔹 PROPERTY UPDATE EXAMPLES")
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
        print(f"Connecting to Rose API at: {BASE_URL}")
        client = RoseClient(
            base_url=BASE_URL,
            access_token=ACCESS_TOKEN
        )
        
        # List existing pipelines
        pipelines = list_pipelines(client)
        if not pipelines:
            print("❌ No pipelines found. Please create a pipeline first.")
            return
        
        # Use the first pipeline for demonstration
        target_pipeline = pipelines[0]
        pipeline_id = target_pipeline.pipeline_id
        
        print(f"🎯 Using pipeline: {target_pipeline.pipeline_name} (ID: {pipeline_id})")
        print()
        
        # Example 1: Add a simple property
        print("📋 Example 1: Adding a simple property")
        simple_update = {"extra_key": "extra_value", "updated_at": int(time.time())}
        success = update_pipeline_properties(client, pipeline_id, simple_update)
        
        if not success:
            print("❌ Simple update failed, skipping other examples")
            return
        
        print()
        
        # Example 2: Update dataset mapping
        print("📋 Example 2: Updating dataset mapping")
        dataset_update = {
            "datasets": {
                "interaction": "new_interaction_dataset_id",
                "metadata": "new_metadata_dataset_id"
            },
            "custom_config": {"batch_size": 1000}
        }
        success = update_pipeline_properties(client, pipeline_id, dataset_update)
        
        if not success:
            print("❌ Dataset update failed, skipping other examples")
            return
        
        print()
        
        # Example 3: Add complex nested properties
        print("📋 Example 3: Adding complex nested properties")
        complex_update = {
            "advanced_config": {
                "processing": {
                    "batch_size": 500,
                    "timeout": 300,
                    "retry_attempts": 3
                },
                "monitoring": {
                    "enabled": True,
                    "alert_threshold": 0.8
                }
            },
            "tags": ["production", "updated", "v2"]
        }
        success = update_pipeline_properties(client, pipeline_id, complex_update)
        
        print()
        
        # Final status check
        print("🔹 FINAL STATUS CHECK")
        print("=" * 30)
        final_pipeline = client.pipelines.get(pipeline_id)
        print(f"Pipeline: {final_pipeline.pipeline_name}")
        print(f"Status: {final_pipeline.status}")
        print(f"Properties: {final_pipeline.properties}")
        
        print("\n🎉 Pipeline update examples completed!")
        print("\nKey takeaways:")
        print("1. ✅ Pipeline updates are asynchronous - monitor status")
        print("2. ✅ Properties are merged, not replaced")
        print("3. ✅ Complex nested properties are supported")
        print("4. ✅ Always check final status after updates")
        print("5. ✅ Updates may take a few seconds to process")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


def main():
    """Run the pipeline update examples."""
    print("🚀 Rose Python SDK - Update Pipeline Example")
    print("=" * 60)
    print("Demonstrating how to update pipeline properties")
    print()
    
    demonstrate_property_updates()


if __name__ == "__main__":
    main()
