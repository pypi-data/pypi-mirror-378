# tests/test_auth.py
import pytest
from fastapi import HTTPException
from accessnode.core.auth import create_access_token, verify_token, authenticate_user
from datetime import timedelta

pytestmark = pytest.mark.asyncio

async def test_create_access_token():
    """Test creating access tokens."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

    # Test with expiration
    token_with_exp = create_access_token(data, expires_delta=timedelta(minutes=15))
    assert token_with_exp is not None
    assert isinstance(token_with_exp, str)

async def test_verify_token():
    """Test token verification."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    token_data = verify_token(token)
    assert token_data.username == "testuser"

    with pytest.raises(HTTPException):
        verify_token("invalid_token")

async def test_authenticate_user(db_session, test_user):
    """Test user authentication."""
    # Test valid credentials
    user = await authenticate_user(db_session, "testuser", "testpass")
    assert user is not None
    assert user.username == "testuser"

    # Test invalid password
    invalid_pass_user = await authenticate_user(db_session, "testuser", "wrongpass")
    assert invalid_pass_user is False

    # Test non-existent user
    nonexistent_user = await authenticate_user(db_session, "nonexistent", "testpass")
    assert nonexistent_user is False
