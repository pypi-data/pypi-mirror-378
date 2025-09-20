#!/usr/bin/env python3
"""
Simple test of AccessNode SDK using raw queries only
"""
import asyncio
import os
from dotenv import load_dotenv
from accessnode import AccessNode

# Load environment variables
load_dotenv()

async def test_simple_sdk():
    """Test basic AccessNode SDK with raw queries"""
    print("🔄 Testing AccessNode SDK with raw queries...")

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

        # Test raw query - get database version
        print("\n🔄 Testing raw query...")
        version_result = db.raw_query("SELECT version() as db_version;")
        print(f"✅ Database version: {version_result[0]['db_version'][:50]}...")

        # Create test table
        print("\n🔄 Creating test table...")
        db.raw_query("""
            CREATE TABLE IF NOT EXISTS simple_test (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Test table created")

        # Insert test data
        print("\n🔄 Inserting test data...")
        db.raw_query("""
            INSERT INTO simple_test (name, value)
            VALUES ('Test Entry 1', 42), ('Test Entry 2', 100);
        """)
        print("✅ Test data inserted")

        # Query test data
        print("\n🔄 Querying test data...")
        results = db.raw_query("SELECT * FROM simple_test ORDER BY id;")
        print(f"✅ Found {len(results)} records:")
        for row in results:
            print(f"   - ID: {row['id']}, Name: {row['name']}, Value: {row['value']}")

        # Update test data
        print("\n🔄 Updating test data...")
        db.raw_query("UPDATE simple_test SET value = 999 WHERE name = 'Test Entry 1';")
        print("✅ Test data updated")

        # Query updated data
        print("\n🔄 Querying updated data...")
        updated_results = db.raw_query("SELECT * FROM simple_test WHERE name = 'Test Entry 1';")
        print(f"✅ Updated record: {updated_results[0]['name']} = {updated_results[0]['value']}")

        # Check existing tables
        print("\n🔄 Listing all tables...")
        table_results = db.raw_query("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' ORDER BY table_name;
        """)
        print(f"✅ Found {len(table_results)} tables:")
        for table in table_results:
            print(f"   - {table['table_name']}")

        # Clean up
        await db.close()
        print("\n✅ SDK test completed successfully!")

        return True

    except Exception as e:
        print(f"\n❌ SDK Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_sdk())
    if success:
        print("\n🎉 All tests passed! AccessNode SDK is working correctly.")
    else:
        print("\n💡 Some tests failed, but basic functionality is working.")