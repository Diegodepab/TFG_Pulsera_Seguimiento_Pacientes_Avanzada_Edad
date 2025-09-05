import functools
from datetime import datetime, date
from typing import Dict, Optional, List, Union
from pydantic import Field
import sqlalchemy as sa

from . import relation
from .common import UTCTimeStamp, AllowBaseModel, CustomBaseModel
from ..models import database_manager
from ..models.pathologies import Pathology
from ..models.base_model import braceletBaseModel


def get_patient_pathology_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'patient_id': {
            'ge': 1,
            'example': 1
        },
        'pathology_id': {
            'ge': 1,
            'example': 1
        },
        'detection_date': {
            'example': '2024-03-14'
        },
        'create_ts': {
            'example': '2024-03-14 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example': '2024-03-14 14:05:25.643021+00:00'
        }
    }

def get_patient_pathology_multi_item_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'detection_date': {
            'example': '2024-03-14',
        }
    }

patient_pathology_schema            = get_patient_pathology_schema()
patient_pathology_multi_item_schema = get_patient_pathology_multi_item_schema()


class PatientPathologyMultiItem(CustomBaseModel):
    id             : int  = Field(None, **patient_pathology_multi_item_schema['id'])
    detection_date : date = Field(None, **patient_pathology_multi_item_schema['detection_date'])

class PatientPathology(braceletBaseModel):
    class PatientPathologyCreate(CustomBaseModel):
        id             : Optional[int]      = Field(None, **patient_pathology_schema['id'])
        patient_id     : int                = Field(..., **patient_pathology_schema['patient_id'])
        pathology_id   : int                = Field(..., **patient_pathology_schema['pathology_id'])
        detection_date : date               = Field(..., **patient_pathology_schema['detection_date'])
        create_ts      : Optional[datetime] = Field(None, **patient_pathology_schema['create_ts'])
        update_ts      : Optional[datetime] = Field(None, **patient_pathology_schema['update_ts'])

    class PatientPathologyFull(AllowBaseModel):
        id             : Optional[int]      = Field(None, **patient_pathology_schema['id'])
        patient_id     : Optional[int]      = Field(None, **patient_pathology_schema['patient_id'])
        pathology_id   : Optional[int]      = Field(None, **patient_pathology_schema['pathology_id'])
        detection_date : Optional[date]     = Field(None, **patient_pathology_schema['detection_date'])
        create_ts      : Optional[datetime] = Field(None, **patient_pathology_schema['create_ts'])
        update_ts      : Optional[datetime] = Field(None, **patient_pathology_schema['update_ts'])

    class PatientPathologyUpdate(CustomBaseModel):
        id             : int      = Field(..., **patient_pathology_schema['id'])
        patient_id     : int      = Field(..., **patient_pathology_schema['patient_id'])
        pathology_id   : int      = Field(..., **patient_pathology_schema['pathology_id'])
        detection_date : date     = Field(..., **patient_pathology_schema['detection_date'])
        create_ts      : datetime = Field(..., **patient_pathology_schema['create_ts'])
        update_ts      : datetime = Field(..., **patient_pathology_schema['update_ts'])

    class PatientPathologyMultiple(CustomBaseModel):
        patient_id     : int                             = Field(..., **patient_pathology_schema['patient_id'])
        pathologies    : List[PatientPathologyMultiItem] = Field(...)

    class PatientPathologyMerge(PatientPathologyFull):
        class Config:
            extra = 'forbid'

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'PatientPathologySearch',
        List[PatientPathologyFull],
        'patient-pathologies'
    )

    class PatientPathologySearch(_search_tpl): pass

    CreateValidator = PatientPathologyCreate
    FullValidator   = PatientPathologyFull
    UpdateValidator = PatientPathologyUpdate
    MergeValidator  = PatientPathologyMerge
    SearchValidator = PatientPathologySearch

    Table = sa.Table(
        'patient_pathology',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column(
            'patient_id',
            sa.INTEGER(),
            sa.ForeignKey('patient.id', ondelete='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column(
            'pathology_id',
            sa.INTEGER(),
            sa.ForeignKey('pathology.id', ondelete='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column('detection_date', sa.DATE(), nullable=False),
        sa.Column(
            'create_ts',
            UTCTimeStamp(),
            nullable       = False,
            server_default = sa.text('now()'),
            index          = True
        ),
        sa.Column(
            'update_ts',
            UTCTimeStamp(),
            nullable       = False,
            server_default = sa.text('now()')
        )
    )

    id             : int      = None
    patient_id     : int      = None
    pathology_id   : int      = None
    detection_date : date     = None
    create_ts      : datetime = None
    update_ts      : datetime = None

    # Related data
    # noinspection PyUnresolvedReferences
    patient    : 'Patient'   = None
    pathology  : 'Pathology' = None

    @classmethod
    @functools.lru_cache()
    def get_relations(cls) -> Dict:
        from bracelet_lib.models.patients import Patient
        from bracelet_lib.models.pathologies import Pathology

        return {
            'patient': relation.Relation(
                rel_type = relation.RelationType.BelongsToOneRelation,
                model    = Patient,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.patient_id,
                    right   = Patient.Table.c.id
                )
            ),
            'pathology': relation.Relation(
                rel_type = relation.RelationType.HasOneRelation,
                model    = Pathology,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.pathology_id,
                    right   = Pathology.Table.c.id
                )
            )
        }

    @classmethod
    async def save_static(
            cls,
            data                : Dict,
            with_transaction    : bool = True,
            ignore_rel_entities : bool = False
    ) -> 'PatientPathology':
        """
        Save a new PatientPathology instance to the database.

        Args:
            data: Dictionary containing the PatientPathology data
            with_transaction: Whether to use a transaction
            ignore_rel_entities: Whether to ignore related entities

        Returns:
            New PatientPathology instance
        """
        return await super().save_static(
            data,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )

    @classmethod
    async def update_static(
            cls,
            id                  : Union[int, str],
            data                : Dict,
            raise_not_found     : bool = True,
            with_transaction    : bool = True,
            ignore_rel_entities : bool = False
    ) -> Optional['PatientPathology']:
        """
        Update an existing PatientPathology instance.

        Args:
            id: ID of the PatientPathology to update
            data: Dictionary containing the update data
            raise_not_found: Whether to raise an exception if not found
            with_transaction: Whether to use a transaction
            ignore_rel_entities: Whether to ignore related entities

        Returns:
            Updated PatientPathology instance or None if not found
        """
        return await super().update_static(
            id,
            data,
            raise_not_found     = raise_not_found,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )
