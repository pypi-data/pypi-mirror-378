import pytest
from accessnode import AccessNode
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_postgresql_handler():
    with patch('accessnode.accessnode.PostgresqlHandler') as mock:
        yield mock

@pytest.fixture
def mock_mysql_handler():
    with patch('accessnode.accessnode.MySQLHandler') as mock:
        yield mock

@pytest.fixture
def mock_mongodb_handler():
    with patch('accessnode.accessnode.MongoDBHandler') as mock:
        yield mock

def test_accessnode_initialization_postgresql(mock_postgresql_handler):
    db = AccessNode('postgresql', 'test_db', host='localhost', port=5432)
    assert db.db_type == 'postgresql'
    mock_postgresql_handler.assert_called_once()

def test_accessnode_initialization_mysql(mock_mysql_handler):
    db = AccessNode('mysql', 'test_db', host='localhost', port=3306)
    assert db.db_type == 'mysql'
    mock_mysql_handler.assert_called_once()

def test_accessnode_initialization_mongodb(mock_mongodb_handler):
    db = AccessNode('mongodb', 'test_db', host='localhost', port=27017)
    assert db.db_type == 'mongodb'
    mock_mongodb_handler.assert_called_once()

def test_accessnode_invalid_type():
    with pytest.raises(ValueError):
        AccessNode('invalid_type', 'test_db')

@pytest.fixture
def db_with_mock_handler():
    db = AccessNode('postgresql', 'test_db')
    db.db_handler = MagicMock()
    return db

def test_create_table(db_with_mock_handler):
    schema = {'id': 'INTEGER PRIMARY KEY', 'name': 'VARCHAR(255)'}
    db_with_mock_handler.create_table('test_table', schema)
    db_with_mock_handler.db_handler.create_table.assert_called_once()

def test_insert(db_with_mock_handler):
    data = {'name': 'test', 'value': 123}
    db_with_mock_handler.insert('test_table', data)
    db_with_mock_handler.db_handler.insert.assert_called_once_with('test_table', data)

def test_get(db_with_mock_handler):
    filter_data = {'id': 1}
    db_with_mock_handler.get('test_table', filter_data)
    db_with_mock_handler.db_handler.get.assert_called_once_with('test_table', filter_data)

def test_get_all(db_with_mock_handler):
    db_with_mock_handler.get_all('test_table')
    db_with_mock_handler.db_handler.get_all.assert_called_once_with('test_table', None)

def test_update(db_with_mock_handler):
    filter_data = {'id': 1}
    update_data = {'name': 'updated'}
    db_with_mock_handler.update('test_table', filter_data, update_data)
    db_with_mock_handler.db_handler.update.assert_called_once_with('test_table', filter_data, update_data)

def test_delete(db_with_mock_handler):
    filter_data = {'id': 1}
    db_with_mock_handler.delete('test_table', filter_data)
    db_with_mock_handler.db_handler.delete.assert_called_once_with('test_table', filter_data)

def test_raw_query(db_with_mock_handler):
    query = "SELECT * FROM test_table"
    db_with_mock_handler.raw_query(query)
    db_with_mock_handler.db_handler.raw_query.assert_called_once_with(query)

def test_context_manager(db_with_mock_handler):
    with db_with_mock_handler as db:
        assert db == db_with_mock_handler
    db_with_mock_handler.db_handler.close.assert_called_once()

