# base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class DatabaseHandler(ABC):

    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    async def get(self, table_name: str, filter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a single record from the database."""
        pass

    @abstractmethod
    async def get_all(self, table_name: str, filter_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve all records from the database."""
        pass

    @abstractmethod
    async def insert(self, table_name: str, data: Dict[str, Any], filter_data: Dict[str, Any] = None) -> Union[int, str]:
        """Insert a record into the database."""
        pass

    @abstractmethod
    async def update(self, table_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update records in the database."""
        pass

    @abstractmethod
    async def delete(self, table_name: str, filter_data: Dict[str, Any]) -> int:
        """Delete records from the database."""
        pass

    @abstractmethod
    async def raw_query(self, query: str) -> Union[List[Dict[str, Any]], str]:
        """Execute a raw SQL query."""
        pass

    @abstractmethod
    async def get_table_schema(self, table_name: str = None) -> List[Dict[str, Any]]:
        """Get schema information for all tables or a specific table."""
        pass
