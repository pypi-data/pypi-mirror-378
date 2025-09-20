#!/usr/bin/env python3
"""
AccessNode Database Provisioning Demo

This demonstrates how users can instantly provision databases of any type
for quick development without setting up database servers.
"""

import asyncio
import sys
sys.path.append('.')

from accessnode.services.database_provisioner import DatabaseProvisioningService


async def demo_sqlite_provisioning():
    """Demo SQLite provisioning - instant, no server needed."""
    print("🗃️  SQLITE PROVISIONING DEMO")
    print("=" * 50)

    provisioner = DatabaseProvisioningService(base_data_dir='/tmp/accessnode_demo')

    # Provision SQLite database
    result = await provisioner.provision_sqlite(
        user_id=12345,
        db_name="hackathon_project"
    )

    print("✅ Database provisioned instantly!")
    print(f"📁 Database file: {result['database_path']}")
    print(f"🔗 Connection string: {result['connection_string']}")

    # Show how to use it with AccessNode
    print("\n💻 Usage with AccessNode SDK:")
    print(f"""
from accessnode import AccessNode

db = AccessNode(
    db_type="sqlite",
    database_name="{result['database_path']}",
    host="localhost"
)
await db.initialize()

# Ready to use!
users = await db.get_all("users")
print(users)  # Shows welcome data
""")

    return result


async def demo_postgresql_provisioning():
    """Demo PostgreSQL provisioning with Docker."""
    print("\n🐘 POSTGRESQL PROVISIONING DEMO")
    print("=" * 50)

    provisioner = DatabaseProvisioningService(base_data_dir='/tmp/accessnode_demo')

    try:
        # This requires Docker to be running
        result = await provisioner.provision_postgresql(
            user_id=12345,
            db_name="my_postgres_db"
        )

        print("✅ PostgreSQL container started!")
        print(f"🌐 Host: {result['host']}")
        print(f"🔌 Port: {result['port']}")
        print(f"👤 Username: {result['username']}")
        print(f"🔗 Connection: {result['connection_string']}")
        print(f"🐳 Container: {result['container_name']}")

        print("\n💻 Usage with AccessNode SDK:")
        print(f"""
from accessnode import AccessNode

db = AccessNode(
    db_type="postgresql",
    database_name="{result['db_name']}",
    username="{result['username']}",
    password="{result['password']}",
    host="{result['host']}",
    port={result['port']}
)
await db.initialize()

# Ready to use PostgreSQL!
await db.raw_query("CREATE TABLE products (id SERIAL PRIMARY KEY, name TEXT)")
""")

        return result

    except Exception as e:
        print(f"⚠️  PostgreSQL provisioning requires Docker: {e}")
        print("💡 To enable PostgreSQL provisioning:")
        print("   1. Install Docker Desktop")
        print("   2. Start Docker")
        print("   3. Run this demo again")
        return None


async def show_supported_databases():
    """Show all supported database types."""
    print("\n🗄️  SUPPORTED DATABASE TYPES")
    print("=" * 50)

    databases = [
        {
            "name": "SQLite",
            "type": "sqlite",
            "description": "File-based, instant setup",
            "requirements": "None",
            "best_for": "Development, prototyping, demos"
        },
        {
            "name": "PostgreSQL",
            "type": "postgresql",
            "description": "Advanced relational database",
            "requirements": "Docker",
            "best_for": "Production apps, complex queries"
        },
        {
            "name": "MySQL",
            "type": "mysql",
            "description": "Popular relational database",
            "requirements": "Docker",
            "best_for": "Web applications, WordPress"
        },
        {
            "name": "MongoDB",
            "type": "mongodb",
            "description": "Document-oriented NoSQL",
            "requirements": "Docker",
            "best_for": "JSON data, flexible schemas"
        }
    ]

    for db in databases:
        print(f"📊 {db['name']} ({db['type']})")
        print(f"   {db['description']}")
        print(f"   Requirements: {db['requirements']}")
        print(f"   Best for: {db['best_for']}")
        print()


async def main():
    """Run the complete provisioning demo."""
    print("🚀 ACCESSNODE DATABASE PROVISIONING DEMO")
    print("=" * 60)
    print("Provision any database type instantly for quick development!")
    print()

    # Show supported types
    await show_supported_databases()

    # Demo SQLite (always works)
    sqlite_result = await demo_sqlite_provisioning()

    # Demo PostgreSQL (requires Docker)
    postgres_result = await demo_postgresql_provisioning()

    print("\n🎯 QUICK START SUMMARY")
    print("=" * 30)
    print("✅ SQLite: Ready to use (no dependencies)")
    if postgres_result:
        print("✅ PostgreSQL: Container running")
    else:
        print("⚠️  PostgreSQL: Requires Docker")

    print("\n🔥 For hackathons and quick projects:")
    print("   • Use SQLite for instant database")
    print("   • Use PostgreSQL for production-like testing")
    print("   • All databases come with sample schemas")
    print("   • Connection details provided automatically")

    print(f"\n💾 Your databases are stored in: /tmp/accessnode_demo")
    print("🌐 API endpoints available at: /provision/*")


if __name__ == "__main__":
    asyncio.run(main())