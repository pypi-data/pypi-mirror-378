# accessnode/postgresql.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Any, Dict, List, Union
from ..base import DatabaseHandler

class PostgresqlHandler(DatabaseHandler):
    def __init__(self,**kwargs):
        # Setup the async connection
        connection_string = f'postgresql+asyncpg://{kwargs.get("username", "postgres")}:{kwargs.get("password", "")}@{kwargs.get("host", "localhost")}:{kwargs.get("port", 5432)}/{kwargs.get("database", "")}'
        self.engine = create_async_engine(connection_string)
        self.AsyncSession = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_table(self, table_schema: str) -> None:
        async with self.AsyncSession() as session:
            await session.execute(text(table_schema))
            await session.commit()

    async def insert(self, table_name: str, data: Dict[str, Any], filter_data: Dict[str, Any] = None) -> int:
        async with self.AsyncSession() as session:
            columns = ', '.join(data.keys())
            values = ', '.join([f':{k}' for k in data.keys()])
            query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING id")
            result = await session.execute(query, data)
            await session.commit()
            return result.scalar_one()

    async def get(self, table_name: str, filter_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        async with self.AsyncSession() as session:
            conditions = ' AND '.join([f"{k} = :{k}" for k in filter_data.keys()])
            query = text(f"SELECT * FROM {table_name} WHERE {conditions}")
            result = await session.execute(query, filter_data)
            row = result.fetchone()
            return dict(row._mapping) if row else None

    async def get_all(self, table_name: str, filter_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        async with self.AsyncSession() as session:
            if filter_data:
                conditions = ' AND '.join([f"{k} = :{k}" for k in filter_data.keys()])
                query = text(f"SELECT * FROM {table_name} WHERE {conditions}")
                result = await session.execute(query, filter_data)
            else:
                query = text(f"SELECT * FROM {table_name}")
                result = await session.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def update(self, table_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        async with self.AsyncSession() as session:
            set_clause = ', '.join([f"{k} = :{k}" for k in update_data.keys()])
            where_clause = ' AND '.join([f"{k} = :filter_{k}" for k in filter_data.keys()])
            query = text(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}")
            params = {**update_data, **{f"filter_{k}": v for k, v in filter_data.items()}}
            result = await session.execute(query, params)
            await session.commit()
            return result.rowcount

    async def delete(self, table_name: str, filter_data: Dict[str, Any]) -> int:
        async with self.AsyncSession() as session:
            conditions = ' AND '.join([f"{k} = :{k}" for k in filter_data.keys()])
            query = text(f"DELETE FROM {table_name} WHERE {conditions}")
            result = await session.execute(query, filter_data)
            await session.commit()
            return result.rowcount

    async def raw_query(self, query: str) -> Union[List[Dict[str, Any]], str]:
        async with self.AsyncSession() as session:
            result = await session.execute(text(query))

            if result.returns_rows:
                # Use the result's keys along with the row values to safely create a dictionary
                rows = result.fetchall()
                if rows:
                    return [dict(row._mapping) for row in rows]  # _mapping ensures we get key-value pairs
                else:
                    return []
            else:
                await session.commit()  # DDL changes
                return "Done."

    async def get_table_schema(self, table_name: str = None) -> List[Dict[str, Any]]:
        """Get schema information for all tables or a specific table."""
        async with self.AsyncSession() as session:
            if table_name:
                query = text("""
                    SELECT
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        CASE
                            WHEN column_name IN (
                                SELECT kcu.column_name
                                FROM information_schema.key_column_usage kcu
                                JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name
                                WHERE tc.constraint_type = 'PRIMARY KEY' AND kcu.table_name = :table_name
                            ) THEN 'PRIMARY KEY'
                            WHEN column_name IN (
                                SELECT kcu.column_name
                                FROM information_schema.key_column_usage kcu
                                JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name
                                WHERE tc.constraint_type = 'FOREIGN KEY' AND kcu.table_name = :table_name
                            ) THEN 'FOREIGN KEY'
                            ELSE NULL
                        END as key_type
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """)
                result = await session.execute(query, {"table_name": table_name})
            else:
                # Get all tables in the database
                query = text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                result = await session.execute(query)

            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def close(self) -> None:
        await self.engine.dispose()
