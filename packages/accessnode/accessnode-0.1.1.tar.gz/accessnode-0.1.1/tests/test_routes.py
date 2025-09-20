# tests/test_routes.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid
from unittest.mock import patch
from accessnode.core.database import get_db
from accessnode.core.models import Base
from main import app

# Create test database engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture
async def test_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session for testing
    async with TestingSessionLocal() as session:
        yield session
        # Rollback any changes
        await session.rollback()

@pytest.fixture
def override_get_db(test_db):
    async def _override_get_db():
        try:
            yield test_db
        finally:
            await test_db.close()
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def test_client(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_user(test_client):
    unique_username = f"newuser_{uuid.uuid4().hex}"
    await test_client.post(
        "/user/register",
        json={"username": unique_username, "password": "newpass"}
    )
    return unique_username

async def get_token(test_client, username):
    response = await test_client.post(
        "/user/token",
        data={"username": username, "password": "newpass"}
    )
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_register(test_client):
    unique_username = f"newuser_{uuid.uuid4().hex}"
    response = await test_client.post(
        "/user/register",
        json={"username": unique_username, "password": "newpass"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == unique_username

    # Test duplicate registration
    response = await test_client.post(
        "/user/register",
        json={"username": unique_username, "password": "newpass"}
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login(test_client):
    unique_username = f"newuser_{uuid.uuid4().hex}"
    response = await test_client.post(
        "/user/register",
        json={"username": unique_username, "password": "newpass"}
    )
    assert response.status_code == 200

    # Test successful login
    response = await test_client.post(
        "/user/token",
        data={"username": unique_username, "password": "newpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Test failed login
    response = await test_client.post(
        "/user/token",
        data={"username": unique_username, "password": "wrongpass"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_verify_token(test_client):
    unique_username = f"newuser_{uuid.uuid4().hex}"
    await test_client.post(
        "/user/register",
        json={"username": unique_username, "password": "newpass"}
    )

    response = await test_client.post(
        "/user/token",
        data={"username": unique_username, "password": "newpass"}
    )
    token = response.json()["access_token"]

    response = await test_client.get(f"/user/verify-token?token={token}")
    assert response.status_code == 200
    assert response.json()["valid"] is True

    response = await test_client.get("/user/verify-token?token=invalid_token")
    assert response.status_code == 200
    assert response.json()["valid"] is False

@pytest.mark.asyncio
async def test_get_me(test_client, test_user):
    token = await get_token(test_client, test_user)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await test_client.get("/user/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user

@pytest.fixture
async def test_database_info():
    return {
        "db_name": f"test_db_{uuid.uuid4().hex[:8]}",
        "db_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "username": "test_user",
        "password": "test_pass"
    }

@pytest.mark.asyncio
async def test_setup_database(test_client, test_user, test_database_info):
    token = await get_token(test_client, test_user)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await test_client.post(
        "/user/databases/setup", 
        headers=headers, 
        json=test_database_info
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["db_name"] == test_database_info["db_name"]
    assert result["db_type"] == test_database_info["db_type"]
    assert result["host"] == test_database_info["host"]
    assert result["port"] == test_database_info["port"]
    assert result["username"] == test_database_info["username"]
    assert result["password"] == "********"

@pytest.fixture
async def setup_test_database(test_client, test_user, test_database_info):
    token = await get_token(test_client, test_user)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await test_client.post(
        "/user/databases/setup",
        headers=headers,
        json=test_database_info
    )
    assert response.status_code == 200
    return response.json()

@pytest.mark.asyncio
async def test_get_user_databases(test_client, test_user, setup_test_database):
    token = await get_token(test_client, test_user)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await test_client.get("/user/databases", headers=headers)
    assert response.status_code == 200
    databases = response.json()
    assert len(databases) > 0
    assert databases[0]["db_name"] == setup_test_database["db_name"]

@pytest.mark.asyncio
async def test_execute_query(test_client, test_user, setup_test_database):
    token = await get_token(test_client, test_user)
    headers = {"Authorization": f"Bearer {token}"}
    
    with patch('accessnode.AccessNode.raw_query') as mock_query:
        mock_query.return_value = [{"result": 1}]
        
        query_data = {"query": "SELECT 1"}
        response = await test_client.post(
            f"/user/database/{setup_test_database['id']}/query",
            headers=headers,
            json=query_data
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "result" in result
        mock_query.assert_called_once_with("SELECT 1")

# @pytest.mark.asyncio
# async def test_connect_database(test_client, test_user, test_database_info):
#     token = await get_token(test_client, test_user)
#     headers = {"Authorization": f"Bearer {token}"}
    
#     with patch('db_opps.check_db_connection') as mock_check:
#         mock_check.return_value = True
        
#         response = await test_client.post(
#             "/user/databases/connect", 
#             headers=headers, 
#             json=test_database_info
#         )
        
#         assert response.status_code == 200
#         result = response.json()
#         assert result["db_name"] == test_database_info["db_name"]
#         assert result["db_type"] == test_database_info["db_type"]
#         assert result["host"] == test_database_info["host"]
#         assert result["port"] == test_database_info["port"]
#         assert result["username"] == test_database_info["username"]
#         assert result["password"] == "********"
#         mock_check.assert_called_once()
