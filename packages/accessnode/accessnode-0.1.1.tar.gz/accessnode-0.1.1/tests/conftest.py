# tests/conftest.py
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


# Test database URL for the default postgres database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_table"

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

async def create_database():
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='postgres',
            host='localhost'
        )
        await conn.execute('DROP DATABASE IF EXISTS test_table')
        await conn.execute('CREATE DATABASE test_table')
        await conn.close()
    except Exception as e:
        print(f"Error creating test database: {e}")
        raise

async def drop_database():
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='postgres',
            host='localhost'
        )
        await conn.execute('DROP DATABASE IF EXISTS test_table')
        await conn.close()
    except Exception as e:
        print(f"Error dropping test database: {e}")

@pytest.fixture(scope="session")
async def database():
    await create_database()
    yield
    await drop_database()

@pytest.fixture(scope="session")
async def engine(database):
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True,
        pool_pre_ping=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with session_maker() as session:
        try:
            yield session
            await session.rollback()  # Rollback any pending changes
        finally:
            await session.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    # First try to find existing user
    stmt = select(User).where(User.username == "testuser")
    result = await db_session.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return existing_user
        
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_database(db_session: AsyncSession, test_user: User) -> UserDatabase:
    encrypted_password = encrypt_password("postgres")
    # Convert bytes to string for database storage
    password_str = encrypted_password.decode('utf-8') if isinstance(encrypted_password, bytes) else encrypted_password
    
    database = UserDatabase(
        owner_id=test_user.id,
        db_name="test_table",
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
