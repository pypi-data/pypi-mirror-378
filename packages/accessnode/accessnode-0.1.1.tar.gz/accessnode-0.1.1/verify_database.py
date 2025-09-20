#!/usr/bin/env python3
"""
Verify database setup and data
"""
import asyncio
import os
from dotenv import load_dotenv
from accessnode import AccessNode

# Load environment variables
load_dotenv()

async def verify_database():
    """Verify database setup and show all data"""
    print("🔍 Verifying AccessNode Database Setup")
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

        # Check database connection
        print("📊 Database Information:")
        db_info = db.raw_query("SELECT version(), current_database(), current_user;")
        print(f"   Database: {db_info[0]['current_database']}")
        print(f"   User: {db_info[0]['current_user']}")
        print(f"   Version: {db_info[0]['version'][:60]}...")

        # List all tables
        print("\n📋 Tables in Database:")
        tables = db.raw_query("""
            SELECT
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        for table in tables:
            print(f"   - {table['table_name']} ({table['table_type']})")

        # Check users table
        print("\n👥 Users Table:")
        users = db.raw_query("SELECT id, username FROM users ORDER BY id;")
        if users:
            for user in users:
                print(f"   - ID: {user['id']}, Username: {user['username']}")
        else:
            print("   - No users found")

        # Check user_databases table
        print("\n💾 User Databases Table:")
        user_dbs = db.raw_query("""
            SELECT
                id, db_name, db_type, host, port, username,
                CASE
                    WHEN password IS NOT NULL THEN '[ENCRYPTED]'
                    ELSE '[NULL]'
                END as password_status,
                owner_id
            FROM user_databases
            ORDER BY id;
        """)
        if user_dbs:
            for udb in user_dbs:
                print(f"   - ID: {udb['id']}, Name: {udb['db_name']}, Type: {udb['db_type']}")
                print(f"     Host: {udb['host']}:{udb['port']}, User: {udb['username']}")
                print(f"     Password: {udb['password_status']}, Owner: {udb['owner_id']}")
        else:
            print("   - No database connections found")

        # Check test tables
        print("\n🧪 Test Tables:")

        # Check simple_test table
        simple_test = db.raw_query("SELECT COUNT(*) as count FROM simple_test;")
        print(f"   - simple_test: {simple_test[0]['count']} records")

        if simple_test[0]['count'] > 0:
            sample_data = db.raw_query("SELECT * FROM simple_test LIMIT 3;")
            for row in sample_data:
                print(f"     * {row['name']}: {row['value']}")

        # Check sdk_test table if it exists
        try:
            sdk_test = db.raw_query("SELECT COUNT(*) as count FROM sdk_test;")
            print(f"   - sdk_test: {sdk_test[0]['count']} records")
        except Exception:
            print("   - sdk_test: table not found")

        # Database size and stats
        print("\n📊 Database Statistics:")
        stats = db.raw_query("""
            SELECT
                pg_database.datname as database_name,
                pg_size_pretty(pg_database_size(pg_database.datname)) as size
            FROM pg_database
            WHERE pg_database.datname = current_database();
        """)
        print(f"   - Database size: {stats[0]['size']}")

        # Connection info
        connections = db.raw_query("""
            SELECT count(*) as active_connections
            FROM pg_stat_activity
            WHERE datname = current_database();
        """)
        print(f"   - Active connections: {connections[0]['active_connections']}")

        print("\n✅ Database verification completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Verification Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_database())
    if success:
        print("\n🎉 Database is properly set up and working!")
    else:
        print("\n⚠️  There were some issues with the database verification.")