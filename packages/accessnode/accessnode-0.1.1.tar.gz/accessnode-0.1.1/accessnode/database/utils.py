from typing import Any, List
from accessnode.database.types import DatabaseType
from accessnode.database.databases.mongodb import MongoDBHandler
from accessnode.database.databases.mysql import MySQLHandler
from accessnode.database.databases.postgres import PostgresqlHandler
from accessnode.database.databases.sqlite import SQLiteHandler

from accessnode.core.exceptions import DatabaseError

def create_db_handler(db_type: str, **kwargs) -> Any:
    """
    Create and return the appropriate database handler based on the database type.
    
    :param db_type: Type of the database (e.g., 'postgresql', 'mysql', 'mongodb', 'sqlite').
    :param database: The name of the database to connect to.
    :param kwargs: Additional configuration parameters for the database connection.
    :return: Instance of the selected database handler.
    """
    try:
        if db_type == DatabaseType.POSTGRESQL:
            return PostgresqlHandler(**kwargs)
        elif db_type == DatabaseType.MYSQL:
            return MySQLHandler(**kwargs)
        elif db_type == DatabaseType.MONGODB:
            return MongoDBHandler(**kwargs)
        elif db_type == DatabaseType.SQLITE:
            return SQLiteHandler(**kwargs)
        else:
            supported = ", ".join(f"'{db}'" for db in DatabaseType.get_supported_types())
            raise ValueError(f"Unsupported database type. Choose from: {supported}")
    except Exception as e:
        raise DatabaseError(f"Failed to create database handler for '{db_type}': {str(e)}")
