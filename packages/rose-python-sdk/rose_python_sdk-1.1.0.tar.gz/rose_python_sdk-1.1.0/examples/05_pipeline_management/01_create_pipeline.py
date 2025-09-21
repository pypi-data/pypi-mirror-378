#!/usr/bin/env python3
"""
Create Pipeline Example

Example showing how to create a reflex pipeline using the Rose Python SDK.
"""

import os
from rose_sdk import RoseClient
from rose_sdk.utils.pipeline import (
    create_pipeline,
    create_realtime_leaderboard_pipeline, 
    PipelineBuilder,
    get_supported_scenarios
)
from typing import List

def find_datasets(client: RoseClient, dataset_names: List[str]):
    """Find datasets by name."""
    print("🔹 FINDING DATASETS")
    print("=" * 40)
    
    datasets = client.datasets.list()
    found_datasets = {}
    
    for dataset in datasets:
        if dataset.dataset_name in dataset_names:
            found_datasets[dataset.dataset_name] = dataset.dataset_name
            print(f"📋 Found {dataset.dataset_name}: {dataset.dataset_id}")
    
    missing_datasets = set(dataset_names) - set(found_datasets.keys())
    if missing_datasets:
        print(f"❌ Missing datasets: {missing_datasets}")
        return None
    
    print()
    return found_datasets


def create_pipeline_simple(client:RoseClient, account_id, pipeline_name, scenario, dataset_mapping):
    """Create pipeline using the simple helper function."""
    print(f"🔹 CREATING {scenario.upper()} PIPELINE (SIMPLE)")
    print("=" * 40)
    
    # Create pipeline configuration
    pipeline_config = create_pipeline(
        account_id=account_id,
        pipeline_name=pipeline_name,
        scenario=scenario,
        dataset_mapping=dataset_mapping,
        extra_key="extra_value"
    )
    
    print(f"📋 Pipeline configuration:")
    print(f"   Account ID: {pipeline_config['account_id']}")
    print(f"   Pipeline Name: {pipeline_config['pipeline_name']}")
    print(f"   Scenario: {pipeline_config['properties']['scenario']}")
    print(f"   Datasets: {pipeline_config['properties']['datasets']}")
    
    print()
    
    # Create the pipeline
    try:
        response = client.pipelines.create(
            name=pipeline_config["pipeline_name"],
            properties=pipeline_config["properties"]
        )
        
        print(f"✅ Pipeline created successfully!")
        print(f"   Pipeline ID: {response.pipeline_id}")
        return response.pipeline_id
        
    except Exception as e:
        print(f"❌ Failed to create pipeline: {e}")
        return None



def list_pipelines(client:RoseClient):
    """List all pipelines."""
    print("🔹 LISTING PIPELINES")
    print("=" * 40)
    
    try:
        pipelines = client.pipelines.list()
        
        if not pipelines:
            print("📋 No pipelines found")
            return
        
        print(f"📋 Found {len(pipelines)} pipeline(s):")
        for pipeline in pipelines:
            print(f"   {pipeline.pipeline_name} (ID: {pipeline.pipeline_id})")
            print(f"      Account: {pipeline.account_id}")
            print(f"      Status: {pipeline.status}")
            print()
        
    except Exception as e:
        print(f"❌ Failed to list pipelines: {e}")


def show_scenario_info():
    """Show information about supported scenarios."""
    print("🔹 SUPPORTED SCENARIOS")
    print("=" * 40)
    
    scenarios = get_supported_scenarios()
    for scenario_name, info in scenarios.items():
        print(f"📋 {scenario_name.upper()}")
        print(f"   Description: {info['description']}")
        print(f"   Required Datasets: {', '.join(info['dataset_keys'])}")
        print()


def main():
    """Create a pipeline for the luli account."""
    print("🚀 Rose Python SDK - Create Pipeline Example")
    print("=" * 60)
    print("Creating a pipeline for the luli account")
    print()
    
    # Show supported scenarios
    show_scenario_info()
    
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
        
        # Find the required datasets for realtime_leaderboard scenario
        # Note: We need to find user datasets and map them to pipeline dataset keys
        required_datasets = find_datasets(client, ["interaction", "metadata"])
        if not required_datasets:
            print("❌ Required datasets not found. Please create them first.")
            print("   Required datasets for realtime_leaderboard: interaction, metadata")
            return
        
        # Map user datasets to pipeline dataset keys
        # In this case, the user dataset names match the pipeline keys
        dataset_mapping = {
            "interaction": required_datasets["interaction"],
            "metadata": required_datasets["metadata"]
        }
        
        # Create pipeline using simple method
        pipeline_id = create_pipeline_simple(
            client=client,
            account_id="luli",
            pipeline_name="realtime-leaderboard-pipeline",
            scenario="realtime_leaderboard",
            dataset_mapping=dataset_mapping
        )
        
        if pipeline_id:
            print("🎉 Pipeline creation completed!")
            
            # List all pipelines to confirm
            list_pipelines(client)
            
            print("\nKey takeaways:")
            print("1. Use create_pipeline() for simple setup - only need scenario and datasets")
            print("2. Queries and reflexes are automatically configured based on scenario")
            print("3. Use PipelineBuilder for advanced configuration")
            print("4. Pipelines are created asynchronously via Lambda")
    
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
