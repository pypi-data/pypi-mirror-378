#!/usr/bin/env python3
"""
Quick test of AccessNode SDK functionality
"""
import asyncio
import os
from dotenv import load_dotenv
from accessnode import AccessNode

# Load environment variables
load_dotenv()

async def test_sdk():
    """Test basic AccessNode SDK functionality"""
    print("🔄 Testing AccessNode SDK...")

    try:
        # Create AccessNode instance
        db = AccessNode(
            db_type="postgresql",
            database_name=os.getenv('POSTGRES_DB', 'accessnode_main'),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            username=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

        print("✅ AccessNode instance created")

        # Initialize the connection
        await db.initialize()
        print("✅ Database connection initialized")

        # Test raw query
        print("\n🔄 Testing raw query...")
        version_result = await db.raw_query("SELECT version() as db_version;")
        print(f"✅ Database version: {version_result[0]['db_version'][:50]}...")

        # Create test table
        print("\n🔄 Creating test table...")
        await db.raw_query("""
            CREATE TABLE IF NOT EXISTS sdk_test (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Test table created")

        # Test insert
        print("\n🔄 Testing insert operation...")
        test_id = await db.insert("sdk_test", {
            "name": "SDK Test Entry",
            "value": 42
        })
        print(f"✅ Inserted record with ID: {test_id}")

        # Test select
        print("\n🔄 Testing select operation...")
        record = await db.get("sdk_test", {"id": test_id})
        print(f"✅ Retrieved record: {record['name']} with value {record['value']}")

        # Test select all
        print("\n🔄 Testing select all...")
        all_records = await db.get_all("sdk_test")
        print(f"✅ Found {len(all_records)} records in test table")

        # Test update
        print("\n🔄 Testing update operation...")
        await db.update("sdk_test", {"id": test_id}, {"value": 100})
        updated_record = await db.get("sdk_test", {"id": test_id})
        print(f"✅ Updated record value to: {updated_record['value']}")

        # Clean up
        await db.close()
        print("\n✅ SDK test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ SDK Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_sdk())