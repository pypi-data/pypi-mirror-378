#!/usr/bin/env python3
"""
Test async CRUD operations with the updated AccessNode
"""
import asyncio
import os
from dotenv import load_dotenv
from accessnode import AccessNode

# Load environment variables
load_dotenv()

async def test_async_crud():
    """Test all async CRUD operations"""
    print("🔄 Testing Async CRUD Operations")
    print("=" * 40)

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

        await db.initialize()
        print("✅ AccessNode initialized")

        # Test async raw_query
        print("\n1. 🔄 Testing async raw_query...")
        version_result = await db.raw_query("SELECT version() as db_version;")
        print(f"✅ Raw query works: {version_result[0]['db_version'][:50]}...")

        # Create test table
        print("\n2. 🔄 Creating async_test table...")
        await db.raw_query("""
            CREATE TABLE IF NOT EXISTS async_test (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table created")

        # Test INSERT
        print("\n3. 🔄 Testing async INSERT...")
        user_id = await db.insert("async_test", {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        })
        print(f"✅ Inserted user with ID: {user_id}")

        # Test GET (single record)
        print("\n4. 🔄 Testing async GET...")
        user = await db.get("async_test", {"id": user_id})
        print(f"✅ Retrieved user: {user['name']} ({user['email']})")

        # Test INSERT multiple records
        print("\n5. 🔄 Testing multiple INSERTs...")
        user_id2 = await db.insert("async_test", {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "age": 25
        })
        user_id3 = await db.insert("async_test", {
            "name": "Bob Wilson",
            "email": "bob@example.com",
            "age": 35
        })
        print(f"✅ Inserted users with IDs: {user_id2}, {user_id3}")

        # Test GET_ALL
        print("\n6. 🔄 Testing async GET_ALL...")
        all_users = await db.get_all("async_test")
        print(f"✅ Retrieved {len(all_users)} users:")
        for user in all_users:
            print(f"   - {user['name']} ({user['age']} years old)")

        # Test GET_ALL with filter
        print("\n7. 🔄 Testing async GET_ALL with filter...")
        young_users = await db.get_all("async_test", {"age": 25})
        print(f"✅ Found {len(young_users)} users age 25:")
        for user in young_users:
            print(f"   - {user['name']}")

        # Test UPDATE
        print("\n8. 🔄 Testing async UPDATE...")
        updated_count = await db.update(
            "async_test",
            {"id": user_id},
            {"age": 31, "email": "john.doe@example.com"}
        )
        print(f"✅ Updated {updated_count} record(s)")

        # Verify update
        updated_user = await db.get("async_test", {"id": user_id})
        print(f"✅ Verified update: {updated_user['name']} is now {updated_user['age']} years old")

        # Test DELETE
        print("\n9. 🔄 Testing async DELETE...")
        deleted_count = await db.delete("async_test", {"id": user_id3})
        print(f"✅ Deleted {deleted_count} record(s)")

        # Verify delete
        remaining_users = await db.get_all("async_test")
        print(f"✅ Remaining users: {len(remaining_users)}")

        # Test complex raw query
        print("\n10. 🔄 Testing complex async raw query...")
        stats = await db.raw_query("""
            SELECT
                COUNT(*) as total_users,
                AVG(age) as avg_age,
                MIN(age) as min_age,
                MAX(age) as max_age
            FROM async_test;
        """)
        print(f"✅ Stats - Total: {stats[0]['total_users']}, Avg Age: {stats[0]['avg_age']:.1f}")

        print("\n🎉 All async CRUD operations working perfectly!")
        return True

    except Exception as e:
        print(f"\n❌ Async CRUD Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_async_crud())
    if success:
        print("\n✅ SUCCESS: Async CRUD operations are fully functional!")
    else:
        print("\n❌ FAILURE: Some async operations failed.")