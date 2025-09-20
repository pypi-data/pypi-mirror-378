from enum import Enum
from typing import Any, List, Dict, Union, Optional

class JoinType(Enum):
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL JOIN"

class OrderDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"

class Operator(Enum):
    EQ = "="
    NEQ = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    LIKE = "LIKE"
    ILIKE = "ILIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"
    EXISTS = "EXISTS"
    ANY = "ANY"
    ALL = "ALL"

class WhereClause:
    def __init__(
        self,
        field: str,
        operator: Operator,
        value: Any,
        is_or: bool = False
    ):
        self.field = field
        self.operator = operator
        self.value = value
        self.is_or = is_or

class JoinClause:
    def __init__(
        self,
        table: str,
        type: JoinType,
        conditions: List[WhereClause]
    ):
        self.table = table
        self.type = type
        self.conditions = conditions

class OrderByClause:
    def __init__(
        self,
        field: str,
        direction: OrderDirection = OrderDirection.ASC
    ):
        self.field = field
        self.direction = direction

QueryValue = Union[str, int, float, bool, None, List[Any], Dict[str, Any]]