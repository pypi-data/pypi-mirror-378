# accessnode/schema_manager/schema_validator.py

"""Schema validation functionality."""
from typing import Dict, Any, List, Optional
import json

class SchemaValidator:
    """Validates database schemas and schema changes."""
    
    ALLOWED_TYPES = {
        'string', 'text', 'integer', 'float', 'decimal',
        'boolean', 'date', 'datetime', 'uuid', 'json', 'relation'
    }
    
    ALLOWED_RELATION_TYPES = {
        'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'
    }
    
    async def validate_schema(self, schema: Dict[str, Any]) -> List[str]:
        """
        Validate a complete schema definition.
        
        Example schema:
        {
            "name": "User",
            "fields": {
                "id": {"type": "uuid", "primary": true},
                "email": {"type": "string", "unique": true},
                "posts": {
                    "type": "relation",
                    "references": "Post",
                    "relation_type": "one_to_many"
                }
            }
        }
        """
        errors = []
        
        # Validate schema structure
        if not isinstance(schema, dict):
            errors.append("Schema must be a dictionary")
            return errors
            
        # Check required fields
        if 'name' not in schema:
            errors.append("Schema must have a name")
        elif not isinstance(schema['name'], str):
            errors.append("Schema name must be a string")
            
        if 'fields' not in schema:
            errors.append("Schema must have fields defined")
        elif not isinstance(schema['fields'], dict):
            errors.append("Fields must be a dictionary")
        else:
            # Validate each field
            for field_name, field_def in schema['fields'].items():
                field_errors = self._validate_field(field_name, field_def)
                errors.extend(field_errors)
                
        return errors
        
    async def validate_updates(
        self,
        schema_id: str,
        updates: Dict[str, Any]
    ) -> List[str]:
        """
        Validate proposed schema updates.
        
        Example updates:
        {
            "operations": [
                {
                    "type": "add_field",
                    "field": "status",
                    "definition": {"type": "string"}
                }
            ]
        }
        """
        errors = []
        
        if not isinstance(updates, dict):
            errors.append("Updates must be a dictionary")
            return errors
            
        if 'operations' not in updates:
            errors.append("Updates must contain operations")
            return errors
            
        for operation in updates['operations']:
            op_errors = self._validate_operation(operation)
            errors.extend(op_errors)
            
        return errors
        
    def _validate_field(
        self,
        field_name: str,
        field_def: Dict[str, Any]
    ) -> List[str]:
        """Validate field definition."""
        errors = []
        
        if not isinstance(field_def, dict):
            errors.append(f"Field '{field_name}' definition must be a dictionary")
            return errors
            
        if 'type' not in field_def:
            errors.append(f"Field '{field_name}' must specify type")
        elif field_def['type'] not in self.ALLOWED_TYPES:
            errors.append(
                f"Field '{field_name}' has invalid type. "
                f"Allowed types: {', '.join(self.ALLOWED_TYPES)}"
            )
            
        if field_def['type'] == 'relation':
            if 'references' not in field_def:
                errors.append(
                    f"Relation field '{field_name}' must specify references"
                )
            if 'relation_type' not in field_def:
                errors.append(
                    f"Relation field '{field_name}' must specify relation_type"
                )
            elif field_def['relation_type'] not in self.ALLOWED_RELATION_TYPES:
                errors.append(
                    f"Relation field '{field_name}' has invalid relation_type. "
                    f"Allowed types: {', '.join(self.ALLOWED_RELATION_TYPES)}"
                )
                
        return errors
        
    def _validate_operation(self, operation: Dict[str, Any]) -> List[str]:
        """Validate update operation."""
        errors = []
        
        if not isinstance(operation, dict):
            errors.append("Operation must be a dictionary")
            return errors
            
        if 'type' not in operation:
            errors.append("Operation must specify type")
        elif operation['type'] not in {'add_field', 'modify_field', 'remove_field', 'add_relation'}:
            errors.append("Invalid operation type")
            
        if operation['type'] in {'add_field', 'modify_field'}:
            if 'field' not in operation:
                errors.append("Operation must specify field name")
            if 'definition' not in operation:
                errors.append("Operation must include field definition")
            else:
                field_errors = self._validate_field(
                    operation['field'],
                    operation['definition']
                )
                errors.extend(field_errors)
                
        elif operation['type'] == 'remove_field':
            if 'field' not in operation:
                errors.append("Remove operation must specify field name")
                
        elif operation['type'] == 'add_relation':
            if 'field' not in operation:
                errors.append("Relation operation must specify field name")
            if 'references' not in operation:
                errors.append("Relation operation must specify references")
            if 'relation_type' not in operation:
                errors.append("Relation operation must specify relation_type")
            elif operation['relation_type'] not in self.ALLOWED_RELATION_TYPES:
                errors.append(
                    f"Invalid relation_type. "
                    f"Allowed types: {', '.join(self.ALLOWED_RELATION_TYPES)}"
                )
                
        return errors