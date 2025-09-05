# from __future__ import annotations  # Don't do this, enabling here breaks forwardrefs in subclasses, funny eh?
from enum import Enum
from datetime import datetime, timezone

import sqlalchemy as sa
import orjson
import pydantic
from sqlalchemy.dialects import postgresql

# noinspection PyCompatibility
from .. import exceptions


class StrEnum(str, Enum):

    def __str__(self):
        return self.value

    @classmethod
    def values(cls):
        return [v.value for v in cls.__members__.values()]


class SortOrderEnum(StrEnum):
    asc  = 'asc'
    desc = 'desc'
    ASC  = 'ASC'
    DESC = 'DESC'


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class UTCTimeStamp(sa.types.TypeDecorator):
    """
    This column type allows serving and receiving timezone aware, in UTC, datetime, while allowing the
    database to store internally local time, using UTC time, to speed up indexes and simplify management
    """

    impl = sa.types.DateTime(timezone=True)

    def process_bind_param(self, value: datetime, dialect):
        if value is not None:
            if not isinstance(value, datetime):
                # This should not be allowed by Pydantic, just in case...
                raise TypeError('expected datetime.datetime, not ' + repr(value))
            elif value.tzinfo is None:
                raise exceptions.ValidationError(
                    loc  = ['body'],
                    msg  = f'Naive datetime is not allowed, please send timezone aware datetime',
                    type = exceptions.ErrorType.BAD_REQUEST
                )

            # Transform to UTC and clean the timezone later
            return value.astimezone(tz=timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc) if value else value

    @property
    def python_type(self):
        return datetime


# noinspection PyArgumentList
class ORJSONB(sa.types.TypeDecorator):
    """
    This column type allows serving and receiving json types, using orjson (de)serializer
    """

    impl = postgresql.JSONB

    def bind_processor(self, dialect):
        def process(value):
            if value is not None:
                if not isinstance(value, dict):
                    raise TypeError('expected dict, not ' + repr(value))

                return orjson.dumps(value).decode()

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None:
                return orjson.loads(value)

        return process

    def coerce_compared_value(self, op, value):
        return self.impl.coerce_compared_value(op, value)


class BaseModel(pydantic.BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

    @classmethod
    def from_model(cls, model):
        # noinspection PyArgumentList
        return cls( **model.dict() )

    def is_set(self, col) -> bool:
        """
        This is needed to differentiate between values set by __init__ and those default class values
        :param col: column/attribute name to check
        :return: True if the value has been set for the model
        """
        return col in self.dict(exclude_unset=True)


class CustomBaseModel(BaseModel):
    class Config:
        extra = 'forbid'

        json_loads = orjson.loads
        json_dumps = orjson_dumps


class AllowBaseModel(BaseModel):
    class Config:
        extra = 'allow'

        json_loads = orjson.loads
        json_dumps = orjson_dumps

modelClass = CustomBaseModel()
