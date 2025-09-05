from datetime import datetime
from typing import Dict, Optional, List, Union
from pydantic import BaseModel, Field
import sqlalchemy as sa

from .common import UTCTimeStamp, CustomBaseModel, AllowBaseModel
from ..models import database_manager
from ..models.base_model import braceletBaseModel


def get_instrument_schema() -> Dict:
    return {
        'id': {
            'ge': 1,
            'example': 1
        },
        'name': {
            'max_length' : 255,
            'example'    : "prototipo de pulsera"
        },
        'filename': {
            'max_length'  : 512,
            "description" : "Filename of the instrument",
            'example'     : '20222207.mp4'
        },
        'model': {
            'max_length' : 255,
            'example'    : "Strauss"
        },
        'url': {
            "description" : "URL of the model glb",
            'example'     : 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        },
        'create_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        },
        'update_ts': {
            'example' : '2020-10-05 14:05:25.643021+00:00'
        }
    }


instrument_schema = get_instrument_schema()


class Instrument(braceletBaseModel):
    class InstrumentCreate(CustomBaseModel):
        id        : Optional[int]                = Field(None, **instrument_schema['id'])
        name      : str                          = Field(..., **instrument_schema['name'])
        filename  : str                          = Field(..., **instrument_schema['filename'])
        model     : str                          = Field(..., **instrument_schema['model'])
        url       : str                          = Field(..., **instrument_schema['url'])
        create_ts : Optional[datetime]           = Field(None, **instrument_schema['create_ts'])
        update_ts : Optional[datetime]           = Field(None, **instrument_schema['update_ts'])

    class InstrumentFull(AllowBaseModel):
        id        : Optional[int]                = Field(None, **instrument_schema['id'])
        name      : Optional[str]                = Field(None, **instrument_schema['name'])
        filename  : Optional[str]                = Field(None, **instrument_schema['filename'])
        model     : Optional[str]                = Field(None, **instrument_schema['model'])
        url       : Optional[str]                = Field(None, **instrument_schema['url'])
        create_ts : Optional[datetime]           = Field(None, **instrument_schema['create_ts'])
        update_ts : Optional[datetime]           = Field(None, **instrument_schema['update_ts'])

    class InstrumentUpdate(CustomBaseModel):
        id        : int                          = Field(..., **instrument_schema['id'])
        name      : str                          = Field(..., **instrument_schema['name'])
        filename  : str                          = Field(..., **instrument_schema['filename'])
        model     : str                          = Field(..., **instrument_schema['model'])
        url       : str                          = Field(..., **instrument_schema['url'])
        create_ts : datetime                     = Field(..., **instrument_schema['create_ts'])
        update_ts : datetime                     = Field(..., **instrument_schema['update_ts'])

    class InstrumentMerge(InstrumentFull):
        class Config:
            extra = 'forbid'
