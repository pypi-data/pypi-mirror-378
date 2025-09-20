# tests/test_utils.py
import pytest
from accessnode.core.utils import verify_password, get_password_hash

def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    
    # Test that hashing works
    assert hashed != password
    assert isinstance(hashed, str)
    
    # Test that verification works
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_password_verification():
    # Test with known password and hash
    password = "testpassword"
    hashed = get_password_hash(password)
    
    # Correct password
    assert verify_password(password, hashed) is True
    
    # Wrong password
    assert verify_password("wrongpassword", hashed) is False
    
    # Empty password
    assert verify_password("", hashed) is False
    
    # None password
    with pytest.raises(TypeError):
        verify_password(None, hashed)
