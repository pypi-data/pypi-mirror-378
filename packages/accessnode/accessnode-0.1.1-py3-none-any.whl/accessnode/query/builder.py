# from typing import Any, List, Dict, Optional, TypeVar, Generic, Type
# from .types import (
#     JoinType, OrderDirection, Operator, WhereClause,
#     JoinClause, OrderByClause, QueryValue
# )
# from ..models.base import BaseModel
# from ..core.exceptions import QueryError

# T = TypeVar('T', bound=BaseModel)

# class QueryBuilder(Generic[T]):
#     def __init__(self, model_class: Type[T]):
#         self.model = model_class
#         self.selected_fields: List[str] = []
#         self.where_clauses: List[WhereClause] = []
#         self.join_clauses: List[JoinClause] = []
#         self.order_by_clauses: List[OrderByClause] = []
#         self.group_by_fields: List[str] = []
#         self.having_clauses: List[WhereClause] = []
#         self._limit: Optional[int] = None
#         self._offset: Optional[int] = None
#         self._distinct: bool = False

#     def select(self, *fields: str) -> 'QueryBuilder[T]':
#         """Select specific fields."""
#         self.selected_fields.extend(fields)
#         return self

#     def distinct(self) -> 'QueryBuilder[T]':
#         """Make the query distinct."""
#         self._distinct = True
#         return self

#     def where(
#         self,
#         field: str,
#         operator: Operator,
#         value: QueryValue
#     ) -> 'QueryBuilder[T]':
#         """Add WHERE clause."""
#         self.where_clauses.append(
#             WhereClause(field, operator, value)
#         )
#         return self

#     def or_where(
#         self,
#         field: str,
#         operator: Operator,
#         value: QueryValue
#     ) -> 'QueryBuilder[T]':
#         """Add OR WHERE clause."""
#         self.where_clauses.append(
#             WhereClause(field, operator, value, is_or=True)
#         )
#         return self

#     def where_in(self, field: str, values: List[Any]) -> 'QueryBuilder[T]':
#         """Add WHERE IN clause."""
#         return self.where(field, Operator.IN, values)

#     def where_not_in(self, field: str, values: List[Any]) -> 'QueryBuilder[T]':
#         """Add WHERE NOT IN clause."""
#         return self.where(field, Operator.NOT_IN, values)

#     def where_null(self, field: str) -> 'QueryBuilder[T]':
#         """Add WHERE IS NULL clause."""
#         return self.where(field, Operator.IS_NULL, None)

#     def where_not_null(self, field: str) -> 'QueryBuilder[T]':
#         """Add WHERE IS NOT NULL clause."""
#         return self.where(field, Operator.IS_NOT_NULL, None)

#     def where_between(
#         self,
#         field: str,
#         start: Any,
#         end: Any
#     ) -> 'QueryBuilder[T]':
#         """Add WHERE BETWEEN clause."""
#         return self.where(field, Operator.BETWEEN, [start, end])

#     def join(
#         self,
#         table: str,
#         field: str,
#         operator: Operator,
#         value: str,
#         type: JoinType = JoinType.INNER
#     ) -> 'QueryBuilder[T]':
#         """Add JOIN clause."""
#         self.join_clauses.append(
#             JoinClause(
#                 table,
#                 type,
#                 [WhereClause(field, operator, value)]
#             )
#         )
#         return self

#     def left_join(
#         self,
#         table: str,
#         field: str,
#         operator: Operator,
#         value: str
#     ) -> 'QueryBuilder[T]':
#         """Add LEFT JOIN clause."""
#         return self.join(table, field, operator, value, JoinType.LEFT)

#     def right_join(
#         self,
#         table: str,
#         field: str,
#         operator: Operator,
#         value: str
#     ) -> 'QueryBuilder[T]':
#         """Add RIGHT JOIN clause."""
#         return self.join(table, field, operator, value, JoinType.RIGHT)

#     def order_by(
#         self,
#         field: str,
#         direction: OrderDirection = OrderDirection.ASC
#     ) -> 'QueryBuilder[T]':
#         """Add ORDER BY clause."""
#         self.order_by_clauses.append(OrderByClause(field, direction))
#         return self

#     def group_by(self, *fields: str) -> 'QueryBuilder[T]':
#         """Add GROUP BY clause."""
#         self.group_by_fields.extend(fields)
#         return self

