#!/usr/bin/env python3
"""
Test the async AccessNode functionality
"""
import pytest
from accessnode import AccessNode
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def test_db_config():
    """Test database configuration"""
    return {
        'db_type': 'postgresql',
        'database_name': 'test_accessnode',
        'host': 'localhost',
        'port': 5432,
        'username': 'postgres',
        'password': 'postgres'
    }

@pytest.fixture
async def accessnode_instance(test_db_config):
    """Create AccessNode instance for testing"""
    db = AccessNode(**test_db_config)
    await db.initialize()

    # Create test table
    await db.raw_query("""
        CREATE TABLE IF NOT EXISTS test_items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            value INTEGER,
            active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    yield db

    # Cleanup
    try:
        await db.raw_query("DROP TABLE IF EXISTS test_items;")
    except Exception:
        pass

class TestAsyncAccessNode:
    """Test async AccessNode operations"""

    @pytest.mark.asyncio
    async def test_initialization(self, test_db_config):
        """Test AccessNode initialization"""
        db = AccessNode(**test_db_config)
        await db.initialize()
        assert db.db_type == 'postgresql'
        assert db.database_name == 'test_accessnode'
        assert db._initialized

    @pytest.mark.asyncio
    async def test_raw_query(self, accessnode_instance):
        """Test async raw query execution"""
        result = await accessnode_instance.raw_query("SELECT 1 as test_value;")
        assert len(result) == 1
        assert result[0]['test_value'] == 1

    @pytest.mark.asyncio
    async def test_database_version(self, accessnode_instance):
        """Test database version query"""
        result = await accessnode_instance.raw_query("SELECT version() as db_version;")
        assert len(result) == 1
        assert 'PostgreSQL' in result[0]['db_version']

    @pytest.mark.asyncio
    async def test_insert_operation(self, accessnode_instance):
        """Test async insert operation"""
        data = {
            'name': 'Test Item',
            'value': 100,
            'active': True
        }

        item_id = await accessnode_instance.insert('test_items', data)
        assert isinstance(item_id, int)
        assert item_id > 0

    @pytest.mark.asyncio
    async def test_get_operation(self, accessnode_instance):
        """Test async get operation"""
        # First insert an item
        data = {'name': 'Get Test Item', 'value': 200}
        item_id = await accessnode_instance.insert('test_items', data)

        # Then retrieve it
        retrieved_item = await accessnode_instance.get('test_items', {'id': item_id})

        assert retrieved_item is not None
        assert retrieved_item['name'] == 'Get Test Item'
        assert retrieved_item['value'] == 200
        assert retrieved_item['id'] == item_id

    @pytest.mark.asyncio
    async def test_get_all_operation(self, accessnode_instance):
        """Test async get_all operation"""
        # Insert multiple items
        items_data = [
            {'name': 'Item 1', 'value': 10},
            {'name': 'Item 2', 'value': 20},
            {'name': 'Item 3', 'value': 30}
        ]

        inserted_ids = []
        for item in items_data:
            item_id = await accessnode_instance.insert('test_items', item)
            inserted_ids.append(item_id)

        # Get all items
        all_items = await accessnode_instance.get_all('test_items')
        assert len(all_items) >= 3  # At least the 3 we inserted

        # Get items with filter
        filtered_items = await accessnode_instance.get_all('test_items', {'value': 20})
        assert len(filtered_items) == 1
        assert filtered_items[0]['name'] == 'Item 2'

    @pytest.mark.asyncio
    async def test_update_operation(self, accessnode_instance):
        """Test async update operation"""
        # Insert item
        data = {'name': 'Update Test', 'value': 300}
        item_id = await accessnode_instance.insert('test_items', data)

        # Update item
        updated_count = await accessnode_instance.update(
            'test_items',
            {'id': item_id},
            {'name': 'Updated Item', 'value': 350}
        )

        assert updated_count == 1

        # Verify update
        updated_item = await accessnode_instance.get('test_items', {'id': item_id})
        assert updated_item['name'] == 'Updated Item'
        assert updated_item['value'] == 350

    @pytest.mark.asyncio
    async def test_delete_operation(self, accessnode_instance):
        """Test async delete operation"""
        # Insert item
        data = {'name': 'Delete Test', 'value': 400}
        item_id = await accessnode_instance.insert('test_items', data)

        # Verify item exists
        item = await accessnode_instance.get('test_items', {'id': item_id})
        assert item is not None

        # Delete item
        deleted_count = await accessnode_instance.delete('test_items', {'id': item_id})
        assert deleted_count == 1

        # Verify item is deleted
        deleted_item = await accessnode_instance.get('test_items', {'id': item_id})
        assert deleted_item is None

    @pytest.mark.asyncio
    async def test_complex_query(self, accessnode_instance):
        """Test complex raw query with joins and aggregations"""
        # Create related table
        await accessnode_instance.raw_query("""
            CREATE TABLE IF NOT EXISTS test_categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """)

        # Insert category
        await accessnode_instance.raw_query("""
            INSERT INTO test_categories (name) VALUES ('Electronics');
        """)

        # Add category_id to test_items
        await accessnode_instance.raw_query("""
            ALTER TABLE test_items
            ADD COLUMN IF NOT EXISTS category_id INTEGER
            REFERENCES test_categories(id);
        """)

        # Insert item with category
        await accessnode_instance.raw_query("""
            INSERT INTO test_items (name, value, category_id)
            VALUES ('Laptop', 1000, 1);
        """)

        # Complex query
        result = await accessnode_instance.raw_query("""
            SELECT
                c.name as category_name,
                COUNT(i.id) as item_count,
                AVG(i.value) as avg_value
            FROM test_categories c
            LEFT JOIN test_items i ON c.id = i.category_id
            GROUP BY c.id, c.name;
        """)

        assert len(result) >= 1
        assert result[0]['category_name'] == 'Electronics'

        # Cleanup
        await accessnode_instance.raw_query("DROP TABLE IF EXISTS test_categories CASCADE;")

    @pytest.mark.asyncio
    async def test_error_handling(self, accessnode_instance):
        """Test error handling for invalid operations"""

        # Test invalid table name
        with pytest.raises(Exception):
            await accessnode_instance.get('nonexistent_table', {'id': 1})

        # Test invalid SQL
        with pytest.raises(Exception):
            await accessnode_instance.raw_query("INVALID SQL SYNTAX;")

    @pytest.mark.asyncio
    async def test_transaction_behavior(self, accessnode_instance):
        """Test transaction-like behavior"""
        # Count items before
        before_count = await accessnode_instance.raw_query("SELECT COUNT(*) as count FROM test_items;")
        initial_count = before_count[0]['count']

        # Insert multiple items in sequence
        items = [
            {'name': 'Trans Item 1', 'value': 500},
            {'name': 'Trans Item 2', 'value': 600},
            {'name': 'Trans Item 3', 'value': 700}
        ]

        for item in items:
            await accessnode_instance.insert('test_items', item)

        # Count items after
        after_count = await accessnode_instance.raw_query("SELECT COUNT(*) as count FROM test_items;")
        final_count = after_count[0]['count']

        assert final_count == initial_count + 3