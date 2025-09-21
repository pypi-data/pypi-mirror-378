#!/usr/bin/env python3
"""
Basic Record Ingestion Examples

Simple examples showing how to ingest records into datasets.
No API access required - these examples demonstrate the record concepts.
"""

from rose_sdk.models.record import Record, Records


def show_record_models():
    """Show how to work with record models."""
    print("🔹 RECORD MODELS")
    print("=" * 40)
    
    # Create sample interaction records
    interaction_records = [
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
            "user_id": "user_001", 
            "item_id": "video_001",
            "item_type": "video",
            "play_amount_second": 45,
            "interaction": "pause",
            "client_upload_timestamp": 1705123500,
            "server_upload_timestamp": 1705123505
        }
    ]
    
    print("📋 Sample Interaction Records:")
    for i, record_data in enumerate(interaction_records, 1):
        print(f"   Record {i}:")
        for field, value in record_data.items():
            print(f"     {field}: {value}")
        print()
    
    # Create sample metadata records
    metadata_records = [
        {
            "item_id": "song_001",
            "item_type": "music",
            "content_rating": "PG",
            "name": "Amazing Song",
            "description": "A beautiful melody that touches the heart",
            "expire_timestamp": 1735680000,
            "publish_timestamp": 1704000000,
            "artists": ["Artist One", "Artist Two"],
            "genres": ["Pop", "Rock"]
        },
        {
            "item_id": "video_001",
            "item_type": "video", 
            "content_rating": "G",
            "name": "Funny Cat Video",
            "description": "Cute cats doing funny things",
            "expire_timestamp": None,
            "publish_timestamp": 1704000000,
            "artists": ["Video Creator"],
            "genres": ["Comedy", "Animals"]
        }
    ]
    
    print("📋 Sample Metadata Records:")
    for i, record_data in enumerate(metadata_records, 1):
        print(f"   Record {i}:")
        for field, value in record_data.items():
            if field in ["artists", "genres"]:
                print(f"     {field}: {value} (list)")
            else:
                print(f"     {field}: {value}")
        print()


def show_record_creation():
    """Show how to create Record objects."""
    print("🔹 RECORD CREATION")
    print("=" * 40)
    
    # Create individual records
    interaction_record = Record(
        user_id="user_002",
        item_id="podcast_001",
        item_type="podcast",
        play_amount_second=300,
        interaction="complete",
        client_upload_timestamp=1705123600,
        server_upload_timestamp=1705123605
    )
    
    print("📋 Individual Record:")
    print(f"   Type: {type(interaction_record)}")
    print(f"   Data: {interaction_record}")
    print()
    
    # Create a collection of records
    records_data = [
        {
            "user_id": "user_003",
            "item_id": "movie_001", 
            "item_type": "movie",
            "play_amount_second": 7200,
            "interaction": "play",
            "client_upload_timestamp": 1705123700,
            "server_upload_timestamp": 1705123705
        },
        {
            "user_id": "user_003",
            "item_id": "movie_001",
            "item_type": "movie", 
            "play_amount_second": 0,
            "interaction": "stop",
            "client_upload_timestamp": 1705123800,
            "server_upload_timestamp": 1705123805
        }
    ]
    
    records = Records(records=[Record(**data) for data in records_data])
    
    print("📋 Records Collection:")
    print(f"   Type: {type(records)}")
    print(f"   Count: {len(records.records)}")
    print(f"   Records: {records.records}")
    print()


def show_data_validation():
    """Show data validation concepts."""
    print("🔹 DATA VALIDATION")
    print("=" * 40)
    
    # Valid interaction record
    valid_record = {
        "user_id": "user_004",
        "item_id": "book_001",
        "item_type": "book",
        "play_amount_second": 0,  # 0 for non-media items
        "interaction": "view",
        "client_upload_timestamp": 1705123900,
        "server_upload_timestamp": 1705123905
    }
    
    print("📋 Valid Record:")
    print(f"   All required fields present: ✅")
    print(f"   Correct data types: ✅")
    print(f"   Valid timestamps: ✅")
    print()
    
    # Invalid record examples
    invalid_examples = [
        {
            "issue": "Missing required field",
            "record": {
                "user_id": "user_005",
                "item_id": "item_001",
                # Missing item_type, play_amount_second, etc.
            }
        },
        {
            "issue": "Wrong data type",
            "record": {
                "user_id": "user_006",
                "item_id": "item_002",
                "item_type": "music",
                "play_amount_second": "not_a_number",  # Should be int
                "interaction": "play",
                "client_upload_timestamp": 1705124000,
                "server_upload_timestamp": 1705124005
            }
        },
        {
            "issue": "Missing identifier field",
            "record": {
                # Missing user_id (identifier)
                "item_id": "item_003",
                "item_type": "music",
                "play_amount_second": 120,
                "interaction": "play",
                "client_upload_timestamp": 1705124100,
                "server_upload_timestamp": 1705124105
            }
        }
    ]
    
    print("📋 Invalid Record Examples:")
    for example in invalid_examples:
        print(f"   Issue: {example['issue']}")
        print(f"   Record: {example['record']}")
        print()