#     def having(
#         self,
#         field: str,
#         operator: Operator,
#         value: QueryValue
#     ) -> 'QueryBuilder[T]':
#         """Add HAVING clause."""
#         self.having_clauses.append(
#             WhereClause(field, operator, value)
#         )
#         return self

#     def limit(self, limit: int) -> 'QueryBuilder[T]':
#         """Set LIMIT clause."""
#         if limit < 0:
#             raise QueryError("Limit must be non-negative")
#         self._limit = limit
#         return self

#     def offset(self, offset: int) -> 'QueryBuilder[T]':
#         """Set OFFSET clause."""
#         if offset < 0:
#             raise QueryError("Offset must be non-negative")
#         self._offset = offset
#         return self

#     def paginate(self, page: int, per_page: int = 20) -> 'QueryBuilder[T]':
#         """Add pagination."""
#         if page < 1:
#             raise QueryError("Page must be positive")
#         if per_page < 1:
#             raise QueryError("Items per page must be positive")
        
#         self._limit = per_page
#         self._offset = (page - 1) * per_page
#         return self

#     async def count(self) -> int:
#         """Get count of records."""
#         original_fields = self.selected_fields.copy()
#         self.selected_fields = ["COUNT(*) as count"]
#         result = await self.first()
#         self.selected_fields = original_fields
#         return result.count if result else 0

#     async def exists(self) -> bool:
#         """Check if any records exist."""
#         return await self.count() > 0

#     async def first(self) -> Optional[T]:
#         """Get first record."""
#         self._limit = 1
#         results = await self.get()
#         return results[0] if results else None

#     async def first_or_fail(self) -> T:
#         """Get first record or raise exception."""
#         result = await self.first()
#         if not result:
#             raise QueryError("No records found")
#         return result

#     async def get(self) -> List[T]:
#         """Execute query and get results."""
#         # This will be implemented by each database adapter
#         pass

#     async def update(self, data: Dict[str, Any]) -> int:
#         """Update records matching query."""
#         # This will be implemented by each database adapter
#         pass

#     async def delete(self) -> int:
#         """Delete records matching query."""
#         # This will be implemented by each database adapter
#         pass

#     def clone(self) -> 'QueryBuilder[T]':
#         """Create a clone of the current query."""
#         new_query = QueryBuilder(self.model)
#         new_query.selected_fields = self.selected_fields.copy()
#         new_query.where_clauses = self.where_clauses.copy()
#         new_query.join_clauses = self.join_clauses.copy()
#         new_query.order_by_clauses = self.order_by_clauses.copy()
#         new_query.group_by_fields = self.group_by_fields.copy()
#         new_query.having_clauses = self.having_clauses.copy()
#         new_query._limit = self._limit
#         new_query._offset = self._offset
#         new_query._distinct = self._distinct
#         return new_query






































# # # from typing import Any, Dict, List, Optional, Union, Type
# # # from ..models.base import BaseModel
# # # from .filters import FilterExpression
# # # from .compiler import QueryCompiler

# # # class QueryBuilder:
# # #     """Builds database queries with type safety"""
    
# # #     def __init__(self, model: Type[BaseModel]):
# # #         self.model = model
# # #         self.compiler = QueryCompiler()
# # #         self._reset()
    
# # #     def _reset(self):
# # #         self.selected_fields = []
# # #         self.where_clauses = []
# # #         self.order_by_clauses = []
# # #         self.includes = []
# # #         self.limit_value = None
# # #         self.offset_value = None
    
# # #     def select(self, *fields: str) -> 'QueryBuilder':
# # #         """Select specific fields"""
# # #         self.selected_fields.extend(fields)
# # #         return self
    
# # #     def where(self, *filters: FilterExpression) -> 'QueryBuilder':
# # #         """Add WHERE clauses"""
# # #         self.where_clauses.extend(filters)
# # #         return self
    
# # #     def order_by(self, field: str, ascending: bool = True) -> 'QueryBuilder':
# # #         """Add ORDER BY clause"""
# # #         self.order_by_clauses.append((field, ascending))
# # #         return self
    
# # #     def include(self, relation: str) -> 'QueryBuilder':
# # #         """Include related models"""
# # #         self.includes.append(relation)
# # #         return self
    
# # #     def limit(self, value: int) -> 'QueryBuilder':
# # #         """Add LIMIT clause"""
# # #         self.limit_value = value
# # #         return self
    
# # #     def offset(self, value: int) -> 'QueryBuilder':
# # #         """Add OFFSET clause"""
# # #         self.offset_value = value
# # #         return self
    
# # #     def build(self) -> str:
# # #         """Build the final query"""
# # #         return self.compiler.compile(self)


# # # # from typing import Any, Dict, List, Optional
# # # # from .operators import Operator

# # # # class QueryBuilder:
# # # #     def __init__(self):
# # # #         self.select_fields: List[str] = []
# # # #         self.where_conditions: List[Dict] = []
# # # #         self.include_relations: Dict[str, Any] = {}
# # # #         self.order_by: List[Dict] = []
# # # #         self.limit_value: Optional[int] = None
# # # #         self.offset_value: Optional[int] = None
# # # #         self.group_by: List[str] = []

# # # #     def select(self, *fields: str) -> 'QueryBuilder':
# # # #         self.select_fields.extend(fields)
# # # #         return self

# # # #     def where(self, field: str, operator: Operator, value: Any) -> 'QueryBuilder':
# # # #         self.where_conditions.append({
# # # #             'field': field,
# # # #             'operator': operator,
# # # #             'value': value
# # # #         })
# # # #         return self

# # # #     def include(self, relation: str, nested: Optional[Dict] = None) -> 'QueryBuilder':
# # # #         self.include_relations[relation] = nested or {}
# # # #         return self

# # # #     def order_by_asc(self, field: str) -> 'QueryBuilder':
# # # #         self.order_by.append({'field': field, 'direction': 'ASC'})
# # # #         return self

# # # #     def order_by_desc(self, field: str) -> 'QueryBuilder':
# # # #         self.order_by.append({'field': field, 'direction': 'DESC'})
# # # #         return self

# # # #     def limit(self, value: int) -> 'QueryBuilder':
# # # #         self.limit_value = value
# # # #         return self

# # # #     def offset(self, value: int) -> 'QueryBuilder':
# # # #         self.offset_value = value
# # # #         return self

# # # #     def group_by(self, *fields: str) -> 'QueryBuilder':
# # # #         self.group_by.extend(fields)
# # # #         return self

# # #  accessnode/query/builder.py
# # from typing import Any, Dict, List, Optional
# # from accessnode.query.base_query import BaseQueryBuilder
# # from accessnode.database.types import QueryOperator

# # class QueryBuilder(BaseQueryBuilder):
# #     def select(self, *fields: str) -> 'QueryBuilder':
# #         """Select specific fields"""
# #         self.selected_fields.extend(fields)
# #         return self

# #     def filter(self, **conditions: Dict[str, Any]) -> 'QueryBuilder':
# #         """Add filter conditions"""
# #         for field, value in conditions.items():
# #             if '__' in field:
# #                 field_name, operator = field.split('__')
# #                 self.filters[field_name] = {
# #                     'operator': QueryOperator(operator),
# #                     'value': value
# #                 }
# #             else:
# #                 self.filters[field] = {
# #                     'operator': QueryOperator.EQUALS,
# #                     'value': value
# #                 }
# #         return self

# #     def limit(self, limit: int) -> 'QueryBuilder':
# #         """Set limit"""
# #         self._limit = limit
# #         return self

# #     def offset(self, offset: int) -> 'QueryBuilder':
# #         """Set offset"""
# #         self._offset = offset
# #         return self

# #     def order_by(self, field: str, descending: bool = False) -> 'QueryBuilder':
# #         """Add order by clause"""
# #         self._order_by.append({
# #             'field': field,
# #             'descending': descending
# #         })
# #         return self

# #     def include(self, relation: str) -> 'QueryBuilder':
# #         """Include related models"""
# #         self._includes.append(relation)
# #         return self

# #     def update(self, data: Dict[str, Any]) -> 'QueryBuilder':
# #         """Set update data"""
# #         self._update_data = data
# #         return self

# #     def delete(self) -> 'QueryBuilder':
# #         """Mark as delete query"""
# #         self._is_delete = True
# #         return self

# #     def insert(self, data: Dict[str, Any]) -> 'QueryBuilder':
# #         """Set insert data"""
# #         self._insert_data = data
# #         return self

# #     async def execute(self) -> List[Dict[str, Any]]:
# #         """Execute the query"""
# #         # This will be implemented by each database adapter
# #         pass

# #     async def count(self) -> int:
# #         """Get count of records"""
# #         # This will be implemented by each database adapter
# #         pass





