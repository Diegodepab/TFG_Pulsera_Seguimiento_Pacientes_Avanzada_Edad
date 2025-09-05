from __future__ import annotations
from typing import Optional, Type, Union, Tuple, Dict

from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy import Table, Column


class RelationType(Enum):
    HasManyRelation         = 0  # 1:N
    ManyToManyRelation      = 1  # N:N
    BelongsToOneRelation    = 2  # Has one parent
    HasOneRelation          = 3  # 1:1
    HasOneThroughRelation   = 4  # 1:1, through a link table
    HasOneDependingRelation = 5  # 1:1, where the linked table has an ID we need to create ourselves


@dataclass()
class JoinMetaThrough:
    left        : Column
    right       : Column
    table_class : Table
    add_link    : bool  = False  # If set, a _link field will be added to the embedded field will the link entity values
    additional_fields : Dict[str, Column] = field(default_factory=dict)  # Dictionary of additional fields to include from the through table


@dataclass()
class JoinMeta:
    left    : Union[Column, Tuple[Union[Column, str, bool, int], ...]]
    right   : Union[Column, Tuple[Union[Column, str, bool, int], ...]]
    through : Optional[JoinMetaThrough] = None


class Relation:
    __table : Optional[Table]

    # noinspection PyUnresolvedReferences
    def __init__(
            self,
            rel_type : RelationType,
            model    : Optional[Type['TbraceletModel']] = None,
            table    : Optional[Table] = None,
            join     : JoinMeta = None
    ):
        self.rel_type = rel_type
        self.model    = model
        self.table    = table
        self.join     = join

    @property
    def table(self):
        # This is special because it's different in dynamic or static relations,
        # table is only set in dynamic situations
        return self.model.Table if self.model is not None else self.__table

    @table.setter
    def table(self, table: Table):
        self.__table = table

    def is_dynamic(self) -> bool:
        """
        Returns true if the relation is dynamic, false if it has a braceletBaseModel attached
        :return: boolean
        """
        return self.model is None
