#!/usr/bin/env python3
"""
Test configuration and utilities
"""
import os
import tempfile
import unittest
from unittest.mock import patch


class TestConfig:
    """Test configuration constants"""

    # Test database configuration
    TEST_DB_CONFIG = {
        'db_type': 'postgresql',
        'database_name': os.getenv('TEST_DATABASE_NAME', 'test_accessnode'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'username': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
    }

    # Test environment variables
    TEST_ENV = {
        'SECRET_KEY': 'test-secret-key-for-testing',
        'ENCRYPTION_KEY': 'test-encryption-key-32-characters',
        'POSTGRES_USER': 'postgres',
        'POSTGRES_PASSWORD': 'postgres',
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'test_accessnode'
    }


class BaseTestCase(unittest.TestCase):
    """Base test case with common utilities"""

    def setUp(self):
        """Set up common test environment"""
        # Patch environment variables for testing
        self.env_patcher = patch.dict(os.environ, TestConfig.TEST_ENV)
        self.env_patcher.start()

        # Import secure credentials
        from .test_credentials import TestCredentials
        creds = TestCredentials.get_test_credentials()

        # Common test data with secure passwords
        self.test_user_data = {
            "username": "testuser",
            "password": creds["password"]
        }

        self.test_db_config = {
            "db_name": "test_db",
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "username": "postgres",
            "password": creds["db_password"]
        }

    def tearDown(self):
        """Clean up after each test"""
        self.env_patcher.stop()

    def create_temp_file(self, content=""):
        """Create a temporary file for testing"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def assertDictContainsSubset(self, subset, dictionary, msg=None):
        """Assert that subset is a subset of dictionary"""
        for key, value in subset.items():
            self.assertIn(key, dictionary, msg)
            self.assertEqual(dictionary[key], value, msg)


class AsyncBaseTestCase(unittest.IsolatedAsyncioTestCase, BaseTestCase):
    """Base async test case"""

    async def asyncSetUp(self):
        """Async setup for tests"""
        BaseTestCase.setUp(self)

    async def asyncTearDown(self):
        """Async cleanup for tests"""
        BaseTestCase.tearDown(self)


def skip_if_no_database(test_func):
    """Decorator to skip tests if database is not available"""
    def wrapper(*args, **kwargs):
        try:
            import psycopg2
            # Try to connect to test database
            connection = psycopg2.connect(
                host=TestConfig.TEST_DB_CONFIG['host'],
                port=TestConfig.TEST_DB_CONFIG['port'],
                user=TestConfig.TEST_DB_CONFIG['username'],
                password=TestConfig.TEST_DB_CONFIG['password'],
                dbname='postgres'  # Connect to default database first
            )
            connection.close()
            return test_func(*args, **kwargs)
        except Exception:
            return unittest.skip("Database not available for testing")
    return wrapper


def requires_database(cls):
    """Class decorator to mark all test methods as requiring database"""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and attr_name.startswith('test_'):
            setattr(cls, attr_name, skip_if_no_database(attr))
    return cls