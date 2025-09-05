import typing

from fastapi import Query, Path

from lib import exceptions
from bracelet_lib.models.common import StrEnum


class HTTPResponses:
    search = {
        # 400: {"description": "Bad request"},
        401: {"description": "Unauthorized"}
    }

    get = {
        # 400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"}
    }

    post = {
        # 400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        409: {"description": "Data conflict"}
    }

    put = {
        # 400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        409: {"description": "Data conflict"},
        404: {"description": "Not found"}
    }

    delete = {
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"}
    }


class BasicQueryParams:
    def __init__(
            self,
            q: str = Query(
                None,
                description = 'Query DSL to filter database results.'
            ),
            limit: int = Query(
                50,
                description = 'Limit of number of records to return.'
            ),
            offset: int = Query(
                None,
                description = 'Number of records to skip before returning elements.'
            ),
            sort_by: str = Query(
                None,
                description = 'Column list to use to sort the results, ex: create_ts:desc,name:asc'
            ),
            fields: str = Query(
                None,
                description = 'Field list to include in the result set.'
            ),
            pq: str = Query(
                None,
                description = 'Query DSL used for efficient pagination.'
            ),
            from_prev: bool = Query(
                False,
                description = 'Hint for the pagination engine, it means backwards direction.'
            )
    ):
        self.q          = q
        self.limit      = limit
        self.offset     = offset
        self.sort_by    = sort_by
        self.fields     = fields
        self.pq         = pq
        self.from_prev  = from_prev

    def get_dict(self):
        return self.__dict__


class FieldsQueryParam:
    def __init__(
            self,
            fields: str = Query(
                None,
                description = 'Field list to include in the result set.'
            )
    ):
        self.fields = fields


def build_embed_query_param(
        entities      : type(StrEnum),
        default_value : typing.Any = None
):
    return build_enum_query_param(
        entities        = entities,
        alias           = 'embed',
        description     = 'Related entities to include in the result set.',
        default_value   = default_value,
        raise_not_found = False  # Needed here because of nested embeds
    )


def build_enum_query_param(
        entities        : type(StrEnum),
        alias           : str,
        description     : str,
        default_value   : typing.Any = None,
        raise_not_found : bool = True
):
    class EnumQueryParam:

        # noinspection PyInitNewSignature
        def __init__(
                self,
                enum: type(StrEnum)
        ):
            self.enum        = enum
            self.enum_values = enum.values()

        def __call__(
                self,
                value: str = Query(
                    default_value,
                    alias       = alias,
                    description = description,
                    enum        = entities.values()
                )
        ):
            # If no value is given we handle it taking into account the default value for the argument
            if not value:
                return default_value

            value = value.lower()
            if raise_not_found:
                ent_gen = (e.strip() for e in value.split(','))

                for entity in ent_gen:
                    if entity not in self.enum_values:
                        raise exceptions.ValidationError(
                            loc  = ['query', alias],
                            msg  = f'Invalid {alias} entity: {entity}',
                            type = exceptions.ErrorType.BAD_REQUEST
                        )

            return value

    return EnumQueryParam(enum=entities)


# noinspection PyDefaultArgument
def build_array_int_query_param(alias: str, desc: str = '', ignore: typing.List[str] = []):
    class ArrayIntQueryParam:

        def __call__(
                self,
                array: str = Query('', alias=alias, description=desc)
        ):
            if not array:
                return []

            array     = array.lower()
            array_gen = (i.strip() for i in array.split(','))

            array_valid = []
            for value in array_gen:
                try:
                    # validate non ignored words
                    if value not in ignore:
                        value = int(value)

                    array_valid.append( value )
                except ValueError:
                    raise exceptions.ValidationError(
                        loc  = ['query', alias],
                        msg  = f'value {value} is not a valid integer',
                        type = exceptions.ErrorType.BAD_REQUEST
                    )

            return array_valid

    return ArrayIntQueryParam()


class RelEntitiesQParam:
    """
    Base class for define q param for related entities
    """

    def get_dict(self) -> typing.Dict:
        return { str(k).split('_', 1)[1]: v for k, v in self.__dict__.items() if v }


def build_array_str_query_param(alias: str, desc: str = ''):
    class ArrayStrQueryParam:

        def __call__(
                self,
                array: str = Query('', alias=alias, description=desc)
        ):
            if not array:
                return []

            array     = array.lower()
            array_gen = (i.strip() for i in array.split(','))

            return list(array_gen)

    return ArrayStrQueryParam()


def build_int_or_str_path_param(alias: str, desc: str, valid_str: str = 'any'):
    class IntStrPathParam:

        def __call__(
                self,
                value: str = Path(
                    ...,
                    alias       = alias,
                    description = f"{desc}. Use keyword '{valid_str}' to get all child entities"
                )
        ):
            try:
                return int(value)
            except ValueError:
                if value != valid_str:
                    raise exceptions.ValidationError(
                        loc  = ['path', alias],
                        msg  = f'Invalid value {value}, must be an integer or {valid_str}',
                        type = exceptions.ErrorType.BAD_REQUEST
                    )

            return value

    return IntStrPathParam()
