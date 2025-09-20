# accessnode/models/base.py
from typing import Any, Dict, List, Optional, Type, TypeVar, ClassVar
from pydantic import BaseModel as PydanticModel
from ..core.exceptions import ValidationError
from ..query.builder import QueryBuilder
from .fields import BaseField
from .relations import Relationship
import datetime

T = TypeVar('T', bound='BaseModel')

class BaseModel(PydanticModel):
    __table__: ClassVar[str]
    __fields__: ClassVar[Dict[str, BaseField]]
    __relationships__: ClassVar[Dict[str, Relationship]]
    __timestamps__: ClassVar[bool] = True

    id: Optional[Any] = None

    def __init__(self, **data):
        self._data = {}
        self._original = {}
        self._loaded_relationships = {}
        self._dirty = set()

        # Validate and set fields
        for field_name, field in self.__fields__.items():
            value = data.get(field_name)
            try:
                validated_value = field.validate(value)
                self._data[field_name] = validated_value
                self._original[field_name] = validated_value
            except ValidationError as e:
                raise ValidationError(f"Validation failed for field {field_name}: {str(e)}")

    @classmethod
    def query(cls) -> QueryBuilder:
        """Create a new query builder instance."""
        return QueryBuilder(cls)

    async def save(self) -> bool:
        """Save or update the model."""
        if self.id is None:
            # Create new record
            self._data['created_at'] = datetime.utcnow()
            self._data['updated_at'] = datetime.utcnow()
            query = self.query().insert(self._data)
            result = await query.execute()
            self.id = result
            return True
        else:
            # Update existing record
            if not self._dirty:
                return False
            
            updates = {
                field: self._data[field]
                for field in self._dirty
            }
            updates['updated_at'] = datetime.utcnow()
            
            query = self.query().where('id', '=', self.id).update(updates)
            await query.execute()
            self._dirty.clear()
            return True

    async def delete(self) -> bool:
        """Delete the model."""
        if self.id is None:
            return False

        # Handle cascade deletes for relationships
        for name, relation in self.__relationships__.items():
            if relation.cascade_delete:
                related_models = await getattr(self, name)
                if isinstance(related_models, list):
                    for model in related_models:
                        await model.delete()
                elif related_models:
                    await related_models.delete()

        query = self.query().where('id', '=', self.id).delete()
        await query.execute()
        return True

    async def refresh(self) -> 'BaseModel':
        """Refresh the model from the database."""
        if self.id is None:
            raise ValidationError("Cannot refresh a model that hasn't been saved")

        query = self.query().where('id', '=', self.id)
        fresh_data = await query.first()
        
        if not fresh_data:
            raise ValidationError("Model no longer exists in the database")

        self._data = fresh_data._data
        self._original = fresh_data._data.copy()
        self._dirty.clear()
        self._loaded_relationships.clear()
        
        return self

    def __getattr__(self, name: str) -> Any:
        """Handle dynamic relationship loading."""
        if name in self.__relationships__:
            if name not in self._loaded_relationships:
                relation = self.__relationships__[name]
                self._loaded_relationships[name] = relation.load(self)
            return self._loaded_relationships[name]

        if name in self._data:
            return self._data[name]

        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Handle attribute setting and dirty tracking."""
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        if name in self.__fields__:
            field = self.__fields__[name]
            validated_value = field.validate(value)
            if self._data.get(name) != validated_value:
                self._data[name] = validated_value
                self._dirty.add(name)
        else:
            super().__setattr__(name, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **self._data,
            **{
                name: relation.to_dict()
                for name, relation in self._loaded_relationships.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        return cls(**data)





























# from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
# from accessnode.query.base_query import BaseQueryBuilder
# from accessnode.database.types import Field, Relation

# T = TypeVar('T', bound='BaseModel')

# class BaseModel(Generic[T]):
#     __table__: str
#     __schema__: Dict[str, Field]
#     __relations__: Dict[str, Relation]
    
#     def __init__(self, **data):
#         self._data = data
#         self._changed_fields = set()
#         self._loaded_relations = {}

#     @classmethod
#     async def create(cls: Type[T], **data) -> T:
#         """Create a new record"""
#         instance = cls(**data)
#         await instance.save()
#         return instance

#     @classmethod
#     async def find_many(cls: Type[T], **filters) -> List[T]:
#         """Find multiple records with filters"""
#         query = BaseQueryBuilder(cls).filter(**filters)
#         results = await query.execute()
#         return [cls(**record) for record in results]

#     @classmethod
#     async def find_unique(cls: Type[T], **filters) -> Optional[T]:
#         """Find a unique record"""
#         query = BaseQueryBuilder(cls).filter(**filters).limit(1)
#         result = await query.execute()
#         return cls(**result[0]) if result else None

#     async def save(self) -> None:
#         """Save or update the model"""
#         if not hasattr(self, 'id'):
#             # Create new record
#             query = BaseQueryBuilder(self.__class__).insert(self._data)
#             result = await query.execute()
#             self.id = result['id']
#         else:
#             # Update existing record
#             if self._changed_fields:
#                 updates = {k: self._data[k] for k in self._changed_fields}
#                 query = BaseQueryBuilder(self.__class__).filter(id=self.id).update(updates)
#                 await query.execute()

#     async def delete(self) -> None:
#         """Delete the model"""
#         if hasattr(self, 'id'):
#             query = BaseQueryBuilder(self.__class__).filter(id=self.id).delete()
#             await query.execute()

    
#     async def load_relation(self, relation_name: str) -> Any:
#         """Load a related model"""
#         if relation_name not in self.__relations__:
#             raise ValueError(f"Unknown relation: {relation_name}")
        
#         if relation_name not in self._loaded_relations:
#             relation = self.__relations__[relation_name]
#             related_model = relation.model
#             foreign_key = relation.foreign_key
            
#             query = BaseQueryBuilder(related_model).filter(**{foreign_key: self.id})
#             result = await query.execute()
            
#             if relation.type == 'one':
#                 self._loaded_relations[relation_name] = related_model(**result[0]) if result else None
#             else:
#                 self._loaded_relations[relation_name] = [related_model(**r) for r in result]
        
#         return self._loaded_relations[relation_name]