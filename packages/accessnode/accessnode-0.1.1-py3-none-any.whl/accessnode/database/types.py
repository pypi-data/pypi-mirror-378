# acceessnode/database/types.py
from enum import Enum
from typing import Any, Dict, Type, Union, List


class DatabaseType:
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"

    @classmethod
    def get_supported_types(cls) -> List[str]:
        return [getattr(cls, attr) for attr in dir(cls) 
                if not attr.startswith("_") and isinstance(getattr(cls, attr), str)]

class QueryOperator(str, Enum):
    EQUALS = 'eq'
    NOT_EQUALS = 'neq'
    GT = 'gt'
    GTE = 'gte'
    LT = 'lt'
    LTE = 'lte'
    IN = 'in'
    NOT_IN = 'not_in'
    LIKE = 'like'
    ILIKE = 'ilike'
    CONTAINS = 'contains'
    STARTS_WITH = 'starts_with'
    ENDS_WITH = 'ends_with'
    IS_NULL = 'is_null'
    NOT_NULL = 'not_null'

class Field:
    """Base field type for model definitions"""
    def __init__(
        self,
        type: Type,
        required: bool = False,
        unique: bool = False,
        default: Any = None,
        index: bool = False,
        primary_key: bool = False
    ):
        self.type = type
        self.required = required
        self.unique = unique
        self.default = default
        self.index = index
        self.primary_key = primary_key

class Relation:
    """Base relation type for model definitions"""
    def __init__(
        self,
        model: str,
        type: str,
        foreign_key: str,
        local_key: str = 'id',
        through: str = None,
        through_fields: tuple[str, str] = None,
        cascade: bool = False,
        back_populates: str = None
    ):
        self.model = model
        self.type = type
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.through = through
        self.through_fields = through_fields
        self.cascade = cascade
        self.back_populates = back_populates

# Database specific types
DatabaseConfig = Dict[str, Any]
QueryResult = Union[Dict[str, Any], List[Dict[str, Any]]]