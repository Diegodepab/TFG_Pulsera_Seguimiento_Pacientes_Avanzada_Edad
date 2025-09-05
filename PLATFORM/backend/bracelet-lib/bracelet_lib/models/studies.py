import functools
from datetime import datetime, date
from typing import Dict, Optional, List, Union
from pydantic import Field
import sqlalchemy as sa

from . import relation
from .common import UTCTimeStamp, AllowBaseModel, CustomBaseModel
from ..models import database_manager
from ..models.patients import Patient
from ..models.base_model import braceletBaseModel


def get_study_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'patient_id': {
            'ge': 1,
            'example': 1
        },
        'step_count': {
            'ge': 0,
            'example': 1000
        },
        'bpm': {
            'ge': 0,
            'example': 75
        },
        'spo2': {
            'ge': 0,
            'le': 100,
            'example': 98
        },
        'ts': {
            'example': '2025-05-26T12:34:56Z'
        },
        'create_ts': {
            'example': '2025-05-26T12:34:56Z'
        },
        'update_ts': {
            'example': '2025-05-26T12:34:56Z'
        }
    }

study_schema = get_study_schema()


class Study(braceletBaseModel):
    class StudyCreate(CustomBaseModel):
        id         : Optional[int]      = Field(None, **study_schema['id'])
        patient_id : int                = Field(..., **study_schema['patient_id'])
        step_count : int                = Field(..., **study_schema['step_count'])
        bpm        : int                = Field(..., **study_schema['bpm'])
        spo2       : Optional[int]      = Field(None, **study_schema['spo2'])
        ts         : datetime           = Field(..., **study_schema['ts'])
        create_ts  : Optional[datetime] = Field(None, **study_schema['create_ts'])
        update_ts  : Optional[datetime] = Field(None, **study_schema['update_ts'])

    class StudyFull(AllowBaseModel):
        id         : Optional[int]      = Field(None, **study_schema['id'])
        patient_id : Optional[int]      = Field(None, **study_schema['patient_id'])
        step_count : Optional[int]      = Field(None, **study_schema['step_count'])
        bpm        : Optional[int]      = Field(None, **study_schema['bpm'])
        spo2       : Optional[int]      = Field(None, **study_schema['spo2'])
        ts         : Optional[datetime] = Field(None, **study_schema['ts'])
        create_ts  : Optional[datetime] = Field(None, **study_schema['create_ts'])
        update_ts  : Optional[datetime] = Field(None, **study_schema['update_ts'])

    class StudyUpdate(CustomBaseModel):
        id         : int                = Field(..., **study_schema['id'])
        patient_id : int                = Field(..., **study_schema['patient_id'])
        step_count : int                = Field(..., **study_schema['step_count'])
        bpm        : int                = Field(..., **study_schema['bpm'])
        spo2       : Optional[int]      = Field(None, **study_schema['spo2'])
        ts         : datetime           = Field(..., **study_schema['ts'])
        create_ts  : datetime           = Field(..., **study_schema['create_ts'])
        update_ts  : datetime           = Field(..., **study_schema['update_ts'])

    class StudyMerge(StudyFull):
        class Config:
            extra = 'forbid'

    # search schema
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'StudySearch',
        List[StudyFull],
        'studies'
    )
    class StudySearch(_search_tpl): pass

    CreateValidator = StudyCreate
    FullValidator   = StudyFull
    UpdateValidator = StudyUpdate
    MergeValidator  = StudyMerge
    SearchValidator = StudySearch

    Table = sa.Table(
        'study',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('patient_id', sa.INTEGER(), sa.ForeignKey('patient.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('step_count', sa.INTEGER(), nullable=False, comment="Cumulative steps for this study"),
        sa.Column('bpm', sa.INTEGER(), nullable=False, comment="Beats per minute"),
        sa.Column('spo2', sa.INTEGER(), nullable=True, comment="Oxygen saturation %"),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False, comment="Timestamp of the measurement"),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
    )

    id         : int      = None
    patient_id : int      = None
    step_count : int      = None
    bpm        : int      = None
    spo2       : int      = None
    ts         : datetime = None
    create_ts  : datetime = None
    update_ts  : datetime = None

    # Related data
    # noinspection PyUnresolvedReferences
    patient    : 'Patient'   = None

    @classmethod
    @functools.lru_cache()
    def get_relations(cls) -> Dict:
        from bracelet_lib.models.patients import Patient

        return {
            'patient': relation.Relation(
                rel_type = relation.RelationType.BelongsToOneRelation,
                model    = Patient,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.patient_id,
                    right   = Patient.Table.c.id
                )
            )
        }

    @classmethod
    async def save_static(
        cls,
        data: Dict,
        with_transaction    : bool = True,
        ignore_rel_entities : bool = False
    ) -> 'Study':
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
        raise_not_found     : bool = True,
        with_transaction    : bool = True,
        ignore_rel_entities : bool = False
    ) -> Optional['Study']:
        return await super().update_static(
            id,
            data,
            raise_not_found     = raise_not_found,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )
