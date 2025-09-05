import functools
from datetime import datetime, date
from typing import Dict, Optional, List, Union
from pydantic import Field
import sqlalchemy as sa

from . import relation
from .common import UTCTimeStamp, AllowBaseModel, CustomBaseModel, StrEnum
from ..models import database_manager
from ..models.base_model import braceletBaseModel


def get_patient_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'code': {
            'max_length': 255,
            'example': "01293"
        },
        "gender": {
            'max_length'  : 64,
            "description" : "Gender type, FK to gender_type.name",
            "example"     : 'male'
        },
        'weight': {
            'ge': 0,
            'example': 70
        },
        'birth_date': {
            'example': '1990-01-01'
        },
        'owner_user_id': {
            'description': 'The owner of the billing account that created this user',
            'example': 1
        },
        'patient_user_id': {
            'description': 'The user account ID of the patient themselves (nullable)',
            'example': 15
        },
        'create_ts': {
            'example': '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example': '2020-10-05 14:05:25.643021+00:00'
        }
    }


def get_gender_type_schema() -> Dict:
    return {
        'name': {
            'max_length' : 255,
            'example'    : 'standard'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021'
        }
    }



patient_schema     = get_patient_schema()
gender_type_schema = get_gender_type_schema()


class GenderTypeNameEnum(StrEnum):
    MALE   = 'male'
    FEMALE = 'female'


