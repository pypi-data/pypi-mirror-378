# accessnode/models/fields.py
import uuid
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from ..core.exceptions import ValidationError

T = TypeVar('T', bound='BaseField')

class BaseField:
    def __init__(
        self,
        required: bool = False,
        unique: bool = False,
        default: Any = None,
        index: bool = False,
        validators: List[callable] = None
    ):
        self.required = required
        self.unique = unique
        self.default = default
        self.index = index
        self.validators = validators or []

    def validate(self, value: Any) -> Any:
        """Validate field value."""
        if value is None:
            if self.required:
                raise ValidationError(f"Field is required")
            return self.default

        for validator in self.validators:
            value = validator(value)
        return value

class StringField(BaseField):
    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern

    def validate(self, value: Any) -> str:
        value = super().validate(value)
        if value is None:
            return value

        if not isinstance(value, str):
            raise ValidationError("Value must be a string")

        if self.min_length and len(value) < self.min_length:
            raise ValidationError(f"String length must be at least {self.min_length}")

        if self.max_length and len(value) > self.max_length:
            raise ValidationError(f"String length must be at most {self.max_length}")

        if self.pattern:
            import re
            if not re.match(self.pattern, value):
                raise ValidationError(f"String must match pattern: {self.pattern}")

        return value

class IntegerField(BaseField):
    def __init__(
        self,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> int:
        value = super().validate(value)
        if value is None:
            return value

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Value must be an integer")

        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Value must be at least {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Value must be at most {self.max_value}")

        return value

class UUIDField(BaseField):
    def __init__(self, auto_generate: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.auto_generate = auto_generate

    def validate(self, value: Any) -> uuid.UUID:
        if value is None and self.auto_generate:
            return uuid.uuid4()

        value = super().validate(value)
        if value is None:
            return value

        try:
            if isinstance(value, str):
                return uuid.UUID(value)
            elif isinstance(value, uuid.UUID):
                return value
            else:
                raise ValidationError("Invalid UUID format")
        except ValueError:
            raise ValidationError("Invalid UUID format")

class DateTimeField(BaseField):
    def __init__(
        self,
        auto_now: bool = False,
        auto_now_add: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def validate(self, value: Any) -> datetime:
        if (value is None and self.auto_now_add) or self.auto_now:
            return datetime.utcnow()

        value = super().validate(value)
        if value is None:
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValidationError("Invalid datetime format")

        if not isinstance(value, datetime):
            raise ValidationError("Value must be a datetime object")

        return value

class RelationField(BaseField):
    def __init__(
        self,
        model: str,
        relation_type: str = 'many_to_one',
        foreign_key: Optional[str] = None,
        back_populates: Optional[str] = None,
        cascade_delete: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model = model
        self.relation_type = relation_type
        self.foreign_key = foreign_key
        self.back_populates = back_populates
        self.cascade_delete = cascade_delete

class JsonField(BaseField):
    def __init__(self, schema: Optional[Type[BaseModel]] = None, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema

    def validate(self, value: Any) -> Dict:
        value = super().validate(value)
        if value is None:
            return value

        if self.schema:
            try:
                return self.schema(**value).dict()
            except Exception as e:
                raise ValidationError(f"JSON validation failed: {str(e)}")

        if not isinstance(value, (dict, list)):
            raise ValidationError("Value must be a valid JSON object or array")

        return value







































# from typing import Any, Optional, Type
# from datetime import datetime
# from uuid import UUID

# class Field:
#     def __init__(
#         self,
#         type: Type,
#         required: bool = False,
#         unique: bool = False,
#         default: Any = None,
#         index: bool = False,
#         primary_key: bool = False
#     ):
#         self.type = type
#         self.required = required
#         self.unique = unique
#         self.default = default
#         self.index = index
#         self.primary_key = primary_key

# class StringField(Field):
#     def __init__(
#         self,
#         max_length: Optional[int] = None,
#         min_length: Optional[int] = None,
#         **kwargs
#     ):
#         super().__init__(type=str, **kwargs)
#         self.max_length = max_length
#         self.min_length = min_length

# class IntegerField(Field):
#     def __init__(
#         self,
#         min_value: Optional[int] = None,
#         max_value: Optional[int] = None,
#         **kwargs
#     ):
#         super().__init__(type=int, **kwargs)
#         self.min_value = min_value
#         self.max_value = max_value

# class UUIDField(Field):
#     def __init__(self, **kwargs):
#         super().__init__(type=UUID, **kwargs)

# class DateTimeField(Field):
#     def __init__(
#         self,
#         auto_now: bool = False,
#         auto_now_add: bool = False,
#         **kwargs
#     ):
#         super().__init__(type=datetime, **kwargs)
#         self.auto_now = auto_now
#         self.auto_now_add = auto_now_add

# class BooleanField(Field):
#     def __init__(self, **kwargs):
#         super().__init__(type=bool, **kwargs)

# class JsonField(Field):
#     def __init__(self, **kwargs):
#         super().__init__(type=dict, **kwargs)

# class ArrayField(Field):
#     def __init__(
#         self,
#         item_type: Type,
#         **kwargs
#     ):
#         super().__init__(type=list, **kwargs)
#         self.item_type = item_type