"""
Secure test credentials management
Provides secure, configurable test credentials without hardcoding sensitive values
"""
import os
import secrets
import string


class TestCredentials:
    """Manages secure test credentials without hardcoding sensitive values"""

    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a secure password for testing"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Ensure it meets complexity requirements
        if not any(c.isupper() for c in password):
            password = password[:1] + secrets.choice(string.ascii_uppercase) + password[2:]
        if not any(c.islower() for c in password):
            password = password[:2] + secrets.choice(string.ascii_lowercase) + password[3:]
        if not any(c.isdigit() for c in password):
            password = password[:3] + secrets.choice(string.digits) + password[4:]
        if not any(c in "!@#$%^&*" for c in password):
            password = password[:4] + secrets.choice("!@#$%^&*") + password[5:]
        return password

    @staticmethod
    def get_test_password() -> str:
        """Get test password from environment or generate secure one"""
        return os.getenv('TEST_PASSWORD', TestCredentials.generate_secure_password())

    @staticmethod
    def get_db_password() -> str:
        """Get database password for testing"""
        return os.getenv('POSTGRES_PASSWORD', 'postgres')

    @staticmethod
    def get_test_credentials() -> dict:
        """Get standardized test credentials"""
        return {
            "password": TestCredentials.get_test_password(),
            "db_password": TestCredentials.get_db_password(),
            "weak_passwords": [
                "123",
                "weak",
                "password",
                "PASSWORD123"
            ],
            "wrong_password": "definitely_wrong_password"
        }