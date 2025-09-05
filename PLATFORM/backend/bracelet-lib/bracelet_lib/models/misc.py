import functools
from datetime import datetime
from typing import Dict, Optional, List

import sqlalchemy as sa
from pydantic import Field

from . import database_manager, relation
from .base_model import braceletBaseModel
from .common import CustomBaseModel, BaseModel, AllowBaseModel, UTCTimeStamp


def get_country_schema() -> Dict:
    return {
        'code': {
            'max_length': 4,
            'example': 'es'
        },
        'name': {
            'max_length' : 255,
            'example'    : 'Spain'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        }
    }


def get_region_schema() -> Dict:
    return {
        'id': {
            'ge'      : 1,
            'example' : 1
        },
        'name': {
            'max_length': 255,
            'example': 'Málaga'
        },
        'country_code': {
            "description": "Country code, FK to country.code",
            'example'    : 'es'
        }
    }


country_schema = get_country_schema()
region_schema  = get_region_schema()


class Country(braceletBaseModel):
    # noinspection DuplicatedCode
    class CountryCreate(CustomBaseModel):
        code      : str                 = Field(..., **country_schema['code'])
        name      : str                 = Field(..., **country_schema['name'])
        create_ts : Optional[datetime]  = Field(None, **country_schema['create_ts'])
        update_ts : Optional[datetime]  = Field(None, **country_schema['update_ts'])

    # noinspection DuplicatedCode
    class CountryFull(AllowBaseModel):
        code      : Optional[str]       = Field(None, **country_schema['code'])
        name      : Optional[str]       = Field(None, **country_schema['name'])
        create_ts : Optional[datetime]  = Field(None, **country_schema['create_ts'])
        update_ts : Optional[datetime]  = Field(None, **country_schema['update_ts'])

    # noinspection DuplicatedCode
    class CountryUpdate(CustomBaseModel):
        code      : str      = Field(..., **country_schema['code'])
        name      : str      = Field(..., **country_schema['name'])
        create_ts : datetime = Field(..., **country_schema['create_ts'])
        update_ts : datetime = Field(..., **country_schema['update_ts'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'CountrySearch',
        List[CountryFull],
        'counties'
    )
    class CountrySearch(_search_tpl): pass

    CreateValidator = CountryCreate
    FullValidator   = CountryFull
    UpdateValidator = CountryUpdate
    SearchValidator = CountrySearch

    Table = sa.Table(
        'country',
        database_manager.get_metadata(),
        sa.Column('code', sa.VARCHAR(4), primary_key=True),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
        sa.Index(
            'country_name_gist_idx',
            sa.text('name gist_trgm_ops'),
            postgresql_using = 'gist'
        )
    )

    code      : str      = None
    name      : str      = None
    create_ts : datetime = None
    update_ts : datetime = None


class Region(braceletBaseModel):
    # noinspection DuplicatedCode
    class RegionCreate(CustomBaseModel):
        id           : Optional[int] = Field(None, **region_schema['id'])
        name         : str           = Field(..., **region_schema['name'])
        country_code : str           = Field(..., **region_schema['country_code'])

    # noinspection DuplicatedCode
    class RegionFull(BaseModel):
        class Config:
            extra = 'allow'

        id           : Optional[int] = Field(None, **region_schema['id'])
        name         : Optional[str] = Field(None, **region_schema['name'])
        country_code : Optional[str] = Field(None, **region_schema['country_code'])

    # noinspection DuplicatedCode
    class RegionUpdate(CustomBaseModel):
        id           : Optional[int] = Field(..., **region_schema['id'])
        name         : str           = Field(..., **region_schema['name'])
        country_code : str           = Field(..., **region_schema['country_code'])

    # noinspection PyTypeChecker
    _search_tpl = braceletBaseModel.create_search_schema_static(
        'RegionSearch',
        List[RegionFull],
        'regions'
    )
    class RegionSearch(_search_tpl): pass

    CreateValidator = RegionCreate
    FullValidator   = RegionFull
    UpdateValidator = RegionUpdate
    SearchValidator = RegionSearch

    Table = sa.Table(
        'region',
        database_manager.get_metadata(),
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column(
            'country_code',
            sa.VARCHAR(4),
            sa.ForeignKey('country.code', onupdate='CASCADE', ondelete='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column('create_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', UTCTimeStamp(), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('name', 'country_code', name='region_name_country_code_key'),
        sa.Index(
            'region_name_gist_idx',
            sa.text('name gist_trgm_ops'),
            postgresql_using='gist'
        )
    )

    id           : int = None
    name         : str = None
    country_code : str = None
    create_ts    : datetime = None
    update_ts    : datetime = None

    @classmethod
    @functools.lru_cache()
    def get_relations(cls) -> Dict:
        return {
            'country':  relation.Relation(
                rel_type = relation.RelationType.BelongsToOneRelation,
                model    = Country,
                join     = relation.JoinMeta(
                    left    = cls.Table.c.country_code,
                    right   = Country.Table.c.code
                )
            )
        }
