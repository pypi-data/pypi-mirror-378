#!/usr/bin/env python3
# quick_migration.py - Quick migration to add missing columns
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.db_setup import DATABASE_URL


async def add_missing_columns():
    """Add missing columns to existing tables"""
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("🔧 Adding missing columns to users table...")

    alter_statements = [
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS email VARCHAR(255),
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL,
        ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL,
        ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
        """,
        """
        ALTER TABLE user_databases
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
        """
    ]

    async with async_session() as session:
        for statement in alter_statements:
            try:
                await session.execute(text(statement))
                await session.commit()
                print("✅ Columns added successfully")
            except Exception as e:
                print(f"⚠️  Warning: {e}")
                await session.rollback()

    await engine.dispose()
    print("✅ Migration completed!")


if __name__ == "__main__":
    asyncio.run(add_missing_columns())