def show_ingestion_patterns():
    """Show common data ingestion patterns."""
    print("🔹 INGESTION PATTERNS")
    print("=" * 40)
    
    patterns = [
        {
            "name": "Single Record Ingestion",
            "description": "Add one record at a time",
            "use_case": "Real-time data streaming",
            "example": "User clicks play button"
        },
        {
            "name": "Batch Ingestion", 
            "description": "Add multiple records together",
            "use_case": "Bulk data import",
            "example": "Daily data sync from external system"
        },
        {
            "name": "Incremental Ingestion",
            "description": "Add only new or changed records",
            "use_case": "Efficient data updates",
            "example": "Sync only new user interactions"
        },
        {
            "name": "Full Refresh Ingestion",
            "description": "Replace all existing data",
            "use_case": "Complete data reload",
            "example": "Monthly metadata refresh"
        }
    ]
    
    for pattern in patterns:
        print(f"📋 {pattern['name']}:")
        print(f"   Description: {pattern['description']}")
        print(f"   Use case: {pattern['use_case']}")
        print(f"   Example: {pattern['example']}")
        print()


def show_record_examples():
    """Show example records for different scenarios."""
    print("🔹 RECORD EXAMPLES")
    print("=" * 40)
    
    # Music streaming example
    music_interactions = [
        {
            "user_id": "user_music_001",
            "item_id": "song_pop_001",
            "item_type": "music",
            "play_amount_second": 240,
            "interaction": "play",
            "client_upload_timestamp": 1705124200,
            "server_upload_timestamp": 1705124205
        },
        {
            "user_id": "user_music_001",
            "item_id": "song_rock_001", 
            "item_type": "music",
            "play_amount_second": 180,
            "interaction": "skip",
            "client_upload_timestamp": 1705124300,
            "server_upload_timestamp": 1705124305
        }
    ]
    
    print("📋 Music Streaming Interactions:")
    for record in music_interactions:
        print(f"   User {record['user_id']} {record['interaction']}ed {record['item_id']} for {record['play_amount_second']}s")
    print()
    
    # Video content example
    video_metadata = {
        "item_id": "video_tutorial_001",
        "item_type": "video",
        "content_rating": "PG-13",
        "name": "Python Programming Tutorial",
        "description": "Learn Python basics in 30 minutes",
        "expire_timestamp": None,
        "publish_timestamp": 1704000000,
        "artists": ["Tech Instructor", "Code Academy"],
        "genres": ["Education", "Programming", "Technology"]
    }
    
    print("📋 Video Content Metadata:")
    print(f"   Title: {video_metadata['name']}")
    print(f"   Description: {video_metadata['description']}")
    print(f"   Artists: {', '.join(video_metadata['artists'])}")
    print(f"   Genres: {', '.join(video_metadata['genres'])}")
    print()


def main():
    """Run all basic record ingestion examples."""
    print("🚀 Rose Python SDK - Basic Record Ingestion Examples")
    print("=" * 60)
    print("These examples show the core record concepts and data ingestion patterns.")
    print("No API access required - just run and learn!")
    print()
    
    show_record_models()
    show_record_creation()
    show_data_validation()
    show_ingestion_patterns()
    show_record_examples()
    
    print("🎉 Basic record ingestion examples completed!")
    print("\nNext steps:")
    print("1. Try the API examples to ingest real records")
    print("2. Experiment with different record formats")
    print("3. Use these patterns in your own applications")


if __name__ == "__main__":
    main()
