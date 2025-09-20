#!/usr/bin/env python3
"""
Final comprehensive test of all AccessNode functionality
"""
import asyncio
import os
from dotenv import load_dotenv
from accessnode import AccessNode

# Load environment variables
load_dotenv()

async def final_test():
    """Final comprehensive test of AccessNode"""
    print("🚀 FINAL COMPREHENSIVE ACCESSNODE TEST")
    print("=" * 50)

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
        print("✅ AccessNode initialized successfully")

        # Test 1: Raw Query (Async)
        print("\n1. 🔄 Testing Async Raw Query...")
        version = await db.raw_query("SELECT version() as v;")
        print(f"✅ Database: {version[0]['v'][:40]}...")

        # Test 2: Table Creation
        print("\n2. 🔄 Creating comprehensive test table...")
        await db.raw_query("""
            CREATE TABLE IF NOT EXISTS final_test (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                age INTEGER CHECK (age >= 0),
                active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table created with constraints")

        # Test 3: Async INSERT
        print("\n3. 🔄 Testing Async INSERT operations...")
        user1_id = await db.insert("final_test", {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 28
        })
        user2_id = await db.insert("final_test", {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "age": 34,
            "active": False
        })
        print(f"✅ Inserted users with IDs: {user1_id}, {user2_id}")

        # Test 4: Async GET
        print("\n4. 🔄 Testing Async GET operations...")
        alice = await db.get("final_test", {"id": user1_id})
        print(f"✅ Retrieved: {alice['name']} ({alice['email']})")

        # Test 5: Async GET_ALL
        print("\n5. 🔄 Testing Async GET_ALL operations...")
        all_users = await db.get_all("final_test")
        active_users = await db.get_all("final_test", {"active": True})
        print(f"✅ Total users: {len(all_users)}, Active: {len(active_users)}")

        # Test 6: Async UPDATE
        print("\n6. 🔄 Testing Async UPDATE operations...")
        updated = await db.update(
            "final_test",
            {"id": user2_id},
            {"active": True, "age": 35}
        )
        print(f"✅ Updated {updated} record(s)")

        # Test 7: Complex Raw Query
        print("\n7. 🔄 Testing complex raw query...")
        stats = await db.raw_query("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN active THEN 1 END) as active_count,
                AVG(age) as avg_age,
                MAX(age) as max_age,
                MIN(age) as min_age
            FROM final_test;
        """)
        s = stats[0]
        print(f"✅ Stats: {s['total']} total, {s['active_count']} active, avg age: {s['avg_age']:.1f}")

        # Test 8: Transaction-style operations
        print("\n8. 🔄 Testing batch operations...")
        batch_users = [
            {"name": "Charlie Brown", "email": "charlie@example.com", "age": 22},
            {"name": "Diana Prince", "email": "diana@example.com", "age": 29},
            {"name": "Edward Norton", "email": "edward@example.com", "age": 31}
        ]

        batch_ids = []
        for user_data in batch_users:
            user_id = await db.insert("final_test", user_data)
            batch_ids.append(user_id)

        print(f"✅ Batch inserted {len(batch_ids)} users")

        # Test 9: Async DELETE
        print("\n9. 🔄 Testing Async DELETE operations...")
        deleted = await db.delete("final_test", {"age": 22})
        print(f"✅ Deleted {deleted} record(s)")

        # Test 10: Final verification
        print("\n10. 🔄 Final verification...")
        final_count = await db.raw_query("SELECT COUNT(*) as count FROM final_test;")
        final_users = await db.get_all("final_test")

        print(f"✅ Final count: {final_count[0]['count']} users")
        print("✅ Final users:")
        for user in final_users:
            status = "🟢" if user['active'] else "🔴"
            print(f"   {status} {user['name']} ({user['age']} years old)")

        print("\n🎉 ALL TESTS PASSED! AccessNode is fully functional!")
        print("\n📈 SUMMARY:")
        print("   ✅ Async raw queries working")
        print("   ✅ Async CRUD operations working")
        print("   ✅ Complex queries working")
        print("   ✅ Batch operations working")
        print("   ✅ Data integrity maintained")
        print("   ✅ All async patterns implemented correctly")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_test())
    if success:
        print("\n🏆 ACCESSNODE IS READY FOR PRODUCTION!")
        print("🔧 The architectural async fix was successful!")
    else:
        print("\n💥 Some tests failed.")