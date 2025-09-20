#!/usr/bin/env python3
"""
Test script to verify local database connection to accessnode_main
"""
import asyncio
import os
from dotenv import load_dotenv
from accessnode import AccessNode

# Load environment variables
load_dotenv()

async def test_local_connection():
    """Test connection to local accessnode_main database"""
    print("🔄 Testing connection to local PostgreSQL database...")
    print(f"Database: {os.getenv('POSTGRES_DB', 'accessnode_main')}")
    print(f"Host: {os.getenv('POSTGRES_HOST', 'localhost')}")
    print(f"Port: {os.getenv('POSTGRES_PORT', '5432')}")
    print(f"User: {os.getenv('POSTGRES_USER', 'postgres')}")

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

        print("\n🔄 Initializing AccessNode connection...")
        await db.initialize()
        print("✅ AccessNode initialized successfully!")

        # Test basic database connectivity
        print("\n🔄 Testing database query...")
        result = await db.raw_query("SELECT version() as db_version;")
        print(f"✅ Database version: {result[0]['db_version']}")

        # Test table listing
        print("\n🔄 Listing existing tables...")
        tables_result = await db.raw_query("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)

        if tables_result:
            print("📋 Existing tables:")
            for table in tables_result:
                print(f"  - {table['table_name']}")
        else:
            print("📋 No tables found in public schema")

        print("\n🔄 Creating a test table...")
        await db.raw_query("""
            CREATE TABLE IF NOT EXISTS test_users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Test table 'test_users' created successfully!")

        # Test insert operation
        print("\n🔄 Testing insert operation...")
        user_id = await db.insert("test_users", {
            "name": "John Doe",
            "email": "john.doe@example.com"
        })
        print(f"✅ Inserted user with ID: {user_id}")

        # Test select operation
        print("\n🔄 Testing select operation...")
        users = await db.get_all("test_users")
        print(f"✅ Found {len(users)} users in test_users table")
        for user in users:
            print(f"  - {user['name']} ({user['email']})")

        # Clean up
        await db.close()
        print("\n✅ Database connection closed successfully!")
        print("\n🎉 All tests passed! Your local database is working correctly.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check that the 'accessnode_main' database exists in pgAdmin4")
        print("3. Verify your credentials in the .env file")
        print("4. Ensure the user has proper permissions")
        return False

    return True

async def setup_sample_data():
    """Set up some sample data for testing"""
    print("\n🔄 Setting up sample data...")

    try:
        db = AccessNode(
            db_type="postgresql",
            database_name=os.getenv('POSTGRES_DB', 'accessnode_main'),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            username=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

        await db.initialize()

        # Create products table
        await db.raw_query("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(100),
                in_stock BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Insert sample products
        sample_products = [
            {"name": "Laptop Pro", "price": 1299.99, "category": "Electronics"},
            {"name": "Wireless Mouse", "price": 29.99, "category": "Electronics"},
            {"name": "Office Chair", "price": 199.99, "category": "Furniture"},
            {"name": "Coffee Maker", "price": 89.99, "category": "Appliances"},
            {"name": "Python Programming Book", "price": 49.99, "category": "Books"}
        ]

        for product in sample_products:
            await db.insert("products", product)

        print("✅ Sample data created successfully!")
        print("📋 Created tables: test_users, products")

        await db.close()

    except Exception as e:
        print(f"❌ Error setting up sample data: {e}")

if __name__ == "__main__":
    async def main():
        success = await test_local_connection()
        if success:
            await setup_sample_data()
            print("\n🚀 Ready to start developing with AccessNode!")
            print("💡 You can now use the AccessNode SDK or API with your local database.")

    asyncio.run(main())