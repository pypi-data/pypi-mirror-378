# accessnode/query/base_query.py
from typing import Any, Dict, List, Optional, Type
from accessnode.database.types import QueryOperator

class BaseQueryBuilder:
    """Base query builder to avoid circular imports"""
    def __init__(self, model_class: Type):
        self.model = model_class
        self.filters: Dict[str, Dict[str, Any]] = {}
        self.selected_fields: List[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._order_by: List[Dict[str, Any]] = []
        self._includes: List[str] = []
        self._update_data: Optional[Dict[str, Any]] = None
        self._insert_data: Optional[Dict[str, Any]] = None
        self._is_delete: bool = False