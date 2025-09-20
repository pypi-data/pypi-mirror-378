# accessnode/schema_manager/schema_manager.py
from .schema_creator import SchemaCreator
from .schema_updater import SchemaUpdater
from .schema_validator import SchemaValidator
from .schema_migration import SchemaMigrations
from typing import Dict, Any
from asyncpg.pool import Pool

class SchemaManager:
    def __init__(self, database_pool: Pool):
        # Pass the database pool to the relevant components
        self.creator = SchemaCreator(database_pool)
        self.updater = SchemaUpdater(database_pool)
        self.validator = SchemaValidator()
        self.migrations = SchemaMigrations(database_pool)

    def create_schema(self, schema_name: str, schema_fields: Dict[str, Any]) -> None:
        """
        Create a new schema.
        """
        return self.creator.create(schema_name, schema_fields)

    def update_schema(self, schema_name: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing schema.
        """
        return self.updater.update(schema_name, updates)

    def validate_schema(self, schema_data: Dict[str, Any]) -> bool:
        """
        Validate schema data to ensure compatibility.
        """
        return self.validator.validate(schema_data)

    def migrate_schema(self, schema_name: str, migration_instructions: Dict[str, Any]) -> None:
        """
        Apply migrations to an existing schema.
        """
        return self.migrations.migrate(schema_name, migration_instructions)

    # async def alter_schema(self, 
    #     model: Type[BaseModel], 
    #     changes: Dict[str, Any]
    # ) -> None:
    #     """Alter existing schema"""
    #     migration = self.migration_manager.create_migration(
    #         model, changes
    #     )
    #     await self.migration_manager.apply_migration(migration)
    
    # async def drop_schema(self, model: Type[BaseModel]) -> None:
    #     """Drop database schema"""
    #     await self.connection.execute(
    #         f"DROP TABLE IF EXISTS {model.table_name()}"
    #     )