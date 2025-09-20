# cryto.py
import os
from cryptography.fernet import Fernet

# Ensure the encryption key is loaded from the environment
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")


if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable is not set")

# Convert the key to bytes if needed
fernet = Fernet(ENCRYPTION_KEY.encode()) if isinstance(ENCRYPTION_KEY, str) else Fernet(ENCRYPTION_KEY)

def encrypt_password(password: str) -> str:
    """
    Encrypt a password and return it as a UTF-8 string.
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    
    try:
        password_bytes = password.encode('utf-8')
        encrypted_bytes = fernet.encrypt(password_bytes)
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {str(e)}")
        raise

def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt an encrypted password string and return the original password.
    """
    if not isinstance(encrypted_password, str):
        raise ValueError("Encrypted password must be a string")
    
    try:
        encrypted_bytes = encrypted_password.encode('utf-8')
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        raise
