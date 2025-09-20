# accessnode/schema_manager/schema_updater.py

"""Schema update functionality."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .schema_validator import SchemaValidator

class SchemaUpdater:
    """Handles updates to existing database schemas."""
    
    def __init__(self, database_pool):
        self.db_pool = database_pool
        self.validator = SchemaValidator()
        
    async def update_schema(
        self,
        schema_id: str,
        updates: Dict[str, Any],
        validate: bool = True
    ) -> None:
        """
        Update an existing schema.
        
        Example updates:
        {
            "operations": [
                {
                    "type": "add_field",
                    "field": "status",
                    "definition": {"type": "string", "default": "active"}
                },
                {
                    "type": "modify_field",
                    "field": "email",
                    "definition": {"type": "string", "unique": true}
                },
                {
                    "type": "remove_field",
                    "field": "temporary_field"
                },
                {
                    "type": "add_relation",
                    "field": "comments",
                    "references": "Comment",
                    "relation_type": "one_to_many"
                }
            ]
        }
        """
        if validate:
            await self.validator.validate_updates(schema_id, updates)
            
        # Get current schema version
        current_version = await self.get_schema_version(schema_id)
        current_schema = await self._get_schema_definition(schema_id)
        
        # Apply updates to schema definition
        updated_schema = self._apply_updates(current_schema, updates)
        
        # Generate and execute update statements
        statements = self._generate_update_statements(
            current_schema,
            updated_schema,
            updates
        )
        
        async with self.db_pool.get_connection() as conn:
            # Execute schema updates
            for statement in statements:
                await conn.execute(statement)
                
            # Store new schema version
            await conn.execute(
                """
                INSERT INTO schema_versions 
                (schema_id, version, definition)
                VALUES ($1, $2, $3)
                """,
                [
                    schema_id,
                    current_version + 1,
                    updated_schema
                ]
            )
            
    async def get_schema_version(self, schema_id: str) -> int:
        """Get current version of schema."""
        async with self.db_pool.get_connection() as conn:
            result = await conn.execute(
                """
                SELECT MAX(version) as version 
                FROM schema_versions 
                WHERE schema_id = $1
                """,
                [schema_id]
            )
            return result['version'] or 0
            
    async def _get_schema_definition(self, schema_id: str) -> Dict[str, Any]:
        """Get current schema definition."""
        async with self.db_pool.get_connection() as conn:
            result = await conn.execute(
                """
                SELECT definition
                FROM schema_versions
                WHERE schema_id = $1
                ORDER BY version DESC
                LIMIT 1
                """,
                [schema_id]
            )
            return result['definition']
            
    def _apply_updates(
        self,
        current_schema: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply updates to schema definition."""
        updated_schema = current_schema.copy()
        
        for operation in updates['operations']:
            op_type = operation['type']
            
            if op_type == 'add_field':
                updated_schema['fields'][operation['field']] = operation['definition']
            elif op_type == 'modify_field':
                updated_schema['fields'][operation['field']] = operation['definition']
            elif op_type == 'remove_field':
                del updated_schema['fields'][operation['field']]
            elif op_type == 'add_relation':
                updated_schema['fields'][operation['field']] = {
                    'type': 'relation',
                    'references': operation['references'],
                    'relation_type': operation['relation_type']
                }
                
        return updated_schema
        
    def _generate_update_statements(
        self,
        current_schema: Dict[str, Any],
        updated_schema: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> List[str]:
        """Generate SQL statements for schema updates."""
        statements = []
        table_name = current_schema['name'].lower()
        
        for operation in updates['operations']:
            op_type = operation['type']
            
            if op_type == 'add_field':
                field_def = self._generate_field_definition(
                    operation['field'],
                    operation['definition']
                )
                statements.append(
                    f"ALTER TABLE {table_name} ADD COLUMN {field_def}"
                )
            elif op_type == 'modify_field':
                field_def = self._generate_field_definition(
                    operation['field'],
                    operation['definition']
                )
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {field_def}"
                )
            elif op_type == 'remove_field':
                statements.append(
                    f"ALTER TABLE {table_name} DROP COLUMN {operation['field']}"
                )
            elif op_type == 'add_relation':
                if operation['relation_type'] == 'many_to_one':
                    statements.extend([
                        f"ALTER TABLE {table_name} ADD COLUMN {operation['field']}_id UUID",
                        f"ALTER TABLE {table_name} ADD CONSTRAINT fk_{table_name}_{operation['field']} "
                        f"FOREIGN KEY ({operation['field']}_id) "
                        f"REFERENCES {operation['references'].lower()}(id)"
                    ])
                    
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