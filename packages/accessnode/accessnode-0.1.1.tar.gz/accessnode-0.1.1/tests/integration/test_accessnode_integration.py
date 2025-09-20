#!/usr/bin/env python3
"""
Integration tests for AccessNode - using real database connections
"""
import unittest
import asyncio
import os
from unittest import skipUnless
from accessnode import AccessNode


# Only run integration tests if we have a test database available
DB_AVAILABLE = os.getenv('POSTGRES_HOST', 'localhost') and os.getenv('POSTGRES_USER', 'postgres')


@skipUnless(DB_AVAILABLE, "Database not available for integration tests")
class TestAccessNodeIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests with real database"""

    async def asyncSetUp(self):
        """Set up test database and AccessNode instance"""
        self.db_config = {
            'db_type': 'postgresql',
            'database_name': os.getenv('TEST_DATABASE_NAME', 'test_accessnode'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', '5432')),
            'username': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
        }

        self.db = AccessNode(**self.db_config)
        await self.db.initialize()

        # Create test table
        await self.db.raw_query("""
            CREATE TABLE IF NOT EXISTS integration_test_items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                value INTEGER,
                active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    async def asyncTearDown(self):
        """Clean up after each test"""
        try:
            # Clean up test data
            await self.db.raw_query("DROP TABLE IF EXISTS integration_test_items CASCADE;")
            await self.db.close()
        except Exception:
            pass  # Ignore cleanup errors

    async def test_database_connection(self):
        """Test that we can connect to the database"""
        result = await self.db.raw_query("SELECT 1 as test_value;")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['test_value'], 1)

    async def test_database_version(self):
        """Test database version query"""
        result = await self.db.raw_query("SELECT version() as db_version;")
        self.assertEqual(len(result), 1)
        self.assertIn('PostgreSQL', result[0]['db_version'])

    async def test_crud_operations_real_db(self):
        """Test full CRUD cycle with real database"""
        # INSERT
        item_id = await self.db.insert('integration_test_items', {
            'name': 'Integration Test Item',
            'value': 100,
            'active': True
        })
        self.assertIsInstance(item_id, int)
        self.assertGreater(item_id, 0)

        # GET
        retrieved_item = await self.db.get('integration_test_items', {'id': item_id})
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item['name'], 'Integration Test Item')
        self.assertEqual(retrieved_item['value'], 100)
        self.assertTrue(retrieved_item['active'])

        # UPDATE
        updated_count = await self.db.update(
            'integration_test_items',
            {'id': item_id},
            {'name': 'Updated Item', 'value': 150}
        )
        self.assertEqual(updated_count, 1)

        # Verify update
        updated_item = await self.db.get('integration_test_items', {'id': item_id})
        self.assertEqual(updated_item['name'], 'Updated Item')
        self.assertEqual(updated_item['value'], 150)

        # DELETE
        deleted_count = await self.db.delete('integration_test_items', {'id': item_id})
        self.assertEqual(deleted_count, 1)

        # Verify deletion
        deleted_item = await self.db.get('integration_test_items', {'id': item_id})
        self.assertIsNone(deleted_item)

    async def test_batch_operations(self):
        """Test batch insert and get_all operations"""
        # Insert multiple items
        items_data = [
            {'name': 'Batch Item 1', 'value': 10},
            {'name': 'Batch Item 2', 'value': 20},
            {'name': 'Batch Item 3', 'value': 30}
        ]

        inserted_ids = []
        for item in items_data:
            item_id = await self.db.insert('integration_test_items', item)
            inserted_ids.append(item_id)

        self.assertEqual(len(inserted_ids), 3)

        # Get all items
        all_items = await self.db.get_all('integration_test_items')
        self.assertGreaterEqual(len(all_items), 3)

        # Get items with filter
        filtered_items = await self.db.get_all('integration_test_items', {'value': 20})
        self.assertEqual(len(filtered_items), 1)
        self.assertEqual(filtered_items[0]['name'], 'Batch Item 2')

        # Cleanup
        for item_id in inserted_ids:
            await self.db.delete('integration_test_items', {'id': item_id})

    async def test_complex_query(self):
        """Test complex raw SQL query"""
        # Insert test data
        await self.db.insert('integration_test_items', {'name': 'Complex Test 1', 'value': 100})
        await self.db.insert('integration_test_items', {'name': 'Complex Test 2', 'value': 200})

        # Complex query with aggregation
        result = await self.db.raw_query("""
            SELECT
                COUNT(*) as total_count,
                AVG(value) as avg_value,
                MAX(value) as max_value,
                MIN(value) as min_value
            FROM integration_test_items
            WHERE name LIKE 'Complex Test%';
        """)

        self.assertEqual(len(result), 1)
        stats = result[0]
        self.assertEqual(stats['total_count'], 2)
        self.assertEqual(float(stats['avg_value']), 150.0)
        self.assertEqual(stats['max_value'], 200)
        self.assertEqual(stats['min_value'], 100)

    async def test_transaction_behavior(self):
        """Test transaction-like behavior with multiple operations"""
        initial_count_result = await self.db.raw_query(
            "SELECT COUNT(*) as count FROM integration_test_items;"
        )
        initial_count = initial_count_result[0]['count']

        # Perform multiple operations
        items = [
            {'name': 'Transaction Test 1', 'value': 500},
            {'name': 'Transaction Test 2', 'value': 600},
            {'name': 'Transaction Test 3', 'value': 700}
        ]

        for item in items:
            await self.db.insert('integration_test_items', item)

        # Verify all operations completed
        final_count_result = await self.db.raw_query(
            "SELECT COUNT(*) as count FROM integration_test_items;"
        )
        final_count = final_count_result[0]['count']

        self.assertEqual(final_count, initial_count + 3)

    async def test_error_handling_real_db(self):
        """Test error handling with real database errors"""
        # Test invalid table name
        with self.assertRaises(Exception):
            await self.db.get('nonexistent_table_xyz', {'id': 1})

        # Test invalid SQL syntax
        with self.assertRaises(Exception):
            await self.db.raw_query("INVALID SQL SYNTAX HERE;")

        # Test constraint violation (if we had constraints)
        # This would depend on actual database constraints

    async def test_concurrent_operations(self):
        """Test concurrent database operations"""
        async def insert_item(name, value):
            return await self.db.insert('integration_test_items', {
                'name': name,
                'value': value
            })

        # Run multiple inserts concurrently
        tasks = [
            insert_item(f'Concurrent Item {i}', i * 10)
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed and return valid IDs
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIsInstance(result, int)
            self.assertGreater(result, 0)

        # Verify all items were inserted
        concurrent_items = await self.db.get_all('integration_test_items', {})
        concurrent_count = len([
            item for item in concurrent_items
            if item['name'].startswith('Concurrent Item')
        ])
        self.assertEqual(concurrent_count, 5)


if __name__ == '__main__':
    # You can run this with: python -m pytest tests/integration/test_accessnode_integration.py -v
    unittest.main()