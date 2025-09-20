# accessnode/schema_manager/schema_migration.py
"""Schema migration functionality."""
from typing import Dict, Any, List, Optional, Union
import json
from datetime import datetime

class SchemaMigrations:
    """Handles database schema migrations."""
    
    def __init__(self, database_pool):
        self.db_pool = database_pool
        
    async def initialize(self):
        """Initialize migration tracking tables."""
        async with self.db_pool.get_connection() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_id VARCHAR(255) NOT NULL UNIQUE,
                    schema_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    changes JSONB NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_at TIMESTAMP,
                    checksum VARCHAR(64) NOT NULL
                )
            """)
            
    async def create_migration(
        self,
        schema_id: str,
        name: str,
        changes: Dict[str, Any],
        description: Optional[str] = None
    ) -> str:
        """
        Create a new migration.
        
        Example changes:
        {
            "up": [
                {
                    "type": "add_field",
                    "table": "users",
                    "field": "status",
                    "definition": {"type": "string", "default": "'active'"}
                }
            ],
            "down": [
                {
                    "type": "remove_field",
                    "table": "users",
                    "field": "status"
                }
            ]
        }
        """
        migration_id = self._generate_migration_id(name)
        checksum = self._generate_checksum(changes)
        
        async with self.db_pool.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO schema_migrations 
                (migration_id, schema_id, name, description, changes, checksum)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                [
                    migration_id,
                    schema_id,
                    name,
                    description,
                    json.dumps(changes),
                    checksum
                ]
            )
            
        return migration_id
        
    async def apply_migration(
        self,
        migration_id: str,
        direction: str = 'up',
        dry_run: bool = False
    ) -> Union[List[str], None]:
        """Apply a migration to the database."""
        async with self.db_pool.get_connection() as conn:
            # Get migration details
            migration = await conn.execute(
                "SELECT * FROM schema_migrations WHERE migration_id = $1",
                [migration_id]
            )
            
            if not migration:
                raise ValueError(f"Migration {migration_id} not found")
                
            changes = json.loads(migration['changes'])
            statements = self._generate_migration_statements(
                changes[direction]
            )
            
            if dry_run:
                return statements
                
            try:
                # Execute migration
                for statement in statements:
                    await conn.execute(statement)
                    
                # Update migration status
                status = 'applied' if direction == 'up' else 'reverted'
                await self._update_migration_status(
                    migration_id,
                    status,
                    conn
                )
            except Exception as e:
                await conn.execute(
                    """
                    UPDATE schema_migrations 
                    SET status = 'failed', 
                        error = $1
                    WHERE migration_id = $2
                    """,
                    [str(e), migration_id]
                )
                raise
                
        return None
        
    async def get_pending_migrations(self, schema_id: str) -> List[Dict[str, Any]]:
        """Get list of pending migrations."""
        async with self.db_pool.get_connection() as conn:
            result = await conn.execute(
                """
                SELECT migration_id, name, description
                FROM schema_migrations
                WHERE schema_id = $1
                AND status = 'pending'
                ORDER BY created_at ASC
                """,
                [schema_id]
            )
            return result
            
    def _generate_migration_id(self, name: str) -> str:
        """Generate unique migration identifier."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        safe_name = name.lower().replace(' ', '_')
        return f"{timestamp}_{safe_name}"
        
    def _generate_checksum(self, changes: Dict[str, Any]) -> str:
        """Generate checksum for migration changes."""
        import hashlib
        changes_str = json.dumps(changes, sort_keys=True)
        return hashlib.sha256(changes_str.encode()).hexdigest()
        
    def _generate_migration_statements(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate SQL statements for migration."""
        statements = []
        
        for operation in operations:
            op_type = operation['type']
            
            if op_type == 'add_field':
                field_def = self._generate_field_definition(
                    operation['field'],
                    operation['definition']
                )
                statements.append(
                    f"ALTER TABLE {operation['table']} "
                    f"ADD COLUMN {field_def}"
                )
            elif op_type == 'modify_field':
                field_def = self._generate_field_definition(
                    operation['field'],
                    operation['definition']
                )
                statements.append(
                    f"ALTER TABLE {operation['table']} "
                    f"ALTER COLUMN {field_def}"
                )
            elif op_type == 'remove_field':
                statements.append(
                    f"ALTER TABLE {operation['table']} "
                    f"DROP COLUMN {operation['field']}"
                )
            elif op_type == 'create_table':
                fields = []
                for field_name, field_def in operation['fields'].items():
                    fields.append(
                        self._generate_field_definition(field_name, field_def)
                    )
                statements.append(
                    f"CREATE TABLE {operation['table']} "
                    f"({', '.join(fields)})"
                )
            elif op_type == 'drop_table':
                statements.append(
                    f"DROP TABLE {operation['table']}"
                )
                
        return statements
        
    def _generate_field_definition(
        self,
        field_name: str,
        field_def: Dict[str, Any]
    ) -> str:
        """Generate field definition SQL."""
        parts = [field_name]
        
        if 'type' in field_def:
            sql_type = self._map_type(field_def['type'])
            parts.append(sql_type)
            
        if field_def.get('primary'):
            parts.append('PRIMARY KEY')
            
        if field_def.get('unique'):
            parts.append('UNIQUE')
            
        if 'default' in field_def:
            parts.append(f"DEFAULT {field_def['default']}")
            
        return ' '.join(parts)
        
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
        
    async def _update_migration_status(
        self,
        migration_id: str,
        status: str,
        connection = None
    ) -> None:
        """Update migration status."""
        async with self.db_pool.get_connection() as conn:
            await conn.execute(
                """
                UPDATE schema_migrations 
                SET status = $1,
                    applied_at = CASE 
                        WHEN $1 = 'applied' THEN CURRENT_TIMESTAMP 
                        ELSE NULL 
                    END
                WHERE migration_id = $2
                """,
                [status, migration_id]
            )