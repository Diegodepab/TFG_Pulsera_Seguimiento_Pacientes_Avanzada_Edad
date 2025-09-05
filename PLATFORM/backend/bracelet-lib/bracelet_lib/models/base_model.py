import functools
import inspect
import enum
import pydantic
import orjson

from typing import (
    Dict,
    Type,
    Union,
    List,
    Generator,
    Sequence,
    Mapping,
    TypeVar,
    Callable,
    Set,
    Any,
    Optional,
    Tuple
)

from decimal import Decimal
from abc import ABC, abstractmethod
from sqlalchemy import Table, select, Column, PrimaryKeyConstraint, func
from sqlalchemy.sql import Alias

from .relation import RelationType
# noinspection PyCompatibility
from .. import exceptions
from ..cache import cache
from . import database_manager, relation
from .common import modelClass


class SaveAction(enum.Enum):
    CREATE = 1
    UPDATE = 2


def json_dumps(obj):
    """
    Helper to use orjson.dumps but allowing bracelet & Pydantic Models
    :param obj:
    :return:
    """
    def default(o):
        if isinstance(o, BaseModel):
            return o.dict()

        elif isinstance(o, pydantic.BaseModel):
            return o.dict(exclude_unset=True)

        elif isinstance(o, Decimal):
            return str(o)

    return orjson.dumps(obj, default=default)


class BaseModel(ABC):
    CreateValidator : modelClass = None
    FullValidator   : modelClass = None
    UpdateValidator : modelClass = None
    MergeValidator  : modelClass = None

    # Dynamic properties we want to use while casting to Dict
    dynamic_properties: Tuple = ()

    def __init__(self, **kwargs):
        """
        This __init__ allows the subclasses to only define the fields at class level, this way when we create a dict
        from the instances we only get the set values, not the defaults one, similar to skip_defaults in pydantic
        :param kwargs:
        """
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    # This one is needed to support dict(obj) used by pydantic validators for creating rest endpoint responses
    def __iter__(self):
        for key in self.dict():
            yield key, getattr(self, key)

    # This one is needed to support subscript operator []
    def __getitem__(self, key):
        return self.__dict__[key]

    # Used to automatically cast some types
    def __setattr__(self, name, value):
        if value is not None:
            if self.__annotations__.get(name, '') == 'Decimal' and not isinstance(value, Decimal):
                value = Decimal( str(value) )

        super().__setattr__(name, value)

    @classmethod
    def from_pydantic(cls, pyd: pydantic.BaseModel, full=True ) -> 'TBaseModel':
        return cls( **pyd.dict(exclude_unset=not full) )

    @classmethod
    def from_str(cls, data: str) -> 'TBaseModel':
        return cls( **dict(orjson.loads(data)) )

    @classmethod
    def from_dict(cls, data: Mapping) -> 'TBaseModel':
        # We use pydantic as a middleware for casting types and validating some fields
        return cls.from_pydantic( cls.FullValidator(**data), full=False )

    @classmethod
    def copy(cls, obj: 'TBaseModel'):
        return cls( **obj.dict() )

    def dict(self, full=False) -> Dict:
        """
        Get model data as dict
        :param full: if full all values will be returned, even the unset ones
        :return: Dictionary with the instance values
        """
        dat = vars(self)  # For the common case whe short circuit here, no need for pydantic or validation
        if full:
            dat = self.FullValidator( **dat ).dict(exclude_unset=False)

        for prop in self.dynamic_properties:
            dat[prop] = getattr(self, prop)

        return dat

    def update(self, obj: 'TBaseModel'):
        """
        Allows to update existing attributes with the ones from a model of the same class
        :param obj:
        """
        if not isinstance(obj, self.__class__):
            raise ValueError("Only same class objects can be used to update a model class object")

        self.update_from_dict(obj.dict())

    def update_from_dict(self, data: Dict):
        for key, value in data.items():
            setattr(self, key, value)

    def json(self, full=False) -> str:
        """
        Get model data as json
        :param full: if full all values will be returned, even the unset ones
        :return: JSON representation for the class instance
        """
        return self.FullValidator( **self.__dict__ ).json(exclude_unset=not full)

    def is_set(self, col) -> bool:
        """
        This is needed to differentiate between values set by __init__ and those default class values
        :param col: column/attribute name to check
        :return: True if the value has been set for the model
        """
        return col in self.__dict__

    @staticmethod
    def validate(validator: modelClass, **kwargs) -> modelClass:
        """
        Function to validate model data
        :param validator: validator class to validate data
        :param kwargs: all the data to load in the validator
        :return: the validator model built
        """
        return validator(**kwargs)

    @classmethod
    @abstractmethod
    async def get_static(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            raise_not_found : bool = True
    ) -> Optional['TBaseModel']:
        pass

    @classmethod
    @abstractmethod
    async def save_static(cls, data: Dict) -> 'TBaseModel':
        pass

    @abstractmethod
    async def save(self, action: Optional[SaveAction] = None):
        pass

    @classmethod
    @abstractmethod
    async def update_static(
            cls,
            id               : Union[int, str, List[Union[int, str]]],
            data             : Dict,
            raise_not_found  : bool = True
    ) -> Optional['TBaseModel']:
        pass

    @classmethod
    @abstractmethod
    async def delete_static(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            raise_not_found : bool = True
    ) -> None:
        pass


