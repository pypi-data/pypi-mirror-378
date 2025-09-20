from typing import Any, Dict, Callable, TypeVar, Union, Optional
from enum import Enum
from dataclasses import dataclass

class SchemaType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    OBJECT = "object"
    ARRAY = "array"

@dataclass
class SchemaField:
    type: SchemaType
    required: bool = True
    unique: bool = False
    default: Any = None
    ref: Optional[str] = None
    validate: Optional[Callable[[Any], bool]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "required": self.required,
            "unique": self.unique,
            "default": self.default,
            "ref": self.ref
        }

Schema = Dict[str, Union[SchemaField, SchemaType]]

@dataclass
class SchemaOptions:
    timestamps: bool = True
    soft_delete: bool = False
    strict: bool = True
    
    def to_dict(self) -> Dict[str, bool]:
        return {
            "timestamps": self.timestamps,
            "soft_delete": self.soft_delete,
            "strict": self.strict
        }