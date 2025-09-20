# accessnode/schema_manager/schema_creator.py
"""Schema creation functionality."""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from asyncpg.pool import Pool
import asyncpg


# Create the database pool function
async def create_pool() -> Pool:
    return await asyncpg.create_pool(
        user='your_username',
        password='your_password',
        database='your_database',
        host='localhost'
    )


class SchemaCreator:
    """Handles creation of new database schemas."""
    
    def __init__(self, database_pool: Pool):
        self.db_pool = database_pool
        
    async def create_schema(self, schema_definition: Dict[str, Any]) -> str:
        """
        Create a new schema from definition.
        
        Example schema definition:
        {
            "name": "User",
            "fields": {
                "id": {"type": "uuid", "primary": true, "default": "uuid_generate_v4()"},
                "email": {"type": "string", "unique": true},
                "name": {"type": "string"},
                "posts": {
                    "type": "relation",
                    "references": "Post",
                    "relation_type": "one_to_many"
                }
            },
            "indexes": [
                {"fields": ["email"], "type": "unique"}
            ]
        }
        """
        schema_id = self._generate_schema_id(schema_definition)
        
        # Generate DDL statements
        ddl_statements = self._generate_ddl(schema_definition)
        
        # Execute schema creation
        async with self.db_pool.get_connection() as conn:
            # Create schema version tracking
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_versions (
                    id SERIAL PRIMARY KEY,
                    schema_id VARCHAR(255) NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    definition JSONB NOT NULL
                )
            """)
            
            # Store schema definition
            await conn.execute(
                """
                INSERT INTO schema_versions (schema_id, version, definition)
                VALUES ($1, 1, $2)
                """,
                [schema_id, json.dumps(schema_definition)]
            )
            
            # Execute schema DDL
            for statement in ddl_statements:
                await conn.execute(statement)
                
        return schema_id
        
    def _generate_schema_id(self, schema_definition: Dict[str, Any]) -> str:
        """Generate unique schema identifier."""
        name = schema_definition.get('name', '').lower()
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{name}_{timestamp}"
        
    def _generate_ddl(self, schema_definition: Dict[str, Any]) -> List[str]:
        """Generate DDL statements from schema definition."""
        statements = []
        table_name = schema_definition['name'].lower()
        
        # Start table creation
        fields = []
        constraints = []
        
        for field_name, field_def in schema_definition['fields'].items():
            field_type = field_def['type']
            
            if field_type == 'relation':
                # Handle relations
                ref_table = field_def['references'].lower()
                rel_type = field_def['relation_type']
                
                if rel_type == 'many_to_one':
                    fields.append(f"{field_name}_id UUID")
                    constraints.append(
                        f"FOREIGN KEY ({field_name}_id) REFERENCES {ref_table}(id)"
                    )
            else:
                # Handle regular fields
                sql_type = self._map_type(field_type)
                field_parts = [f"{field_name} {sql_type}"]
                
                if field_def.get('primary'):
                    field_parts.append("PRIMARY KEY")
                if field_def.get('unique'):
                    field_parts.append("UNIQUE")
                if field_def.get('default'):
                    field_parts.append(f"DEFAULT {field_def['default']}")
                    
                fields.append(" ".join(field_parts))
                
        # Create table
        create_table = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {','.join(fields + constraints)}
            )
        """
        statements.append(create_table)
        
        # Create indexes
        for index in schema_definition.get('indexes', []):
            idx_name = f"idx_{table_name}_{'_'.join(index['fields'])}"
            idx_type = 'UNIQUE' if index.get('type') == 'unique' else ''
            idx_fields = ', '.join(index['fields'])
            
            create_index = f"""
                CREATE {idx_type} INDEX IF NOT EXISTS {idx_name}
                ON {table_name} ({idx_fields})
            """
            statements.append(create_index)
            
        return statements
        
    def _map_type(self, schema_type: str) -> str:
        """Map schema types to SQL types."""
        type_mapping = {
            'string': 'VARCHAR(255)',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'float': 'FLOAT',
            'decimal': 'DECIMAL',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'datetime': 'TIMESTAMP',
            'uuid': 'UUID',
            'json': 'JSONB'
        }
        return type_mapping.get(schema_type.lower(), 'VARCHAR(255)')