class braceletRedisModel(BaseModel):
    Prefix  : str = None
    FieldID : str = 'id'

    @classmethod
    def _get_full_id(cls, id: Union[int, str]):
        return f'{cls.Prefix}-{id}'

    @classmethod
    async def get_static(
            cls,
            id              : Union[int, str],
            raise_not_found : bool = True
    ) -> Optional['TbraceletRedisModel']:
        ret    = None
        record = await cache.get( cls._get_full_id(id) )

        if record is not None:
            ret = cls.from_str(record)
        elif raise_not_found:
            raise exceptions.NotFoundError()

        return ret

    @classmethod
    async def save_static(cls, data: Dict, ttl: Optional[int] = None) -> 'TbraceletRedisModel':
        # If the field_id has a value in the payload we used that, in other case we create an internal ID
        id_value = data.get(cls.FieldID)
        if id_value is None:
            id_value          = await cache.get_next(cls.Prefix)
            data[cls.FieldID] = id_value

        await cache.set( cls._get_full_id(id_value), json_dumps(data), ttl=ttl )

        return cls.from_dict(data)

    async def save(self, action: Optional[SaveAction] = None, ttl: Optional[int] = None) -> 'TbraceletRedisModel':
        cur_id          = getattr(self, self.FieldID, None)
        raise_not_found = True  # Optimization in case of update, no need to check if already loaded from Redis

        if action is None:  # We need to infer the action first
            if cur_id is None:
                action = SaveAction.CREATE
            else:
                rec    = await cache.get( self._get_full_id(cur_id) )
                action = SaveAction.CREATE if rec is None else SaveAction.UPDATE
                raise_not_found = False

        if action == SaveAction.CREATE:
            ret = await self.save_static(self.dict(), ttl=ttl)
        else:
            ret = await self.update_static(cur_id, self.dict(), raise_not_found=raise_not_found, ttl=ttl)

        return ret

    @classmethod
    async def update_static(
            cls,
            id               : Union[int, str],
            data             : Dict,
            raise_not_found  : bool = True,
            ttl              : Optional[int] = None
    ) -> Optional['TbraceletRedisModel']:
        if raise_not_found:
            await cls.get_static(id, raise_not_found=True)

        await cache.set( cls._get_full_id(id), json_dumps(data), ttl=ttl )
        return cls.from_dict(data)

    @classmethod
    async def delete_static(
            cls,
            id              : Union[int, str],
            raise_not_found : bool = False
    ) -> None:
        found = await cache.delete( cls._get_full_id(id) )
        if raise_not_found and not found:
            raise exceptions.NotFoundError()


class braceletBaseModel(BaseModel):
    SearchValidator : modelClass = None
    Table           : Union[Table, Alias, select] = None

    # The following attrs are only needed in models with different names in attr class and DB table columns
    column_translation     : Dict[str, str] = {}
    rev_column_translation : Dict[str, str] = {}

    @staticmethod
    def create_search_schema_static(
            schema_title    : str,
            items_type      : Type,
            entity_endpoint : str,
            prefix          : str = 'https://bracelet.com/v1',
    ) -> Type[pydantic.BaseModel]:
        class Search(pydantic.BaseModel):
            items: items_type

            first: str = pydantic.Field(
                None,
                example = f'{prefix}/{entity_endpoint}?limit=50&sort_by=create_ts:asc'
            )

            next: str = pydantic.Field(
                None,
                example = f'{prefix}/{entity_endpoint}?pq=create_ts.GT:2018-01-02 OR'
                          f' (create_ts.EQ:2018-01-02 AND id.GT:50)&limit=50&sort_by=create_ts:asc'
            )

            previous: str = pydantic.Field(
                None,
                example = f'{prefix}/{entity_endpoint}?pq=create_ts.LT:2017-02-01 OR '
                          f'(create_ts.EQ:2017-02-01 AND id.LT:100)'
                          f'&from_prev=true&limit=50&sort_by=create_ts:asc'
            )

            class Config:
                title = schema_title
                extra = 'forbid'

        return Search

    @classmethod
    def get_primary_key_columns(cls) -> List[Column]:
        if isinstance(cls.Table.primary_key, PrimaryKeyConstraint):
            return cls.Table.primary_key.columns
        else:  # ColumnCollection, this happens in sa.select instances
            # noinspection PyTypeChecker
            return list(cls.Table.primary_key)

    @classmethod
    async def get_next_primary_key_value(cls) -> int:
        if cls.Table.primary_key is None:
            raise ValueError("The table don't have a primary key")

        if len(cls.Table.primary_key.columns) > 1:
            raise ValueError("The table's primary key have more than 1 column")

        pk_column = cls.Table.primary_key.columns[0]

        if not pk_column.autoincrement:
            raise ValueError("The table's primary key column is not autoincrement")

        query = select(func.nextval(f'{cls.Table.name}_{pk_column.name}_seq'))
        rec   = await database_manager.get_db_conn().fetch_one( query )

        return rec[0]

    @classmethod
    def apply_id_where(cls, query: select, id) -> select:
        """
        This function can be used to apply a where filter to a select object that already exists
        :param query: SQLAlchemy select
        :param id: Could be integer or string or UUID, it depends on the pkey of the table
        :return: query: SQLAlchemy select
        """
        pkey_cols = [ c for c in cls.get_primary_key_columns() ]
        ids_list  = id if isinstance(id, list) else [id]

        for col, value in zip( pkey_cols, ids_list ):
            query = query.where( col == value )

        return query

    @classmethod
    def from_pydantic(cls, pyd: pydantic.BaseModel, full=True) -> 'TbraceletModel':
        return cls( **pyd.dict(exclude_unset=not full) )

    @classmethod
    def from_db(cls, record: Mapping) -> 'TbraceletModel':
        return cls( **dict(record.items()) )

    @classmethod
    def from_db_multi(cls, records: Sequence[Mapping]) -> Generator['TbraceletModel', None, None]:
        for record in records:
            yield cls( **dict(record.items()) )

    @classmethod
    async def _load_defaults(cls, data) -> None:
        """
        Used to load default values specified in SQLAlchemy Tables
        Databases need this because of this issue: https://github.com/encode/databases/issues/72
        :param data:
        """
        # noinspection PyTypeChecker
        for column in cls.Table.columns:  # type 'sqlalchemy.sql.base.ImmutableColumnCollection'
            if column.default is not None and column.name not in data:
                value = column.default.arg

                if column.default.is_callable:
                    value = column.default.arg({})
                    if inspect.isawaitable(value):
                        value = await value

                data[column.name] = value

    @classmethod
    async def _save_relation_data(
            cls,
            rel_tables_data : Mapping[ str, Mapping[ str, Union[Mapping[str, Any], relation.Relation] ] ],
            main_record     : Dict,
            action          : SaveAction
    ) -> None:
        for rel_name, rel_info in rel_tables_data.items():
            # noinspection PyShadowingNames
            relation       = rel_info['relation']
            relation_data  = rel_info['data']
            relation_model = relation.model
            relation_table = relation_model.Table
            is_many        = relation.rel_type in (RelationType.HasManyRelation, RelationType.ManyToManyRelation)

            if relation.join.through:
                raise exceptions.ValidationError(
                    loc  = ['body', rel_name],
                    msg  = f'The field {rel_name} is a relation through a linked table, saving embedded'
                           f' like this is unsupported',
                    type = exceptions.ErrorType.BAD_REQUEST
                )

            elif is_many and not isinstance(relation_data, list):
                raise exceptions.ValidationError(
                    loc  = ['body', rel_name],
                    msg  = f'The field {rel_name} must be a list due to its represent a 1 to M or M to M relation',
                    type = exceptions.ErrorType.BAD_REQUEST
                )

            elif relation_model is None:
                raise exceptions.ValidationError(
                    loc  = ['body', rel_name],
                    msg  = f"The field {rel_name} relates to a field created dynamically with a query."
                           f" This is not allowed for nested creation",
                    type = exceptions.ErrorType.BAD_REQUEST
                )

            if not is_many:
                relation_data = [ relation_data ]

            for data_in in relation_data:
                if relation.rel_type in (RelationType.HasOneRelation, RelationType.HasManyRelation):
                    # Update data according FKs values into inserted parent table record
                    for fk in relation_table.foreign_keys:
                        fk_col = fk.column
                        cols_t = fk.constraint.columns

                        if fk_col.table is cls.Table:
                            for col_t in cols_t:
                                # noinspection PyUnresolvedReferences
                                if data_in.get(col_t.name, None) is None:
                                    data_in[col_t.name] = main_record[fk_col]

                if action == action.CREATE:
                    new_record = await relation_model.save_static(data_in, with_transaction=False)
                else:
                    # Here we extract related table PKs data from data_in, if one value of PKs is not present
                    # we assume a CREATE operation
                    do_insert = False
                    update_id = []
                    for pk in relation_model.get_primary_key_columns():
                        pk_data = data_in.get(pk.name)
                        if pk_data is None:
                            do_insert = True
                            break

                        update_id.append( pk_data )

                    if do_insert:
                        new_record = await relation_model.save_static(data_in, with_transaction=False)
                    else:
                        new_record = await relation_model.update_static(update_id, data_in, with_transaction=False)

                if relation.rel_type in (RelationType.BelongsToOneRelation, RelationType.HasOneDependingRelation):
                    # Update data according FKs values into updated main record table record
                    for fk in cls.Table.foreign_keys:
                        fk_col = fk.column
                        cols_t = fk.constraint.columns

                        if fk_col.table is relation_table:
                            for col_t in cols_t:
                                main_record[col_t.name] = new_record[fk_col.name]

    @classmethod
    async def get_static(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            raise_not_found : bool = True
    ) -> Optional['TbraceletModel']:
        query = cls.Table.select()
        query = cls.apply_id_where(query, id)
        rec   = await database_manager.get_db_conn().fetch_one( query )

        if raise_not_found and rec is None:
            raise exceptions.NotFoundError()

        return cls.from_db(rec)

    @classmethod
    async def save_static(
            cls,
            data                : Dict,
            with_transaction    : bool = True,
            ignore_rel_entities : bool = False
    ) -> 'TbraceletModel':
        await cls._load_defaults(data)

        # Not saving dynamic properties
        for dyn_col in cls.dynamic_properties:
            data.pop(dyn_col, None)

        rel_tables_data = {}

        for name, rel in cls.get_relations().items():
            data_rel = data.pop(name, None)

            if data_rel and ignore_rel_entities is False:
                rel_tables_data[name] = {'data': data_rel, 'relation': rel}

        tx = await database_manager.get_db_conn().transaction() if with_transaction else None
        try:
            await cls._save_relation_data(
                {
                    name: rel_info for name, rel_info in rel_tables_data.items()
                    if rel_info['relation'].rel_type == RelationType.HasOneDependingRelation
                },
                data,
                SaveAction.CREATE
            )

            # These need to be handled first because we need the generated ID columns
            await cls._save_relation_data(
                {
                    name: rel_info for name, rel_info in rel_tables_data.items()
                    if rel_info['relation'].rel_type == RelationType.BelongsToOneRelation
                },
                data,
                SaveAction.CREATE
            )

            query = cls.Table \
                .insert() \
                .returning(cls.Table) \
                .values(data)

            inserted = await database_manager.get_db_conn().fetch_one(query)

            # Now, with the main record inserted, we can create the records depending on its ID values
            await cls._save_relation_data(
                {
                    name: rel_info for name, rel_info in rel_tables_data.items()
                    if rel_info['relation'].rel_type in (RelationType.HasOneRelation, RelationType.HasManyRelation)
                },
                inserted,
                SaveAction.CREATE
            )

        except Exception:
            if tx:
                await tx.rollback()
            raise
        else:
            if tx:
                await tx.commit()

        return cls.from_db(inserted)

    async def save(self, action: Optional[SaveAction] = None, with_transaction: bool = True) -> 'TbraceletModel':
        pkey_columns    = self.get_primary_key_columns()
        pkey_values     = list( getattr(self, col.name, None) for col in pkey_columns)
        raise_not_found = False  # Optimization in case of update, no need to check if already loaded from DB

        if action is None:
            if None in pkey_values:
                action = SaveAction
            else:
                rec    = await self.get_static(pkey_values, raise_not_found=False)
                action = SaveAction.CREATE if rec is None else SaveAction.UPDATE
                raise_not_found = False

        if action == SaveAction.CREATE:
            return await self.save_static(self.dict(), with_transaction=with_transaction)
        else:
            return await self.update_static(
                pkey_values,
                self.dict(),
                raise_not_found  = raise_not_found,
                with_transaction = with_transaction
            )

    @classmethod
    async def update_static(
            cls,
            id               : Union[int, str, List[Union[int, str]]],
            data             : Dict,
            raise_not_found  : bool = True,
            with_transaction    : bool = True,
            ignore_rel_entities : bool = False
    ) -> Optional['TbraceletModel']:

        # Not saving dynamic properties
        for dyn_col in cls.dynamic_properties:
            data.pop(dyn_col, None)

        rel_tables_data = {}

        for name, rel in cls.get_relations().items():
            data_rel = data.pop(name, None)

            if data_rel and ignore_rel_entities is False:
                rel_tables_data[name] = {'data': data_rel, 'relation': rel}

        query = cls.Table \
            .update() \
            .returning(cls.Table)

        query = cls.apply_id_where(query, id)

        tx = await database_manager.get_db_conn().transaction() if with_transaction else None
        try:
            await cls._save_relation_data(
                {
                    name: rel_info for name, rel_info in rel_tables_data.items()
                    if rel_info['relation'].rel_type == RelationType.HasOneDependingRelation
                },
                data,
                SaveAction.UPDATE
            )

            # These need to be handled first because we need the generated ID columns
            await cls._save_relation_data(
                {
                    name: rel_info for name, rel_info in rel_tables_data.items()
                    if rel_info['relation'].rel_type == RelationType.BelongsToOneRelation
                },
                data,
                SaveAction.UPDATE
            )

            updated = await database_manager.get_db_conn().fetch_one(query.values(data))

            if updated:
                # Now, with the main record inserted, we can create the records depending on its ID values
                await cls._save_relation_data(
                    {
                        name: rel_info for name, rel_info in rel_tables_data.items()
                        if rel_info['relation'].rel_type in (RelationType.HasOneRelation, RelationType.HasManyRelation)
                    },
                    updated,
                    SaveAction.UPDATE
                )

            elif raise_not_found:
                raise exceptions.NotFoundError()

        except Exception:
            if tx:
                await tx.rollback()
            raise

        if tx:
            await tx.commit()

        # We need to check if is not None because raise_not_found could be False
        obj = None
        if updated is not None:
            obj = cls.from_db(updated)

        return obj

    @classmethod
    async def delete_static(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            raise_not_found  : bool = True,
            with_transaction : bool = True
    ) -> None:
        # Returning is needed to be able to know if the record was found or not
        query = cls.Table \
            .delete() \
            .returning(cls.Table)

        query = cls.apply_id_where(query, id)

        tx = await database_manager.get_db_conn().transaction() if with_transaction else None
        try:
            deleted_id = await database_manager.get_db_conn().execute( query )

            if raise_not_found and deleted_id is None:
                raise exceptions.NotFoundError()

        except Exception:
            if tx:
                await tx.rollback()
            raise

        if tx:
            await tx.commit()

        return

    @classmethod
    def get_column_by_name(cls, name) -> Column:
        """
        This is mostly used in cases where the Table and the model columns are not the same, and you need a mapping
        :return: Column
        """
        if name in cls.column_translation:
            cname  = cls.column_translation[name]
            if cname is not None:
                name = cname

        # Can raise if column not found in the Table
        return cls.Table.columns[name]

    @classmethod
    def get_attr_name_by_column(cls, name: str) -> str:
        """
        This is mostly used in cases where the Table and the model columns are not the same, and you need a mapping
        :return: str
        """
        attr = name
        if name in cls.rev_column_translation:
            attr = cls.rev_column_translation[name]

        return attr

    # noinspection PyDefaultArgument
    @classmethod
    async def build_dynamic_relations(
            cls,
            context: Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Dict[str, relation.Relation]:
        """
        This creates the final versions of the dynamic_relations if the needed information is available in context
        :return:
        """
        dynamic_rel_funcs = cls.get_dynamic_relations()
        dynamic_relations = {}

        for rel_name, args in context.items():
            if rel_name in dynamic_rel_funcs:
                dynamic_relations[rel_name] = await dynamic_rel_funcs[rel_name](**args)

        return dynamic_relations

    @classmethod
    def get_dynamic_relations(cls) -> Dict[str, Callable]:
        """
        This function is used to return the dynamic relations for the model
        Implemented as a function and not a class attribute, so we can import models here
        This way we don't need to create circular references
        """
        # This should be implemented in subclasses
        return {}

    @classmethod
    def get_relations(cls) -> Dict[str, relation.Relation]:
        """
        This function is used to return the static relations for the model
        Implemented as a function and not a class attribute, so we can import models here
        This way we don't need to create circular references
        """
        # This should be implemented in subclasses
        return {}

    @classmethod
    @functools.lru_cache()
    def get_relation_fields(cls) -> Set:
        """
        This function is used to know what fields in model are dedicated to hold
        relation data a.k.a. embed
        :return:
        """
        all_fields = { **cls.get_relations(), **cls.get_dynamic_relations() }.keys()

        return set( all_fields )


# This is needed for places where the expected types are subclasses of this model
TBaseModel            = TypeVar('TBaseModel', bound=BaseModel)
TbraceletModel      = TypeVar('TbraceletModel', bound=braceletBaseModel)
TbraceletRedisModel = TypeVar('TbraceletRedisModel', bound=braceletRedisModel)