class GenderType(braceletBaseModel):
    class GenderTypeCreate(CustomBaseModel):
        name      : str                = Field(..., **gender_type_schema['name'])
        create_ts : Optional[datetime] = Field(None, **gender_type_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **gender_type_schema['update_ts'])

    # noinspection DuplicatedCode
    class GenderTypeFull(AllowBaseModel):
        name      : Optional[str]      = Field(None, **gender_type_schema['name'])
        create_ts : Optional[datetime] = Field(None, **gender_type_schema['create_ts'])
        update_ts : Optional[datetime] = Field(None, **gender_type_schema['update_ts'])

    class GenderTypeUpdate(CustomBaseModel):
        name       : str                = Field(..., **gender_type_schema['name'])
        create_ts : Optional[datetime] = Field(..., **gender_type_schema['create_ts'])
        update_ts : Optional[datetime] = Field(..., **gender_type_schema['update_ts'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'GenderTypeSearch',
        List[GenderTypeFull],
        'gender-types'
    )
    class GenderTypeSearch(_search_tpl): pass

    CreateValidator = GenderTypeCreate
    FullValidator   = GenderTypeFull
    UpdateValidator = GenderTypeUpdate
    SearchValidator = GenderTypeSearch

    Table = sa.Table(
        'gender_type',
        database_manager.get_metadata(),
        sa.Column('name', sa.VARCHAR(64), primary_key=True),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
    )

    name      : str      = None
    create_ts : datetime = None
    update_ts : datetime = None


class Patient(braceletBaseModel):
    class PatientCreate(CustomBaseModel):
        id               : Optional[int]      = Field(None, **patient_schema['id'])
        code             : str                = Field(...,  **patient_schema['code'])
        gender           : GenderTypeNameEnum = Field(...,  **patient_schema['gender'])
        weight           : int                = Field(...,  **patient_schema['weight'])
        birth_date       : date               = Field(...,  **patient_schema['birth_date'])
        owner_user_id    : Optional[int]      = Field(None, **patient_schema['owner_user_id'])
        patient_user_id  : Optional[int]      = Field(None, **patient_schema['patient_user_id'])
        create_ts        : Optional[datetime] = Field(None, **patient_schema['create_ts'])
        update_ts        : Optional[datetime] = Field(None, **patient_schema['update_ts'])

    class PatientFull(AllowBaseModel):
        id              : Optional[int]      = Field(None, **patient_schema['id'])
        code            : Optional[str]      = Field(None, **patient_schema['code'])
        gender          : Optional[GenderTypeNameEnum] = Field(
            None,
            **patient_schema['gender']
        )
        weight          : Optional[int]      = Field(None, **patient_schema['weight'])
        birth_date      : Optional[date]     = Field(None, **patient_schema['birth_date'])
        owner_user_id   : Optional[int]      = Field(None, **patient_schema['owner_user_id'])
        patient_user_id : Optional[int]      = Field(None, **patient_schema['patient_user_id'])
        create_ts       : Optional[datetime] = Field(None, **patient_schema['create_ts'])
        update_ts       : Optional[datetime] = Field(None, **patient_schema['update_ts'])

    class PatientUpdate(CustomBaseModel):
        id              : int                = Field(..., **patient_schema['id'])
        code            : str                = Field(..., **patient_schema['code'])
        gender          : GenderTypeNameEnum = Field(..., **patient_schema['gender'])
        weight          : int                = Field(..., **patient_schema['weight'])
        birth_date      : date               = Field(..., **patient_schema['birth_date'])
        owner_user_id   : Optional[int]      = Field(..., **patient_schema['owner_user_id'])
        patient_user_id : Optional[int]      = Field(..., **patient_schema['patient_user_id'])
        create_ts       : datetime           = Field(..., **patient_schema['create_ts'])
        update_ts       : datetime           = Field(..., **patient_schema['update_ts'])

    class PatientMerge(PatientFull):
        class Config:
            extra = 'forbid'

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'PatientSearch',
        List[PatientFull],
        'patients'
    )
    class PatientSearch(_search_tpl): pass

    CreateValidator = PatientCreate
    FullValidator   = PatientFull
    UpdateValidator = PatientUpdate
    MergeValidator  = PatientMerge
    SearchValidator = PatientSearch

    Table = sa.Table(
        'patient',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('code', sa.VARCHAR(255), nullable=False, unique=True),
        sa.Column(
            'gender',
            sa.VARCHAR(64),
            sa.ForeignKey('gender_type.name', onupdate='CASCADE'),
            nullable       = False,
            index          = True
        ),
        sa.Column('weight', sa.INTEGER(), nullable=False),
        sa.Column('birth_date', sa.DATE(), nullable=False),
        sa.Column(
            'owner_user_id',
            sa.INTEGER(),
            sa.ForeignKey('user_account.id', onupdate='CASCADE'),
            nullable  = False
        ),
        sa.Column(
            'patient_user_id',
            sa.INTEGER(),
            sa.ForeignKey('user_account.id', onupdate='CASCADE'),
            nullable  = True,
            index     = True
        ),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'))
    )

    id              : int      = None
    code            : str      = None
    gender          : str      = None
    weight          : int      = None
    birth_date      : date     = None
    owner_user_id   : int      = None
    patient_user_id : int      = None
    create_ts       : datetime = None
    update_ts       : datetime = None

    # Related data
    # noinspection PyUnresolvedReferences
    patient_pathologies    : 'List[PatientPathology]'    = None
    patient_models         : 'List[PatientModel]'        = None
    owner_user             : 'UserAccount'               = None
    patient_user           : 'UserAccount'               = None

    @classmethod
    @functools.lru_cache()
    def get_relations(cls) -> Dict:
        from bracelet_lib.models.patient_pathologies import PatientPathology
        from bracelet_lib.models.users import UserAccount
        from bracelet_lib.models.patient_models import PatientModel

        return {
            'patient_pathologies': relation.Relation(
                rel_type = relation.RelationType.HasManyRelation,
                model    = PatientPathology,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.id,
                    right   = PatientPathology.Table.c.patient_id
                )
            ),
            'patient_models': relation.Relation(
                rel_type = relation.RelationType.HasManyRelation,
                model    = PatientPathology,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.id,
                    right   = PatientModel.Table.c.patient_id
                )
            ),
            'owner_user': relation.Relation(
                rel_type = relation.RelationType.BelongsToOneRelation,
                model    = UserAccount,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.owner_user_id,
                    right   = UserAccount.Table.c.id
                )
            ),
            'patient_user': relation.Relation(
                rel_type = relation.RelationType.BelongsToOneRelation,
                model    = UserAccount,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.patient_user_id,
                    right   = UserAccount.Table.c.id
                )
            )
        }

    @classmethod
    async def save_static(
            cls,
            data: Dict,
            with_transaction    : bool = True,
            ignore_rel_entities : bool = False
    ) -> 'Patient':
        """
        Save a new Patient instance to the database.
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
    ) -> Optional['Patient']:
        """
        Update an existing Patient instance.
        """
        return await super().update_static(
            id,
            data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )
