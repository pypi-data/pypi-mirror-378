from typing import Any, Dict, List, Union, Optional
from .exceptions import DatabaseConnectionError

class DatabaseHandler:
    """Base class for database handlers."""
    
    def __init__(self, database: str, **kwargs):
        self.database = database
        self.config = kwargs
        self.connection = None
        
    def connect(self) -> None:
        """Establish database connection."""
        raise NotImplementedError
        
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def get(self, table_name: str, filter_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get single record."""
        raise NotImplementedError
        
    def get_all(self, table_name: str, filter_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get multiple records."""
        raise NotImplementedError
        
    def insert(self, table_name: str, data: Dict[str, Any]) -> Union[int, str]:
        """Insert record."""
        raise NotImplementedError
        
    def update(self, table_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update records."""
        raise NotImplementedError
        
    def delete(self, table_name: str, filter_data: Dict[str, Any]) -> int:
        """Delete records."""
        raise NotImplementedError
        
    def raw_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute raw query."""
        raise NotImplementedError
    








    # Database operations methods
    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Create a table (or collection for MongoDB) with the given schema.
        
        :param table_name: Name of the table/collection to create
        :param schema: Dictionary describing the schema (field names and types)
        """
        if self.db_type == 'mongodb':
            self.db_handler.create_collection(table_name)
        else:
            schema_str = ", ".join([f"{key} {value}" for key, value in schema.items()])
            table_schema = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema_str})"
            self.db_handler.create_table(table_schema)

    def insert(self, table_name: str, data: Dict[str, Any]) -> Union[int, str]:
        """
        Insert data into the specified table/collection.
        
        :param table_name: Name of the table/collection
        :param data: Dictionary of data to insert
        :return: ID of the inserted record
        """
        return self.db_handler.insert(table_name, data)

    def get(self, table_name: str, filter_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """
        Retrieve a single record from the specified table/collection.
        
        :param table_name: Name of the table/collection
        :param filter_data: Dictionary of filter criteria
        :return: Retrieved record or None if not found
        """
        return self.db_handler.get(table_name, filter_data)

    def get_all(self, table_name: str, filter_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all records from the specified table/collection that match the filter criteria.
        
        :param table_name: Name of the table/collection
        :param filter_data: Dictionary of filter criteria (optional)
        :return: List of retrieved records
        """
        return self.db_handler.get_all(table_name, filter_data)

    def update(self, table_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """
        Update records in the specified table/collection.
        
        :param table_name: Name of the table/collection
        :param filter_data: Dictionary of filter criteria
        :param update_data: Dictionary of data to update
        :return: Number of records updated
        """
        return self.db_handler.update(table_name, filter_data, update_data)

    def delete(self, table_name: str, filter_data: Dict[str, Any]) -> int:
        """
        Delete records from the specified table/collection.
        
        :param table_name: Name of the table/collection
        :param filter_data: Dictionary of filter criteria
        :return: Number of records deleted
        """
        return self.db_handler.delete(table_name, filter_data)

    def raw_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a raw query on the database.
        
        :param query: Raw query string
        :return: List of results
        """
        return self.db_handler.raw_query(query)

    def close(self) -> None:
        """
        Close the database connection.
        """
        self.db_handler.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
