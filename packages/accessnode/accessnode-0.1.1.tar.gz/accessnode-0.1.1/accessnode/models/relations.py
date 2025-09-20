from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from .base import BaseModel
from ..core.exceptions import RelationshipError

T = TypeVar('T', bound=BaseModel)

class Relationship:
    def __init__(
        self,
        model: Type[T],
        type: str,
        foreign_key: str,
        local_key: str = 'id',
        back_populates: Optional[str] = None,
        cascade_delete: bool = False
    ):
        self.model = model
        self.type = type
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.back_populates = back_populates
        self.cascade_delete = cascade_delete

class HasOne(Relationship):
    def __init__(
        self,
        model: Type[T],
        foreign_key: str,
        local_key: str = 'id',
        back_populates: Optional[str] = None,
        cascade_delete: bool = False
    ):
        super().__init__(
            model=model,
            type='one_to_one',
            foreign_key=foreign_key,
            local_key=local_key,
            back_populates=back_populates,
            cascade_delete=cascade_delete
        )

class HasMany(Relationship):
    def __init__(
        self,
        model: Type[T],
        foreign_key: str,
        local_key: str = 'id',
        back_populates: Optional[str] = None,
        cascade_delete: bool = False
    ):
        super().__init__(
            model=model,
            type='one_to_many',
            foreign_key=foreign_key,
            local_key=local_key,
            back_populates=back_populates,
            cascade_delete=cascade_delete
        )

class BelongsTo(Relationship):
    def __init__(
        self,
        model: Type[T],
        foreign_key: str,
        local_key: str = 'id',
        back_populates: Optional[str] = None
    ):
        super().__init__(
            model=model,
            type='many_to_one',
            foreign_key=foreign_key,
            local_key=local_key,
            back_populates=back_populates,
            cascade_delete=False
        )

class ManyToMany(Relationship):
    def __init__(
        self,
        model: Type[T],
        pivot_table: str,
        foreign_key: str,
        related_key: str,
        local_key: str = 'id',
        back_populates: Optional[str] = None,
        cascade_delete: bool = False
    ):
        super().__init__(
            model=model,
            type='many_to_many',
            foreign_key=foreign_key,
            local_key=local_key,
            back_populates=back_populates,
            cascade_delete=cascade_delete
        )
        self.pivot_table = pivot_table
        self.related_key = related_key































# # from typing import Optional
# # from dataclasses import dataclass
# # from enum import Enum

# # class RelationType(Enum):
# #     ONE_TO_ONE = "one_to_one"
# #     ONE_TO_MANY = "one_to_many"
# #     MANY_TO_MANY = "many_to_many"

# # @dataclass
# # class Relation:
# #     type: RelationType
# #     foreign_table: str
# #     foreign_key: str
# #     through_table: Optional[str] = None  # For many-to-many relations



# # accessnode/models/relations.py
# from typing import TYPE_CHECKING, Type, Optional, List, Dict, Any
# from dataclasses import dataclass

# if TYPE_CHECKING:
#     from accessnode.models.base import BaseModel

# @dataclass
# class Relation:
#     model: str
#     type: str
#     foreign_key: str
#     local_key: str = 'id'
#     through: Optional[str] = None
#     through_fields: Optional[tuple[str, str]] = None
#     cascade: bool = False
#     back_populates: Optional[str] = None

# class HasOne(Relation):
#     def __init__(
#         self,
#         model: str,
#         foreign_key: str,
#         local_key: str = 'id',
#         cascade: bool = False,
#         back_populates: Optional[str] = None
#     ):
#         super().__init__(
#             model=model,
#             type='one',
#             foreign_key=foreign_key,
#             local_key=local_key,
#             cascade=cascade,
#             back_populates=back_populates
#         )

# class HasMany(Relation):
#     def __init__(
#         self,
#         model: str,
#         foreign_key: str,
#         local_key: str = 'id',
#         cascade: bool = False,
#         back_populates: Optional[str] = None
#     ):
#         super().__init__(
#             model=model,
#             type='many',
#             foreign_key=foreign_key,
#             local_key=local_key,
#             cascade=cascade,
#             back_populates=back_populates
#         )

# class BelongsTo(Relation):
#     def __init__(
#         self,
#         model: str,
#         foreign_key: str,
#         local_key: str = 'id',
#         back_populates: Optional[str] = None
#     ):
#         super().__init__(
#             model=model,
#             type='one',
#             foreign_key=foreign_key,
#             local_key=local_key,
#             back_populates=back_populates
#         )

# class ManyToMany(Relation):
#     def __init__(
#         self,
#         model: str,
#         through: str,
#         through_fields: tuple[str, str],
#         back_populates: Optional[str] = None
#     ):
#         super().__init__(
#             model=model,
#             type='many',
#             foreign_key='',  # Not used directly in many-to-many
#             through=through,
#             through_fields=through_fields,
#             back_populates=back_populates
#         )