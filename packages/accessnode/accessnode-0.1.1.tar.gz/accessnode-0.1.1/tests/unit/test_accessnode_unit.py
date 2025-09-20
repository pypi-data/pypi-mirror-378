#!/usr/bin/env python3
"""
Unit tests for AccessNode - using mocks for isolation
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from accessnode import AccessNode


class TestAccessNodeUnit(unittest.TestCase):
    """Unit tests for AccessNode class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_config = {
            'db_type': 'postgresql',
            'database_name': 'test_db',
            'host': 'localhost',
            'port': 5432,
            'username': 'test_user',
            'password': 'test_pass'
        }

    def test_accessnode_initialization(self):
        """Test AccessNode initialization with config"""
        db = AccessNode(**self.db_config)

        self.assertEqual(db.db_type, 'postgresql')
        self.assertEqual(db.database_name, 'test_db')
        self.assertEqual(db.host, 'localhost')
        self.assertEqual(db.port, 5432)
        self.assertEqual(db.username, 'test_user')
        self.assertEqual(db.password, 'test_pass')
        self.assertFalse(db._initialized)

    def test_accessnode_initialization_without_credentials(self):
        """Test AccessNode can be initialized without database credentials"""
        db = AccessNode()

        self.assertIsNone(db.db_type)
        self.assertIsNone(db.database_name)
        self.assertIsNone(db.username)
        self.assertIsNone(db.password)
        self.assertEqual(db.host, 'localhost')
        self.assertIsNone(db.port)
        self.assertFalse(db._initialized)

    def test_sync_initialization_only(self):
        """Test AccessNode can be created (sync initialization only)"""
        # Just test that AccessNode can be created with mocks
        db = AccessNode(**self.db_config)
        self.assertIsNotNone(db)
        self.assertFalse(db._initialized)

    def test_memory_store_fallback_when_no_db_handler(self):
        """Test that AccessNode falls back to memory store when no db handler"""
        db = AccessNode()

        # Should use memory store
        self.assertIsNotNone(db.memory_store)
        self.assertIsNone(db.db_handler)

    def test_schema_registration(self):
        """Test schema registration in memory store"""
        db = AccessNode()

        # Test schema registration
        db.register_schema('test_table', {'name': str, 'value': int})
        self.assertIsNotNone(db.memory_store)


class TestAccessNodeAsync(unittest.IsolatedAsyncioTestCase):
    """Async test cases for AccessNode"""

    async def asyncSetUp(self):
        """Async setup for each test"""
        self.db_config = {
            'db_type': 'postgresql',
            'database_name': 'test_db',
            'host': 'localhost',
            'port': 5432,
            'username': 'test_user',
            'password': 'test_pass'
        }

    @patch('accessnode.accessnode.create_db_handler')
    @patch('accessnode.accessnode.ConnectionPool.create_pool')
    async def test_async_crud_operations(self, mock_pool, mock_handler):
        """Test full CRUD cycle with mocks"""
        # Setup mocks
        mock_db_handler = AsyncMock()
        mock_db_handler.insert.return_value = 1
        mock_db_handler.get.return_value = {'id': 1, 'name': 'test'}
        mock_db_handler.get_all.return_value = [{'id': 1, 'name': 'test'}]
        mock_db_handler.update.return_value = 1
        mock_db_handler.delete.return_value = 1

        mock_handler.return_value = mock_db_handler
        mock_pool.return_value = AsyncMock()

        db = AccessNode(**self.db_config)
        await db.initialize()

        # Test INSERT
        insert_id = await db.insert('test_table', {'name': 'test'})
        self.assertEqual(insert_id, 1)

        # Test GET
        result = await db.get('test_table', {'id': 1})
        self.assertEqual(result['name'], 'test')

        # Test GET_ALL
        all_results = await db.get_all('test_table')
        self.assertEqual(len(all_results), 1)

        # Test UPDATE
        updated = await db.update('test_table', {'id': 1}, {'name': 'updated'})
        self.assertEqual(updated, 1)

        # Test DELETE
        deleted = await db.delete('test_table', {'id': 1})
        self.assertEqual(deleted, 1)

    @patch('accessnode.accessnode.create_db_handler')
    @patch('accessnode.accessnode.ConnectionPool.create_pool')
    async def test_error_handling(self, mock_pool, mock_handler):
        """Test error handling in database operations"""
        # Setup mocks to raise exceptions
        mock_db_handler = AsyncMock()
        mock_db_handler.raw_query.side_effect = Exception("Database error")
        mock_handler.return_value = mock_db_handler
        mock_pool.return_value = AsyncMock()

        db = AccessNode(**self.db_config)
        await db.initialize()

        # Test that exception is propagated
        with self.assertRaises(Exception) as context:
            await db.raw_query("INVALID SQL")

        self.assertIn("Database error", str(context.exception))

    async def test_memory_store_operations(self):
        """Test operations using memory store (no database connection)"""
        db = AccessNode()  # No database config

        # Register schema
        db.register_schema('users', {'name': str, 'age': int})

        # Test insert
        result = await db.insert('users', {'name': 'Alice', 'age': 30})
        self.assertIsNotNone(result)

        # Test get_all
        all_users = await db.get_all('users')
        self.assertEqual(len(all_users), 1)
        self.assertEqual(all_users[0]['name'], 'Alice')

        # Test update
        updated = await db.update('users', {'name': 'Alice'}, {'age': 31})
        self.assertEqual(updated, 1)

        # Test delete
        deleted = await db.delete('users', {'name': 'Alice'})
        self.assertEqual(deleted, 1)

        # Verify deletion
        remaining = await db.get_all('users')
        self.assertEqual(len(remaining), 0)


if __name__ == '__main__':
    unittest.main()