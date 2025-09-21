#!/usr/bin/env python3
"""
List Pipeline Queries Example

Example showing how to list queries from a pipeline using the Rose Python SDK.
Only works for pipelines with status "CREATE SUCCESSFUL".
"""

import os
from rose_sdk import RoseClient


def main():
    """List queries from a successful pipeline."""
    print("🚀 Rose Python SDK - List Pipeline Queries Example")
    print("=" * 60)
    print("Listing queries from a successful pipeline")
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
        
        # List all pipelines
        print("🔹 LISTING PIPELINES")
        print("=" * 30)
        pipelines = client.pipelines.list()
        
        if not pipelines:
            print("📋 No pipelines found.")
            return
        
        print(f"📋 Found {len(pipelines)} pipeline(s):")
        for i, pipeline in enumerate(pipelines, 1):
            print(f"   {i}. {pipeline.pipeline_name} (ID: {pipeline.pipeline_id})")
            print(f"      Status: {pipeline.status}")
        print()
        
        # Find a successful pipeline
        successful_pipeline = None
        for pipeline in pipelines:
            if pipeline.status == "CREATE SUCCESSFUL":
                successful_pipeline = pipeline
                break
        
        if not successful_pipeline:
            print("❌ No pipelines with status 'CREATE SUCCESSFUL' found.")
            print("   Pipeline must be successfully created before listing queries.")
            return
        
        print(f"🎯 Selected successful pipeline:")
        print(f"   Name: {successful_pipeline.pipeline_name}")
        print(f"   ID: {successful_pipeline.pipeline_id}")
        print(f"   Status: {successful_pipeline.status}")
        print()
        
        # List queries from the successful pipeline
        print("🔹 LISTING PIPELINE QUERIES")
        print("=" * 40)
        print("📤 Fetching queries...")
        
        try:
            queries = client.pipelines.list_queries(successful_pipeline.pipeline_id)
            
            if not queries:
                print("📋 No queries found for this pipeline.")
            else:
                print(f"📋 Found {len(queries)} query/queries:")
                for i, query in enumerate(queries, 1):
                    print(f"   {i}. Query ID: {query.query_id}")
                    print(f"      Name: {query.query_name}")
                    print(f"      Type: {query.query_type}")
                    print(f"      Status: {query.status}")
                    print()
            
        except ValueError as e:
            print(f"❌ Cannot list queries: {e}")
            return
        except Exception as e:
            print(f"❌ Error listing queries: {e}")
            return
        
        print("🎉 Query listing example completed!")
        print("\nKey takeaways:")
        print("1. ✅ Only pipelines with status 'CREATE SUCCESSFUL' can list queries")
        print("2. ✅ Use client.pipelines.list_queries(pipeline_id) to get queries")
        print("3. ✅ Check pipeline status before attempting to list queries")
        print("4. ✅ Queries are only available after successful pipeline creation")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
