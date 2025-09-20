# tests/conftest_fixed.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from typing import AsyncGenerator
import asyncio
import asyncpg

# Import from the correct locations
from database.db_setup import Base
from database.models import User, UserDatabase
from utils.utils import get_password_hash
from utils.crypto import encrypt_password
from main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_accessnode"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

async def create_test_database():
    """Create test database"""
    try:
        # Connect to postgres database to create test database
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='postgres',
            host='localhost'
        )

        # Drop and create test database
        await conn.execute('DROP DATABASE IF EXISTS test_accessnode')
        await conn.execute('CREATE DATABASE test_accessnode')
        await conn.close()
        print("✅ Test database created")
    except Exception as e:
        print(f"Error creating test database: {e}")
        raise

async def drop_test_database():
    """Drop test database"""
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='postgres',
            host='localhost'
        )
        await conn.execute('DROP DATABASE IF EXISTS test_accessnode')
        await conn.close()
        print("✅ Test database dropped")
    except Exception as e:
        print(f"Error dropping test database: {e}")

@pytest.fixture(scope="session")
async def test_database():
    """Create and cleanup test database"""
    await create_test_database()
    yield
    await drop_test_database()

@pytest.fixture(scope="session")
async def test_engine(test_database):
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        future=True,
        pool_pre_ping=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user"""
    # Check if user already exists
    stmt = select(User).where(User.username == "testuser")
    result = await db_session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return existing_user

    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_user_database(db_session: AsyncSession, test_user: User) -> UserDatabase:
    """Create test user database connection"""
    encrypted_password = encrypt_password("postgres")

    # Convert bytes to string for database storage
    password_str = encrypted_password.decode('utf-8') if isinstance(encrypted_password, bytes) else encrypted_password

    database = UserDatabase(
        owner_id=test_user.id,
        db_name="test_postgres_db",
        db_type="postgresql",
        host="localhost",
        port=5432,
        username="postgres",
        password=password_str
    )
    db_session.add(database)
    await db_session.commit()
    await db_session.refresh(database)
    return database