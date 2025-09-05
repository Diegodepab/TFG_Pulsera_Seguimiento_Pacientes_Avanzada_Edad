import functools
from datetime import datetime
from typing import Dict, Optional, Union, List
from pydantic import Field
import sqlalchemy as sa

from . import relation
from .common import UTCTimeStamp, AllowBaseModel, CustomBaseModel
from ..models import database_manager
from ..models.base_model import braceletBaseModel


def get_patient_model_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'name': {
            'max_length': 255,
            'example': "model"
        },
        'patient_id': {
            'description': "ID of the patient owner of the patient model, FK to patient.id",
            'example': 123
        },
        'filename': {
            'max_length'  : 512,
            "description" : "Filename of the patient model",
            'example'     : '20222207.mp4'
        },
        'url': {
            "description" : "URL of the model glb",
            'example'     : 'https://www.cloud.com/modelo.glb'
        },
        'create_ts': {
            'example': '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example': '2020-10-05 14:05:25.643021+00:00'
        }
    }


patient_model_schema = get_patient_model_schema()


class PatientModel(braceletBaseModel):
    class PatientModelCreate(CustomBaseModel):
        id         : Optional[int]      = Field(None, **patient_model_schema['id'])
        name       : str                = Field(..., **patient_model_schema['name'])
        patient_id : Optional[int]      = Field(None, **patient_model_schema['patient_id'])
        filename   : str                = Field(..., **patient_model_schema['filename'])
        url        : str                = Field(..., **patient_model_schema['url'])
        create_ts  : Optional[datetime] = Field(None, **patient_model_schema['create_ts'])
        update_ts  : Optional[datetime] = Field(None, **patient_model_schema['update_ts'])

    class PatientModelFull(AllowBaseModel):
        id         : Optional[int]      = Field(None, **patient_model_schema['id'])
        name       : Optional[str]      = Field(None, **patient_model_schema['name'])
        patient_id : Optional[int]      = Field(None, **patient_model_schema['patient_id'])
        filename   : Optional[str]      = Field(None, **patient_model_schema['filename'])
        url        : Optional[str]      = Field(None, **patient_model_schema['url'])
        create_ts  : Optional[datetime] = Field(None, **patient_model_schema['create_ts'])
        update_ts  : Optional[datetime] = Field(None, **patient_model_schema['update_ts'])

    class PatientModelUpdate(CustomBaseModel):
        id         : int      = Field(..., **patient_model_schema['id'])
        name       : str      = Field(..., **patient_model_schema['name'])
        patient_id : int      = Field(..., **patient_model_schema['patient_id'])
        filename   : str      = Field(..., **patient_model_schema['filename'])
        url        : str      = Field(..., **patient_model_schema['url'])
        create_ts  : datetime = Field(..., **patient_model_schema['create_ts'])
        update_ts  : datetime = Field(..., **patient_model_schema['update_ts'])

    class PatientModelMerge(PatientModelFull):
        class Config:
            extra = 'forbid'

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'PatientModelSearch',
        List[PatientModelFull],
        'patient-models'
    )

    class PatientModelSearch(_search_tpl):
        pass

    CreateValidator = PatientModelCreate
    FullValidator   = PatientModelFull
    UpdateValidator = PatientModelUpdate
    MergeValidator  = PatientModelMerge
    SearchValidator = PatientModelSearch

    Table = sa.Table(
        'patient_model',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column(
            'patient_id',
            sa.INTEGER(),
            sa.ForeignKey('patient.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column('filename', sa.VARCHAR(512), nullable=False),
        sa.Column('url', sa.TEXT(), nullable=False, index=True),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    id         : int      = None
    name       : str      = None
    patient_id : int      = None
    filename   : str      = None
    url        : str      = None
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
    ) -> 'PatientModel':
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
            ignore_rel_entities: bool = False
    ) -> Optional['PatientModel']:
        return await super().update_static(
            id,
            data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )
