from datetime import datetime
from typing import Dict, Optional, List, Union
from pydantic import Field
import sqlalchemy as sa

from .common import UTCTimeStamp, CustomBaseModel, AllowBaseModel
from ..models import database_manager
from ..models.base_model import braceletBaseModel
from bracelet_lib.models import relation


def get_alarm_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'patient_id': {
            'ge': 1,
            'example': 1
        },
        'alarm_type': {
            'max_length': 64,
            'example': 'fall_detected'
        },
        'ts': {
            'example': '2025-05-26T12:34:56Z'
        },
        'is_urgent': {
            'example': True
        },
        'create_ts': {
            'example': '2025-05-26T12:34:56Z'
        },
        'update_ts': {
            'example': '2025-05-26T12:34:56Z'
        }
    }

alarm_schema = get_alarm_schema()

class Alarm(braceletBaseModel):
    class AlarmCreate(CustomBaseModel):
        id         : Optional[int]   = Field(None, **alarm_schema['id'])
        patient_id : int             = Field(..., **alarm_schema['patient_id'])
        alarm_type : str             = Field(..., **alarm_schema['alarm_type'])
        ts         : datetime        = Field(..., **alarm_schema['ts'])
        is_urgent  : bool            = Field(False, **alarm_schema['is_urgent'])
        create_ts  : Optional[datetime] = Field(None, **alarm_schema['create_ts'])
        update_ts  : Optional[datetime] = Field(None, **alarm_schema['update_ts'])

    class AlarmFull(AllowBaseModel):
        id         : Optional[int]   = Field(None, **alarm_schema['id'])
        patient_id : Optional[int]   = Field(None, **alarm_schema['patient_id'])
        alarm_type : Optional[str]   = Field(None, **alarm_schema['alarm_type'])
        ts         : Optional[datetime] = Field(None, **alarm_schema['ts'])
        is_urgent  : Optional[bool]  = Field(None, **alarm_schema['is_urgent'])
        create_ts  : Optional[datetime] = Field(None, **alarm_schema['create_ts'])
        update_ts  : Optional[datetime] = Field(None, **alarm_schema['update_ts'])

    class AlarmUpdate(CustomBaseModel):
        id         : int             = Field(..., **alarm_schema['id'])
        patient_id : int             = Field(..., **alarm_schema['patient_id'])
        alarm_type : str             = Field(..., **alarm_schema['alarm_type'])
        ts         : datetime        = Field(..., **alarm_schema['ts'])
        is_urgent  : bool            = Field(..., **alarm_schema['is_urgent'])
        create_ts  : datetime        = Field(..., **alarm_schema['create_ts'])
        update_ts  : datetime        = Field(..., **alarm_schema['update_ts'])

    class AlarmMerge(AlarmFull):
        class Config:
            extra = 'forbid'

    # Search schema
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'AlarmSearch',
        List[AlarmFull],
        'alarms'
    )
    class AlarmSearch(_search_tpl): pass

    CreateValidator = AlarmCreate
    FullValidator   = AlarmFull
    UpdateValidator = AlarmUpdate
    MergeValidator  = AlarmMerge
    SearchValidator = AlarmSearch

    Table = sa.Table(
        'alarm',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('patient_id', sa.INTEGER(), sa.ForeignKey('patient.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('alarm_type', sa.VARCHAR(64), nullable=False, comment="'fall_detected', 'strange_bpm', 'button_alarm', etc."),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False, comment="Time when alarm was raised"),
        sa.Column('is_urgent', sa.BOOLEAN(), nullable=False, server_default=sa.text('FALSE'), comment="True if urgent"),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    id         : int      = None
    patient_id : int      = None
    alarm_type : str      = None
    ts         : datetime = None
    is_urgent  : bool     = None
    create_ts  : datetime = None
    update_ts  : datetime = None

    # Related data
    patient   : 'Patient' = None

    @classmethod
    def get_relations(cls):
        from ..models.patients import Patient
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
    ) -> 'Alarm':
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
    ) -> Optional['Alarm']:
        return await super().update_static(
            id,
            data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )