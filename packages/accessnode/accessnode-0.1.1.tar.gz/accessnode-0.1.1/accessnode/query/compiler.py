# accessnode/query/compiler.py
from typing import Any, Dict, List, Tuple, Optional
from .types import (
    JoinType, OrderDirection, Operator,
    WhereClause, JoinClause, OrderByClause
)
from .builder import QueryBuilder
from ..core.exceptions import QueryError

class QueryCompiler:
    def __init__(self, query_builder: QueryBuilder):
        self.builder = query_builder
        self.params: List[Any] = []
        self.param_index = 0

    def compile_select(self) -> Tuple[str, List[Any]]:
        """Compile SELECT query."""
        # Reset parameters
        self.params = []
        self.param_index = 0

        # Build query parts
        fields = self._compile_fields()
        table = self.builder.model.__table__
        joins = self._compile_joins()
        where = self._compile_where()
        group_by = self._compile_group_by()
        having = self._compile_having()
        order_by = self._compile_order_by()
        limit_offset = self._compile_limit_offset()

        # Construct query
        query_parts = ["SELECT"]
        if self.builder._distinct:
            query_parts.append("DISTINCT")
        
        query_parts.extend([
            fields,
            f"FROM {table}",
            joins,
            where,
            group_by,
            having,
            order_by,
            limit_offset
        ])

        # Join parts and filter out empty ones
        query = " ".join(part for part in query_parts if part)

        return query, self.params

    def _compile_fields(self) -> str:
        """Compile field selection."""
        if not self.builder.selected_fields:
            return "*"
        return ", ".join(self.builder.selected_fields)

    def _compile_joins(self) -> str:
        """Compile JOIN clauses."""
        if not self.builder.join_clauses:
            return ""

        joins = []
        for join in self.builder.join_clauses:
            conditions = []
            for condition in join.conditions:
                param = self._add_param(condition.value)
                conditions.append(
                    f"{condition.field} {condition.operator.value} {param}"
                )
            
            join_condition = " AND ".join(conditions)
            joins.append(
                f"{join.type.value} {join.table} ON {join_condition}"
            )

        return " ".join(joins)

    def _compile_where(self) -> str:
        """Compile WHERE clauses."""
        if not self.builder.where_clauses:
            return ""

        conditions = []
        for clause in self.builder.where_clauses:
            condition = self._compile_condition(clause)
            if clause.is_or and conditions:
                conditions.append("OR")
            elif conditions:
                conditions.append("AND")
            conditions.append(condition)

        return "WHERE " + " ".join(conditions)

    def _compile_condition(self, clause: WhereClause) -> str:
        """Compile a single condition."""
        if clause.operator in [Operator.IS_NULL, Operator.IS_NOT_NULL]:
            return f"{clause.field} {clause.operator.value}"

        if clause.operator == Operator.BETWEEN:
            if not isinstance(clause.value, (list, tuple)) or len(clause.value) != 2:
                raise QueryError("BETWEEN operator requires two values")
            param1 = self._add_param(clause.value[0])
            param2 = self._add_param(clause.value[1])
            return f"{clause.field} BETWEEN {param1} AND {param2}"

        if clause.operator in [Operator.IN, Operator.NOT_IN]:
            if not isinstance(clause.value, (list, tuple)):
                raise QueryError(f"{clause.operator.value} operator requires a list of values")
            params = [self._add_param(v) for v in clause.value]
            return f"{clause.field} {clause.operator.value} ({', '.join(params)})"

        param = self._add_param(clause.value)
        return f"{clause.field} {clause.operator.value} {param}"

    def _compile_group_by(self) -> str:
        """Compile GROUP BY clause."""
        if not self.builder.group_by_fields:
            return ""
        return "GROUP BY " + ", ".join(self.builder.group_by_fields)

    def _compile_having(self) -> str:
        """Compile HAVING clause."""
        if not self.builder.having_clauses:
            return ""

        conditions = []
        for clause in self.builder.having_clauses:
            conditions.append(self._compile_condition(clause))

        return "HAVING " + " AND ".join(conditions)

    def _compile_order_by(self) -> str:
        """Compile ORDER BY clause."""
        if not self.builder.order_by_clauses:
            return ""

        orders = []
        for clause in self.builder.order_by_clauses:
            orders.append(
                f"{clause.field} {clause.direction.value}"
            )

        return "ORDER BY " + ", ".join(orders)

    def _compile_limit_offset(self) -> str:
        """Compile LIMIT and OFFSET clauses."""
        parts = []
        
        if self.builder._limit is not None:
            parts.append(f"LIMIT {self.builder._limit}")
            
        if self.builder._offset is not None:
            parts.append(f"OFFSET {self.builder._offset}")
            
        return " ".join(parts)

    def _add_param(self, value: Any) -> str:
        """Add parameter and return placeholder."""
        self.params.append(value)
        self.param_index += 1
        return f"${self.param_index}"




















# from typing import Dict, Any, List, Optional
# from accessnode.database.types import QueryOperator
# from accessnode.query.builder import QueryBuilder

# class QueryCompiler:
#     def __init__(self, query_builder: QueryBuilder):
#         self.builder = query_builder
#         self.params: List[Any] = []
#         self.param_index = 0

#     def compile_select(self) -> str:
#         """Compile SELECT query"""
#         fields = '*'
#         if self.builder.selected_fields:
#             fields = ', '.join(self.builder.selected_fields)

#         query = f"SELECT {fields} FROM {self.builder.model.__table__}"
        
#         where_clause = self.compile_where()
#         if where_clause:
#             query += f" WHERE {where_clause}"

#         if self.builder._order_by:
#             order_clauses = []
#             for order in self.builder._order_by:
#                 direction = 'DESC' if order['descending'] else 'ASC'
#                 order_clauses.append(f"{order['field']} {direction}")
#             query += f" ORDER BY {', '.join(order_clauses)}"

#         if self.builder._limit is not None:
#             query += f" LIMIT {self.builder._limit}"

#         if self.builder._offset is not None:
#             query += f" OFFSET {self.builder._offset}"

#         return query

#     def compile_insert(self) -> str:
#         """Compile INSERT query"""
#         fields = list(self.builder._insert_data.keys())
#         values = [self.builder._insert_data[field] for field in fields]
        
#         placeholders = [self.add_param(value) for value in values]
        
#         query = f"INSERT INTO {self.builder.model.__table__} "
#         query += f"({', '.join(fields)}) "
#         query += f"VALUES ({', '.join(placeholders)})"
        
#         return query

#     def compile_update(self) -> str:
#         """Compile UPDATE query"""
#         sets = []
#         for field, value in self.builder._update_data.items():
#             placeholder = self.add_param(value)
#             sets.append(f"{field} = {placeholder}")

#         query = f"UPDATE {self.builder.model.__table__} "
#         query += f"SET {', '.join(sets)}"

#         where_clause = self.compile_where()
#         if where_clause:
#             query += f" WHERE {where_clause}"

#         return query

#     def compile_delete(self) -> str:
#         """Compile DELETE query"""
#         query = f"DELETE FROM {self.builder.model.__table__}"
        
#         where_clause = self.compile_where()
#         if where_clause:
#             query += f" WHERE {where_clause}"

#         return query

#     def compile_where(self) -> str:
#         """Compile WHERE conditions"""
#         if not self.builder.filters:
#             return ""

#         conditions = []
#         for field, condition in self.builder.filters.items():
#             operator = condition['operator']
#             value = condition['value']
            
#             if operator == QueryOperator.EQUALS:
#                 placeholder = self.add_param(value)
#                 conditions.append(f"{field} = {placeholder}")
#             elif operator == QueryOperator.NOT_EQUALS:
#                 placeholder = self.add_param(value)
#                 conditions.append(f"{field} != {placeholder}")
#             elif operator == QueryOperator.IN:
#                 placeholders = [self.add_param(v) for v in value]
#                 conditions.append(f"{field} IN ({', '.join(placeholders)})")
#             elif operator == QueryOperator.LIKE:
#                 placeholder = self.add_param(f"%{value}%")
#                 conditions.append(f"{field} LIKE {placeholder}")
#             elif operator in [QueryOperator.GT, QueryOperator.GTE, QueryOperator.LT, QueryOperator.LTE]:
#                 placeholder = self.add_param(value)
#                 op_map = {
#                     QueryOperator.GT: '>',
#                     QueryOperator.GTE: '>=',
#                     QueryOperator.LT: '<',
#                     QueryOperator.LTE: '<='
#                 }
#                 conditions.append(f"{field} {op_map[operator]} {placeholder}")

#         return " AND ".join(conditions)

#     def add_param(self, value: Any) -> str:
#         """Add parameter and return placeholder"""
#         self.params.append(value)
#         self.param_index += 1
#         return f"${self.param_index}"