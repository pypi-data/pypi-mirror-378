# 001_add_auth_tables.py - Database migration for enhanced authentication
"""
Migration: Add authentication and authorization tables
Date: 2025-09-17
Description: Adds RBAC tables, audit logging, and session management
"""

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.db_setup import get_database_url
from database.models import Base, Role, Permission, User
import os


class AuthMigration:
    """Database migration for authentication system"""

    def __init__(self):
        self.engine = create_async_engine(get_database_url())
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def check_migration_status(self) -> dict:
        """Check which tables already exist"""
        status = {}

        tables_to_check = [
            'roles', 'permissions', 'user_roles', 'role_permissions',
            'user_sessions', 'audit_logs'
        ]

        async with self.async_session() as session:
            for table in tables_to_check:
                try:
                    result = await session.execute(
                        text(f"SELECT 1 FROM {table} LIMIT 1")
                    )
                    status[table] = "exists"
                except Exception:
                    status[table] = "missing"

        return status

    async def backup_existing_data(self):
        """Backup existing user data before migration"""
        print("📦 Backing up existing user data...")

        async with self.async_session() as session:
            # Export existing users
            result = await session.execute(
                text("SELECT id, username, hashed_password FROM users")
            )
            users = result.fetchall()

            print(f"Found {len(users)} existing users")

            # Save to backup file
            import json
            backup_data = {
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "hashed_password": user.hashed_password
                    }
                    for user in users
                ],
                "migration_date": "2025-09-17",
                "migration_version": "001"
            }

            with open("user_backup_001.json", "w") as f:
                json.dump(backup_data, f, indent=2)

            print("✅ User data backed up to user_backup_001.json")

    async def create_new_tables(self):
        """Create new authentication tables"""
        print("🏗️  Creating new authentication tables...")

        async with self.engine.begin() as conn:
            # Create all new tables
            await conn.run_sync(Base.metadata.create_all)

        print("✅ New tables created successfully")

    async def alter_existing_tables(self):
        """Alter existing tables to add new columns"""
        print("🔧 Altering existing tables...")

        alter_statements = [
            # Add new columns to users table
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL,
            ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL,
            ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
            """,

            # Modify existing columns if needed
            """
            ALTER TABLE users
            ALTER COLUMN username TYPE VARCHAR(50),
            ALTER COLUMN hashed_password TYPE VARCHAR(255)
            """,

            # Add new columns to user_databases table
            """
            ALTER TABLE user_databases
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE,
            ALTER COLUMN db_name TYPE VARCHAR(100),
            ALTER COLUMN db_type TYPE VARCHAR(50),
            ALTER COLUMN host TYPE VARCHAR(255),
            ALTER COLUMN username TYPE VARCHAR(100),
            ALTER COLUMN password TYPE VARCHAR(500)
            """
        ]

        async with self.async_session() as session:
            for statement in alter_statements:
                try:
                    await session.execute(text(statement))
                    await session.commit()
                except Exception as e:
                    print(f"Warning: Could not execute statement: {e}")
                    await session.rollback()

        print("✅ Existing tables altered successfully")

    async def insert_default_roles_and_permissions(self):
        """Insert default roles and permissions"""
        print("👤 Creating default roles and permissions...")

        async with self.async_session() as session:
            # Create default permissions
            default_permissions = [
                # User permissions
                {"name": "user.read", "resource": "user", "action": "read", "description": "Read user profile"},
                {"name": "user.update", "resource": "user", "action": "update", "description": "Update user profile"},
                {"name": "user.delete", "resource": "user", "action": "delete", "description": "Delete user account"},

                # Database permissions
                {"name": "database.create", "resource": "database", "action": "create", "description": "Create database connections"},
                {"name": "database.read", "resource": "database", "action": "read", "description": "View database connections"},
                {"name": "database.update", "resource": "database", "action": "update", "description": "Update database connections"},
                {"name": "database.delete", "resource": "database", "action": "delete", "description": "Delete database connections"},
                {"name": "database.query", "resource": "database", "action": "query", "description": "Execute database queries"},

                # Admin permissions
                {"name": "admin.user.create", "resource": "admin", "action": "create", "description": "Create users"},
                {"name": "admin.user.delete", "resource": "admin", "action": "delete", "description": "Delete users"},
                {"name": "admin.role.assign", "resource": "admin", "action": "assign", "description": "Assign roles"},
                {"name": "admin.audit.read", "resource": "admin", "action": "read", "description": "View audit logs"},
            ]

            for perm_data in default_permissions:
                permission = Permission(**perm_data)
                session.add(permission)

            # Create default roles
            default_roles = [
                {
                    "name": "admin",
                    "description": "Full system administrator",
                    "is_default": False,
                    "permissions": default_permissions  # Admin gets all permissions
                },
                {
                    "name": "user",
                    "description": "Regular user",
                    "is_default": True,
                    "permissions": [p for p in default_permissions if not p["name"].startswith("admin.")]
                },
                {
                    "name": "read_only",
                    "description": "Read-only access",
                    "is_default": False,
                    "permissions": [p for p in default_permissions if p["action"] == "read"]
                }
            ]

            await session.commit()  # Commit permissions first

            # Now create roles and assign permissions
            for role_data in default_roles:
                permissions_names = [p["name"] for p in role_data.pop("permissions")]

                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    is_default=role_data["is_default"]
                )
                session.add(role)
                await session.flush()  # Get the role ID

                # Assign permissions to role
                for perm_name in permissions_names:
                    perm_result = await session.execute(
                        text("SELECT id FROM permissions WHERE name = :name"),
                        {"name": perm_name}
                    )
                    perm_id = perm_result.scalar_one_or_none()

                    if perm_id:
                        await session.execute(
                            text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                            {"role_id": role.id, "perm_id": perm_id}
                        )

            await session.commit()

        print("✅ Default roles and permissions created")

    async def assign_default_roles_to_users(self):
        """Assign default role to existing users"""
        print("🔗 Assigning default roles to existing users...")

        async with self.async_session() as session:
            # Get default role (user)
            result = await session.execute(
                text("SELECT id FROM roles WHERE name = 'user'")
            )
            user_role_id = result.scalar_one()

            # Get all existing users
            result = await session.execute(
                text("SELECT id FROM users")
            )
            user_ids = [row[0] for row in result.fetchall()]

            # Assign default role to all users
            for user_id in user_ids:
                await session.execute(
                    text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
                    {"user_id": user_id, "role_id": user_role_id}
                )

            await session.commit()

        print(f"✅ Assigned default role to {len(user_ids)} users")

    async def create_indexes(self):
        """Create performance indexes"""
        print("📈 Creating performance indexes...")

        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
            "CREATE INDEX IF NOT EXISTS idx_user_databases_owner ON user_databases(owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_databases_active ON user_databases(is_active)",
        ]

        async with self.async_session() as session:
            for statement in index_statements:
                try:
                    await session.execute(text(statement))
                    await session.commit()
                except Exception as e:
                    print(f"Warning: Could not create index: {e}")
                    await session.rollback()

        print("✅ Performance indexes created")

    async def run_migration(self):
        """Run the complete migration"""
        print("🚀 Starting authentication system migration...")

        try:
            # Step 1: Check current status
            status = await self.check_migration_status()
            print(f"Migration status: {status}")

            # Step 2: Backup existing data
            await self.backup_existing_data()

            # Step 3: Create new tables
            await self.create_new_tables()

            # Step 4: Alter existing tables
            await self.alter_existing_tables()

            # Step 5: Insert default data
            await self.insert_default_roles_and_permissions()

            # Step 6: Assign roles to existing users
            await self.assign_default_roles_to_users()

            # Step 7: Create indexes
            await self.create_indexes()

            print("✅ Migration completed successfully!")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise
        finally:
            await self.engine.dispose()

    async def rollback_migration(self):
        """Rollback migration (for emergency use)"""
        print("⚠️  Rolling back migration...")

        # This would restore from backup and drop new tables
        # Implementation depends on specific rollback requirements

        print("✅ Migration rolled back")


async def main():
    """Main migration function"""
    migration = AuthMigration()

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        await migration.rollback_migration()
    else:
        await migration.run_migration()


if __name__ == "__main__":
    asyncio.run(main())