# accessnode/mysql.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Any, Dict, List, Union
from ..base import DatabaseHandler

class MySQLHandler(DatabaseHandler):
    def __init__(self, **kwargs):
        # Setup the connection
        # Handle both 'user' and 'username' parameters for compatibility
        username = kwargs.get('username') or kwargs.get('user', 'root')
        password = kwargs.get('password', '')
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 3306)
        database = kwargs.get('database', '')

        connection_string = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_async_engine(connection_string)
        self.AsyncSession = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    def create_table(self, table_schema: str) -> None:
        with self.Session() as session:
            session.execute(text(table_schema))
            session.commit()

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        with self.Session() as session:
            columns = ', '.join(data.keys())
            values = ', '.join([f':{k}' for k in data.keys()])
            query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
            result = session.execute(query, data)
            session.commit()
            return result.lastrowid

    def get(self, table_name: str, filter_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        with self.Session() as session:
            conditions = ' AND '.join([f"{k} = :{k}" for k in filter_data.keys()])
            query = text(f"SELECT * FROM {table_name} WHERE {conditions}")
            result = session.execute(query, filter_data)
            row = result.fetchone()
            return dict(row) if row else None

    def get_all(self, table_name: str, filter_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self.Session() as session:
            if filter_data:
                conditions = ' AND '.join([f"{k} = :{k}" for k in filter_data.keys()])
                query = text(f"SELECT * FROM {table_name} WHERE {conditions}")
                result = session.execute(query, filter_data)
            else:
                query = text(f"SELECT * FROM {table_name}")
                result = session.execute(query)
            return [dict(row) for row in result.fetchall()]

    def update(self, table_name: str, filter_data: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        with self.Session() as session:
            set_clause = ', '.join([f"{k} = :{k}" for k in update_data.keys()])
            where_clause = ' AND '.join([f"{k} = :filter_{k}" for k in filter_data.keys()])
            query = text(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}")
            params = {**update_data, **{f"filter_{k}": v for k, v in filter_data.items()}}
            result = session.execute(query, params)
            session.commit()
            return result.rowcount

    def delete(self, table_name: str, filter_data: Dict[str, Any]) -> int:
        with self.Session() as session:
            conditions = ' AND '.join([f"{k} = :{k}" for k in filter_data.keys()])
            query = text(f"DELETE FROM {table_name} WHERE {conditions}")
            result = session.execute(query, filter_data)
            session.commit()
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
                await session.commit()  # Commit DDL changes
                return "Done."

    async def get_table_schema(self, table_name: str = None) -> List[Dict[str, Any]]:
        """Get schema information for all tables or a specific table."""
        async with self.AsyncSession() as session:
            if table_name:
                query = text("""
                    SELECT
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        IS_NULLABLE as is_nullable,
                        COLUMN_DEFAULT as column_default,
                        CASE
                            WHEN COLUMN_KEY = 'PRI' THEN 'PRIMARY KEY'
                            WHEN COLUMN_KEY = 'MUL' THEN 'FOREIGN KEY'
                            ELSE NULL
                        END as key_type
                    FROM information_schema.columns
                    WHERE table_name = :table_name AND table_schema = DATABASE()
                    ORDER BY ordinal_position
                """)
                result = await session.execute(query, {"table_name": table_name})
            else:
                # Get schema information for all tables in the database
                query = text("""
                    SELECT
                        TABLE_NAME as table_name,
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        IS_NULLABLE as is_nullable,
                        COLUMN_DEFAULT as column_default,
                        CASE
                            WHEN COLUMN_KEY = 'PRI' THEN 'PRIMARY KEY'
                            WHEN COLUMN_KEY = 'MUL' THEN 'FOREIGN KEY'
                            ELSE NULL
                        END as key_type,
                        ORDINAL_POSITION as position
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE()
                    ORDER BY table_name, ORDINAL_POSITION
                """)
                result = await session.execute(query)

            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def close(self) -> None:
        await self.engine.dispose()
