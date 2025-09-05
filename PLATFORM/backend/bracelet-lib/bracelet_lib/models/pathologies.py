import functools
from datetime import datetime
from typing import Dict, Optional, List, Union, Callable
from pydantic import Field
import sqlalchemy as sa
from sqlalchemy import Table as TTable, select
from sqlalchemy.sql import Alias

from . import relation
from .common import UTCTimeStamp, AllowBaseModel, CustomBaseModel
from ..models import database_manager
from ..models.base_model import braceletBaseModel


def get_pathology_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'name': {
            'max_length': 255,
            'example': "Diabetes"
        },
        'create_ts': {
            'example': '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example': '2020-10-05 14:05:25.643021+00:00'
        }
    }


pathology_schema = get_pathology_schema()


class Pathology(braceletBaseModel):
    class PathologyCreate(CustomBaseModel):
        id        : Optional[int]      = Field(None, **pathology_schema['id'])
        name      : str                = Field(..., **pathology_schema['name'])
        create_ts : Optional[datetime] = Field(None, **pathology_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **pathology_schema['update_ts'])

    class PathologyFull(AllowBaseModel):
        id        : Optional[int]      = Field(None, **pathology_schema['id'])
        name      : Optional[str]      = Field(None, **pathology_schema['name'])
        create_ts : Optional[datetime] = Field(None, **pathology_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **pathology_schema['update_ts'])

    class PathologyUpdate(CustomBaseModel):
        id        : int                = Field(..., **pathology_schema['id'])
        name      : str                = Field(..., **pathology_schema['name'])
        create_ts : datetime           = Field(..., **pathology_schema['create_ts'])
        update_ts : datetime           = Field(..., **pathology_schema['update_ts'])

    class PathologyMerge(PathologyFull):
        class Config:
            extra = 'forbid'

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'PathologySearch',
        List[PathologyFull],
        'pathologies'
    )
    class PathologySearch(_search_tpl): pass

    CreateValidator = PathologyCreate
    FullValidator   = PathologyFull
    UpdateValidator = PathologyUpdate
    MergeValidator  = PathologyMerge
    SearchValidator = PathologySearch

    Table = sa.Table(
        'pathology',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    id        : int      = None
    name      : str      = None
    create_ts : datetime = None
    update_ts : datetime = None

    @classmethod
    @functools.lru_cache()
    def get_relations(cls) -> Dict:
        from bracelet_lib.models.patient_pathologies import PatientPathology

        return {
            'patient_pathologies': relation.Relation(
                rel_type  = relation.RelationType.HasManyRelation,
                model     = PatientPathology,
                join      = relation.JoinMeta(
                    left  = cls.Table.c.id,
                    right = PatientPathology.Table.c.pathology_id
                )
            ),
            # 'patients': relation.Relation(
            #     rel_type = relation.RelationType.ManyToManyRelation,
            #     model    = Patient,
            #     join     = relation.JoinMeta(
            #         left    = cls.Table.c.id,
            #         right   = Patient.Table.c.id,
            #         through = relation.JoinMetaThrough(
            #             left        = PatientPathology.Table.c.pathology_id,
            #             right       = PatientPathology.Table.c.patient_id,
            #             table_class = PatientPathology.Table,
            #         )
            #     )
            # )
        }

    @classmethod
    async def save_static(
            cls,
            data: Dict,
            with_transaction    : bool = True,
            ignore_rel_entities : bool = False
    ) -> 'Pathology':
        """
        Save a new Pathology instance to the database.
        """
        return await super().save_static(
            data,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )

    @classmethod
    async def update_static(
            cls,
            id: Union[int, str],
            data: Dict,
            raise_not_found: bool = True,
            with_transaction: bool = True,
            ignore_rel_entities : bool = False
    ) -> Optional['Pathology']:
        """
        Update an existing Pathology instance.
        """
        return await super().update_static(
            id,
            data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )
