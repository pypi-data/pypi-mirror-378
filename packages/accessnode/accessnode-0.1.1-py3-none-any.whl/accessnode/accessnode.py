from typing import Any, Dict, List, Union, Optional
from accessnode.schema_manager.schema_manager import SchemaManager
from .core.exceptions import safe_db_operation
from .caching.cache_database_handler import CacheDatabaseHandler
from .caching.cache_strategy import CacheStrategy
from accessnode.database.pool import ConnectionPool
from accessnode.database.utils import create_db_handler
# from accessnode.models.base import BaseModel
from .storage.memory import MemoryStore
import logging
import asyncio


class AccessNode:
    def __init__(self, db_type: Optional[str] = None, database_name: Optional[str] = None, username: Optional[str] = None,
                 password: Optional[str] = None, host: str = 'localhost', port: Optional[int] = None, 
                 cache: Optional[Any] = None, enforce_schemas: bool = True, auto_sync: bool = False):
        """
        Initialize AccessNode with database connection details and optional caching.

        :param db_type: Type of the database (e.g., 'postgresql', 'mysql', 'mongodb') (optional for small setups).
        :param database_name: Name of the database (optional for small setups).
        :param username: Database username (optional for small setups).
        :param password: Database password (optional for small setups).
        :param host: Database host (default: 'localhost').
        :param port: Database port (optional).
        :param cache: Optional cache instance (e.g., RedisCache).
        :param enforce_schemas: Whether to enforce schemas during operations (default: True).
        :param auto_sync: Automatically synchronize schemas upon initialization (default: False).
        """
        self.memory_store = MemoryStore()
        self.db_type = db_type.lower() if db_type else None
        self.database_name = database_name
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.cache = None
        self.db_pool = None
        self.schema_manager = None
        self.cache_strategy = CacheStrategy()
        self.enforce_schemas = enforce_schemas
        self.auto_sync = auto_sync
        self._initialized = False

        self.db_handler = None

        if cache:
            self.cache = CacheDatabaseHandler(cache, None)
        

    async def _initialize_database(self):
        """
        Internal method to set up the database handler and connection pool.
        """
        if self.db_type: 
            port = int(self.port) if self.port else None

            # Create database handler
            self.db_handler = create_db_handler(
                self.db_type,
                database=self.database_name,
                user=self.username,
                password=self.password,
                host=self.host,
                port=port
            )

            # Create the connection pool
            self.db_pool = await ConnectionPool.create_pool(
                self.db_type,
                user=self.username,
                password=self.password,
                database=self.database_name,
                host=self.host,
                port=port
            )

            # Initialize schema manager
            self.schema_manager = SchemaManager(database_pool=self.db_pool)

            # Update cache with the initialized db_handler
            if self.cache:
                self.cache.db_handler = self.db_handler

    async def initialize(self):
        """
        Public method to initialize the database asynchronously.
        """
        if not self.db_type or not self.database_name:
            logging.warning("Database details are missing; AccessNode will run in a limited mode.")
            return
        
        await self._initialize_database()
        self._initialized = True

        if self.auto_sync and self.schema_manager:
            await self.sync()
        
    

    def register_schema(self, schema_name: str, schema_fields: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a schema dynamically.
        :param schema_name: Name of the schema (e.g., table name).
        :param schema_fields: Optional schema fields for validation.
        """
        print('Registering schema')

        # if schema_name in self.models:
        #     raise ValueError(f"Schema '{schema_name}' is already registered.")
        
        # # self.models[schema_name] = schema_fields or {}

        # # Store schema fields separately, not as part of the data
        # self.models[schema_name] = {
        #     "schema": schema_fields or {},  # Store schema definitions
        #     "data": []  # Separate list for actual data
        # }

        # Register schema in MemoryStore
        try:
            self.memory_store.register_schema(schema_name, schema_fields)
            print(f"Schema '{schema_name}' registered successfully in MemoryStore.")
        except ValueError as e:
            raise ValueError(f"Error registering schema: {e}")

        if self.auto_sync and self.schema_manager:
            self.schema_manager.create_schema(schema_name, schema_fields or {})
    

    def validate_schema(self, schema_data: Dict[str, Any]) -> bool:
        """
        Validate schema data through SchemaManager.
        """
        try:
            return self.schema_manager.validate_schema(schema_data)
        except Exception as e:
            logging.error(f"Error validating schema: {e}")
            raise

    # @safe_db_operation
    # async def execute_operation(
    #     self, 
    #     operation: str, 
    #     table_name: str, 
    #     data: Optional[Dict[str, Any]] = None, 
    #     filter_data: Optional[Dict[str, Any]] = None
    # ) -> Any:
    #     """
    #     Execute database operation with caching support and error handling.
    #     """
    #     try:
    #         if not self.cache:
    #             return await getattr(self.db_handler, operation)(
    #                 table_name=table_name,
    #                 data=data,
    #                 filter_data=filter_data
    #             )

    #         cache_key = self.cache_strategy.generate_key(table_name, filter_data or {})

    #         # Handle read operations
    #         if operation in ["get", "get_all"]:
    #             cached_result = await self.cache.get(cache_key)
    #             if cached_result is not None:
    #                 return cached_result

    #         # Execute database operation
    #         result = await getattr(self.db_handler, operation)(
    #             table_name=table_name,
    #             data=data,
    #             filter_data=filter_data
    #         )

    #         # Cache management for get operations
    #         if operation in ["get", "get_all"] and result:
    #             await self.cache.set(cache_key, result, self.cache_strategy.expiration_time)
    #         elif operation in ["update", "delete", "insert"]:
    #             await self.cache.invalidate(cache_key)

    #         return result
    #     except Exception as e:
    #         logging.error(f"Error executing operation {operation} on {table_name}: {e}")
    #         raise

    @safe_db_operation
    async def execute_operation(
        self,
        operation: str,
        table_name: str,
        data: Optional[Dict[str, Any]] = None,
        filter_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute database operation with caching support and error handling.
        """
        try:
            # Determine the correct arguments for the operation
            if operation in ["get", "get_all"]:
                args = {"table_name": table_name, "filter_data": filter_data}
            elif operation == "insert":
                args = {"table_name": table_name, "data": data, "filter_data": filter_data}
            elif operation == "update":
                args = {"table_name": table_name, "filter_data": filter_data, "update_data": data}
            elif operation == "delete":
                args = {"table_name": table_name, "filter_data": filter_data}
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            # Cache logic for read operations
            if self.cache and operation in ["get", "get_all"]:
                cache_key = self.cache_strategy.generate_key(table_name, filter_data or {})
                cached_result = await self.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

            # Execute database operation
            result = await getattr(self.db_handler, operation)(**args)

            # Cache management for read operations
            if self.cache and operation in ["get", "get_all"] and result:
                await self.cache.set(cache_key, result, self.cache_strategy.expiration_time)
            elif self.cache and operation in ["update", "delete", "insert"]:
                await self.cache.invalidate(cache_key)

            return result
        except Exception as e:
            logging.error(f"Error executing operation {operation} on {table_name}: {e}")
            raise


    async def get(self, table_name: str, filter_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """Retrieve a single record with caching."""
        # If in-memory storage
        if not self.db_handler:
            records = self.memory_store._collections[table_name]
            if not filter_data:
                return records
            return [
                record for record in records
                if all(record.get(k) == v for k, v in filter_data.items())
            ]

        # is using database        
        return await self.execute_operation("get", table_name, filter_data=filter_data)

    async def get_all(self, table_name: str, filter_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # If in-memory storage
        if not self.db_handler:
            records = self.memory_store._collections[table_name]
            if not filter_data:
                return records
            return [
                record for record in records
                if all(record.get(k) == v for k, v in filter_data.items())
            ]

        # is using database
        return await self.execute_operation("get_all", table_name, filter_data=filter_data)

    async def insert(self, table_name: str, data: Dict[str, Any]) -> Union[int, str]:
        # If in-memory storage
        if not self.db_handler:
            document = await self.memory_store.insert(table_name, data)
            return document["_id"]  # Return ID of inserted document

        # is using database
        return await self.execute_operation("insert", table_name, data=data)

    async def update(self, table_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        # If in-memory storage
        if not self.db_handler:
            updated_count = 0
            for record in self.memory_store._collections[table_name]:
                if all(record.get(k) == v for k, v in filter_data.items()):
                    record.update(update_data)
                    updated_count += 1
            return updated_count
        # is using database
        return await self.execute_operation("update", table_name, data=update_data, filter_data=filter_data)

    async def delete(self, table_name: str, filter_data: Dict[str, Any]) -> int:
        # If in-memory storage
        if not self.db_handler:
            original_count = len(self.memory_store._collections[table_name])
            self.memory_store._collections[table_name] = [
                record for record in self.memory_store._collections[table_name]
                if not all(record.get(k) == v for k, v in filter_data.items())
            ]
            return original_count - len(self.memory_store._collections[table_name])
        
        # is using database
        return await self.execute_operation("delete", table_name, filter_data=filter_data)

    async def raw_query(self, query: str) -> Union[List[Dict[str, Any]], str]:
        """Execute raw query (bypasses cache)."""
        try:
            logging.info(f"Executing raw query: {query}")
            return await self.db_handler.raw_query(query)
        except Exception as e:
            logging.error(f"Error executing raw query: {e}")
            raise

    async def get_table_schema(self, table_name: str = None) -> List[Dict[str, Any]]:
        """Get schema information for all tables or a specific table."""
        try:
            logging.info(f"Getting schema for table: {table_name or 'all tables'}")
            return await self.db_handler.get_table_schema(table_name)
        except Exception as e:
            logging.error(f"Error getting table schema: {e}")
            raise


    async def sync(self) -> None:
        """
        Synchronize all registered models with the database.
        Creates or updates tables as needed.
        """
        for model in self.models.values():
            await self.schema_manager.sync_model(model)
    
    def disable_cache(self):
        """Optional method to disable caching."""
        self.cache = None

    def enable_cache(self, cache: Any):
        """Optional method to enable caching."""
        self.cache = CacheDatabaseHandler(cache, None)

    async def transaction(self):
        """
        Start a new transaction.
        Usage:
            async with access_node.transaction() as txn:
                # perform operations
        """
        return await self.db_handler.transaction()
    

    async def close(self) -> None:
        """Close database and cache connections."""
        if self.db_handler:
            await self.db_handler.close()
        if self.cache:
            await self.cache.close()
        if self.db_pool:
            # Handle different pool types
            if hasattr(self.db_pool, 'close'):
                if asyncio.iscoroutinefunction(self.db_pool.close):
                    await self.db_pool.close()
                else:
                    self.db_pool.close()
            elif hasattr(self.db_pool, 'terminate'):
                # For aiomysql pools
                self.db_pool.terminate()
                await self.db_pool.wait_closed()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

