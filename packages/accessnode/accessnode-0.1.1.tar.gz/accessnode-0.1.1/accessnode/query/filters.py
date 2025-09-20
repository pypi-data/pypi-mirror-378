# accessnode/query/filters.py
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

class FilterOperator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_NULL = "is_null"
    NOT_NULL = "not_null"
    BETWEEN = "between"

@dataclass
class Filter:
    field: str
    operator: FilterOperator
    value: Any

class FilterBuilder:
    def __init__(self):
        self.filters: List[Filter] = []
        self.or_groups: List[List[Filter]] = []

    def add(self, field: str, operator: FilterOperator, value: Any) -> 'FilterBuilder':
        """Add a filter condition"""
        self.filters.append(Filter(field, operator, value))
        return self

    def or_(self, *conditions: List[Filter]) -> 'FilterBuilder':
        """Add OR conditions"""
        self.or_groups.append(list(conditions))
        return self

    def build(self) -> Dict[str, Any]:
        """Build the filter dictionary"""
        result = {
            'and': [self._build_condition(f) for f in self.filters]
        }
        
        if self.or_groups:
            result['or'] = [
                {'and': [self._build_condition(f) for f in group]}
                for group in self.or_groups
            ]
            
        return result

    def _build_condition(self, filter: Filter) -> Dict[str, Any]:
        """Build a single filter condition"""
        return {
            'field': filter.field,
            'operator': filter.operator,
            'value': filter.value
        }

# Example usage:
# filters = (
#     FilterBuilder()
#     .add('age', FilterOperator.GTE, 18)
#     .add('status', FilterOperator.EQ, 'active')
#     .or_(
#         Filter('country', FilterOperator.EQ, 'US'),
#         Filter('country', FilterOperator.EQ, 'CA')
#     )
#     .build()
# )