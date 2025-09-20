# tests/test_db_opps.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock
from accessnode.core.db_opps import (
    get_user_by_username,
    create_user,
    get_user_databases,
    check_db_connection
)
from accessnode.core.schemas import UserCreate, UserDatabaseCreate
from accessnode.core.crypto import encrypt_password

async def test_get_user_by_username(db_session: AsyncSession, test_user):
    # Test existing user
    user = await get_user_by_username(db_session, "testuser")
    assert user is not None
    assert user.username == "testuser"

    # Test non-existent user
    user = await get_user_by_username(db_session, "nonexistent")
    assert user is None

async def test_create_user(db_session: AsyncSession):
    user_data = UserCreate(username="newuser", password="newpass")
    user = await create_user(db_session, user_data)
    assert user is not None
    assert user.username == "newuser"

    # Verify user was created in database
    db_user = await get_user_by_username(db_session, "newuser")
    assert db_user is not None
    assert db_user.username == "newuser"

async def test_get_user_databases(db_session: AsyncSession, test_user, test_database):
    databases = await get_user_databases(db_session, test_user.id)
    assert len(databases) > 0
    assert databases[0].db_name == "test_table"
    assert databases[0].db_type == "postgresql"

# @pytest.mark.asyncio
# async def test_check_db_connection():
#     db_info = UserDatabaseCreate(
#         db_name="test_table",
#         db_type="postgres",
#         host="localhost",
#         port=5432,
#         username="postgres",
#         password="postgres"
#     )

#     # Create mock connection with execute method
#     mock_conn = AsyncMock()
#     mock_conn.execute = AsyncMock()

#     # Create context manager class for connection
#     class AsyncContextManager:
#         async def __aenter__(self):
#             return mock_conn
        
#         async def __aexit__(self, exc_type, exc_val, exc_tb):
#             pass

#     # Create mock engine
#     mock_engine = AsyncMock()
#     mock_engine.dispose = AsyncMock()
#     mock_engine.connect.return_value = AsyncContextManager()

#     # Mock the connection check
#     with patch('db_opps.create_async_engine', return_value=mock_engine):
#         result = await check_db_connection(db_info)
#         assert result is True
        
#         # Verify mocks were called
#         mock_engine.connect.assert_called_once()
#         mock_conn.execute.assert_called_once()