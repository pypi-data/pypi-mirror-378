# accessnode/sqlite.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Any, Dict, List, Union
from ..base import DatabaseHandler


class SQLiteHandler(DatabaseHandler):
    def __init__(self, **kwargs):
        # Setup the connection
        connection_string = f'sqlite:///{kwargs.get("database", "")}'
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

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

    def raw_query(self, query: str) -> Union[List[Dict[str, Any]], str]:
        with self.Session() as session:
            result = session.execute(text(query))

            if result.returns_rows:
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows] if rows else []
            else:
                session.commit()
                return "Done."

    async def get_table_schema(self, table_name: str = None) -> List[Dict[str, Any]]:
        """Get schema information for all tables or a specific table."""
        with self.Session() as session:
            if table_name:
                query = text("""
                    SELECT
                        name as column_name,
                        type as data_type,
                        "notnull" as is_nullable,
                        dflt_value as column_default,
                        CASE WHEN pk = 1 THEN 'PRIMARY KEY' ELSE NULL END as key_type
                    FROM pragma_table_info(:table_name)
                """)
                result = session.execute(query, {"table_name": table_name})
            else:
                # Get all tables in the database
                query = text("""
                    SELECT name as table_name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                result = session.execute(query)

            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    def close(self) -> None:
        self.engine.dispose()
