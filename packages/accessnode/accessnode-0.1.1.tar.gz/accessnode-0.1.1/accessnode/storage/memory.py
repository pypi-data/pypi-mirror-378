from typing import Dict, List, Any, Optional
from ..core.types import Schema
from ..core.validation import SchemaValidator
from datetime import datetime

class MemoryStore:
    def __init__(self):
        self._collections: Dict[str, List[Dict[str, Any]]] = {}
        self._schemas: Dict[str, Schema] = {}
        self._auto_increment: Dict[str, int] = {}

    def register_schema(self, name: str, schema: Optional[Schema] = None) -> None:
        """Register a new collection with optional schema."""
        if name in self._collections:
            raise ValueError(f"Collection '{name}' already exists")
        
        self._collections[name] = []
        self._schemas[name] = schema or {}
        self._auto_increment[name] = 0

    async def insert(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a document into a collection."""
        if collection not in self._collections:
            raise ValueError(f"Collection '{collection}' does not exist")

        # Validate schema if exists
        schema = self._schemas[collection]
        print(schema)

        # if schema:
        #     SchemaValidator.validate_schema(data, schema)

        # Add system fields
        self._auto_increment[collection] += 1
        document = {
            "_id": self._auto_increment[collection],
            **data,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        self._collections[collection].append(document)
        return document

    async def find(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find documents matching query."""
        if collection not in self._collections:
            raise ValueError(f"Collection '{collection}' does not exist")

        return [doc for doc in self._collections[collection] 
                if self._matches_query(doc, query)]

    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find first document matching query."""
        results = await self.find(collection, query)
        return results[0] if results else None

    async def update(self, collection: str, query: Dict[str, Any], 
                    update: Dict[str, Any]) -> int:
        """Update documents matching query."""
        if collection not in self._collections:
            raise ValueError(f"Collection '{collection}' does not exist")

        updated = 0
        for doc in self._collections[collection]:
            if self._matches_query(doc, query):
                doc.update(update)
                doc["updatedAt"] = datetime.utcnow()
                updated += 1

        return updated

    async def delete(self, collection: str, query: Dict[str, Any]) -> int:
        """Delete documents matching query."""
        if collection not in self._collections:
            raise ValueError(f"Collection '{collection}' does not exist")

        original_length = len(self._collections[collection])
        self._collections[collection] = [
            doc for doc in self._collections[collection]
            if not self._matches_query(doc, query)
        ]
        return original_length - len(self._collections[collection])

    def _matches_query(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query criteria."""
        for key, value in query.items():
            if key not in doc:
                return False
            if isinstance(value, dict):
                if not self._matches_operators(doc[key], value):
                    return False
            elif doc[key] != value:
                return False
        return True

    def _matches_operators(self, field_value: Any, operators: Dict[str, Any]) -> bool:
        """Handle query operators ($gt, $lt, etc)."""
        for op, value in operators.items():
            if not self._apply_operator(op, field_value, value):
                return False
        return True

    def _apply_operator(self, op: str, field_value: Any, compare_value: Any) -> bool:
        """Apply a single query operator."""
        operators = {
            "$eq": lambda x, y: x == y,
            "$ne": lambda x, y: x != y,
            "$gt": lambda x, y: x > y,
            "$gte": lambda x, y: x >= y,
            "$lt": lambda x, y: x < y,
            "$lte": lambda x, y: x <= y,
            "$in": lambda x, y: x in y,
            "$nin": lambda x, y: x not in y,
        }
        return operators.get(op, lambda x, y: False)(field_value, compare_value)