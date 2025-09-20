# acceessnode/database/pool.py
import asyncpg
import aiomysql
import motor.motor_asyncio
from typing import Any

class ConnectionPool:
    @staticmethod
    async def create_pool(db_type: str, **kwargs) -> Any:
        """
        Create a database connection pool based on the database type.
        """
        if db_type == 'postgresql':
            return await asyncpg.create_pool(
                user=kwargs.get('user'),
                password=kwargs.get('password'),
                database=kwargs.get('database'),
                host=kwargs.get('host', 'localhost')
            )
        elif db_type == 'mysql':
            # For MySQL, create a connection pool using aiomysql
            return await aiomysql.create_pool(
                user=kwargs.get('user'),
                password=kwargs.get('password'),
                db=kwargs.get('database'),
                host=kwargs.get('host', 'localhost'),
                port=kwargs.get('port', 3306),
                minsize=kwargs.get('minsize', 1),  # Minimum pool size
                maxsize=kwargs.get('maxsize', 10)  # Maximum pool size
            )
        elif db_type == 'mongodb':
            # For MongoDB, return a connection pool using Motor
            client = motor.motor_asyncio.AsyncIOMotorClient(
                kwargs.get('host', 'localhost'),
                username=kwargs.get('user'),
                password=kwargs.get('password')
            )
            return client[kwargs.get('database')]  # Return the database instance
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    