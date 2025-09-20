from typing import Any, Dict
from .types import Schema, SchemaType, SchemaField
from .exceptions import ValidationError

class SchemaValidator:
    @staticmethod
    def validate_field(value: Any, field_def: SchemaField) -> bool:
        """Validate a single field against its schema definition."""
        if value is None:
            if field_def.required:
                raise ValidationError(f"Field is required")
            return True

        # Type validation
        if not SchemaValidator._validate_type(value, field_def.type):
            raise ValidationError(f"Invalid type. Expected {field_def.type.value}")

        # Custom validation
        if field_def.validate and not field_def.validate(value):
            raise ValidationError("Custom validation failed")

        return True

    @staticmethod
    def validate_schema(data: Dict[str, Any], schema: Schema) -> bool:
        """Validate entire data object against schema."""
        for field_name, field_def in schema.items():
            if isinstance(field_def, SchemaType):
                field_def = SchemaField(type=field_def)

            value = data.get(field_name)
            SchemaValidator.validate_field(value, field_def)

        return True

    @staticmethod
    def _validate_type(value: Any, expected_type: SchemaType) -> bool:
        type_checks = {
            SchemaType.STRING: lambda x: isinstance(x, str),
            SchemaType.NUMBER: lambda x: isinstance(x, (int, float)),
            SchemaType.BOOLEAN: lambda x: isinstance(x, bool),
            SchemaType.DATE: lambda x: isinstance(x, (str, int)) or hasattr(x, 'isoformat'),
            SchemaType.OBJECT: lambda x: isinstance(x, dict),
            SchemaType.ARRAY: lambda x: isinstance(x, (list, tuple))
        }
        
        return type_checks[expected_type](value)