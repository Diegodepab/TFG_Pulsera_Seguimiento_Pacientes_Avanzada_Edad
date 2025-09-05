import asyncio
import pydantic
import itertools
import functools
import urllib.parse

from typing import List, Any, Dict, Union, Optional, Type, Mapping, Sequence, Tuple, TypeVar
from sqlalchemy import join, select, Column, text, tuple_
from collections import defaultdict, OrderedDict

from abc import ABC, abstractmethod
from .storage import blob_storage_ctrl
from .. import util, exceptions
from ..models import database_manager, relation
from ..models.base_model import (
    TBaseModel,
    braceletBaseModel,
    TbraceletModel,
    TbraceletRedisModel,
    braceletRedisModel
)

from ..models.query_builder import QueryBuilder, JoinMeta
from ..models.relation import RelationType, Relation
from ..models.storage import BlobOpType, SignedUrlRequest, SignedUrlResponse
from ..models.users import UserAccount


class BaseCtrl(ABC):
    Model: Type[TBaseModel] = None

    @classmethod
    @abstractmethod
    async def get(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            raise_not_found : bool = True
    ) -> Optional[TBaseModel]:
        pass

    @classmethod
    @abstractmethod
    async def delete(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            raise_not_found : bool = True
    ) -> None:
        pass

    @classmethod
    @abstractmethod
    async def create(
            cls,
            data     : Union[pydantic.BaseModel, TBaseModel, Dict],
            validate : bool = True
    ) -> TBaseModel:
        pass

    @classmethod
    @abstractmethod
    async def update(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            data            : Union[pydantic.BaseModel, TBaseModel, Dict],
            validate        : bool = True,
            raise_not_found : bool = True
    ) -> TBaseModel:
        pass

    @classmethod
    @abstractmethod
    async def merge(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            data            : Union[pydantic.BaseModel, TBaseModel, Dict],
            validate        : bool = True,
            raise_not_found : bool = True
    ) -> TBaseModel:
        pass

    @classmethod
    async def bulk_add_signed_display_url(cls, items: List[TBaseModel]):
        for item in items:
            try:
                signed_response: SignedUrlResponse.GetSignedUrlResponse = await cls.generate_signed_url(
                    operation = BlobOpType.get,
                    blob_url  = item.url
                )

                item.blob_display_url = signed_response.display_url

            except Exception:
                pass

    @classmethod
    async def generate_signed_url(
            cls,
            operation     : BlobOpType,
            blob_url      : str = None,
            prefix_url    : str = None,
            data          : Union[ SignedUrlRequest.PostSignedUrlRequest, SignedUrlRequest.PutSignedUrlRequest ] = None
    ) -> Optional[ SignedUrlResponse ]:
        """
        Generate a signed url to perform the signed request given
        :param operation: Operation done to process response
        :param blob_url: Complete path (including filename) which will be operated (upload, delete, get...)
        :param prefix_url: Path given for post operations, is not required
        :param data: Contains request extra information (post, put)
        :return: Signed url to perform the request
        """

        path = None
        if blob_url is not None:
            parsed_url = urllib.parse.urlparse(blob_url)
            path = parsed_url.path.strip('/')

        if operation == BlobOpType.get:    # GET
            assert path is not None
            display_url = blob_storage_ctrl.get_signed_url(path)

            return SignedUrlResponse.GetSignedUrlResponse(display_url=display_url)

        elif operation == BlobOpType.delete:   # DELETE
            assert path is not None
            delete_url = blob_storage_ctrl.get_delete_signed_url(path)

            return SignedUrlResponse.DeleteSignedUrlResponse(delete_url=delete_url)

        elif operation == BlobOpType.post:  # POST (SINGLE and MULTIPART)
            assert prefix_url is not None
            assert data is not None and isinstance(data, SignedUrlRequest.PostSignedUrlRequest)

            post_id     = data.id if data.id else await cls.Model.get_next_primary_key_value()
            post_path   = f'{prefix_url}/{post_id}/{data.filename}'
            delete_url  = blob_storage_ctrl.get_delete_signed_url(post_path)
            display_url = blob_storage_ctrl.get_signed_url(post_path)

            if data.num_parts > 1:   # POST MULTIPART
                upload_id, complete_url, abort_url = blob_storage_ctrl.get_multipart_data(post_path)
                urls = blob_storage_ctrl.generate_parts_signed_url(
                    upload_id = upload_id,
                    num_parts = data.num_parts,
                    path      = post_path
                )

                response = {
                    'reserved_id'  : post_id,
                    'upload_id'    : upload_id,
                    'urls'         : urls,
                    'display_url'  : display_url,
                    'delete_url'   : delete_url,
                    'complete_url' : complete_url,
                    'abort_url'    : abort_url
                }

                return SignedUrlResponse.PostSignedUrlResponse(**response)

            else:   # POST UNIQUE
                url = blob_storage_ctrl.get_upload_signed_url(post_path)

                response = {
                    'reserved_id' : post_id,
                    'urls'        : [url],
                    'display_url' : display_url,
                    'delete_url'  : delete_url
                }

                return SignedUrlResponse.PostSignedUrlResponse(**response)

        elif operation == BlobOpType.put:   # PUT
            assert path is not None
            assert data is not None and isinstance(data, SignedUrlRequest.PutSignedUrlRequest)

            display_url = blob_storage_ctrl.get_signed_url(path)
            delete_url = blob_storage_ctrl.get_delete_signed_url(path)

            if data.num_parts > 1:   # PUT MULTIPART
                upload_id, complete_url, abort_url = blob_storage_ctrl.get_multipart_data(path)
                urls = blob_storage_ctrl.generate_parts_signed_url(
                    upload_id = upload_id,
                    num_parts = data.num_parts,
                    path      = path
                )

                response = {
                    'upload_id'    : upload_id,
                    'urls'         : urls,
                    'display_url'  : display_url,
                    'delete_url'   : delete_url,
                    'complete_url' : complete_url,
                    'abort_url'    : abort_url
                }

                return SignedUrlResponse.PutSignedUrlResponse(**response)

            else:   # PUT UNIQUE
                url = blob_storage_ctrl.get_upload_signed_url(path)

                response = {
                    'urls'        : [url],
                    'display_url' : display_url,
                    'delete_url'  : delete_url
                }

                return SignedUrlResponse.PutSignedUrlResponse(**response)

        else:
            return None

    @classmethod
    def list_to_id_map(cls, items: List[TBaseModel]) -> Dict:
        pkey_col_names = [pk_column.name for pk_column in cls.Model.Table.primary_key.columns.values()]
        multi_column   = len(pkey_col_names) > 1
        id_map         = {}

        for item in items:
            # Initially a tuple
            key = tuple( getattr(item, col) for col in pkey_col_names )
            if not multi_column:  # but we get the only item if is single column
                key = key[0]

            id_map[key] = item

        return id_map

    @classmethod
    def cast_as_model(cls, data: Union[pydantic.BaseModel, TbraceletModel, Dict]):
        if isinstance(data, braceletBaseModel) or isinstance(data, braceletRedisModel):
            return data  # already in desired format

        elif isinstance(data, pydantic.BaseModel):
            return cls.Model.from_pydantic(data, full=False)

        elif isinstance(data, dict):
            return cls.Model(**data)

        raise ValueError("Not supported input format to cast_as_model func")

    @classmethod
    def _prepare_data(
            cls,
            data          : Union[pydantic.BaseModel, TbraceletModel, Dict],
            validator_cls : Type[pydantic.BaseModel],
            validate      : bool = True
    ) -> Dict:
        is_pydantic = isinstance(data, pydantic.BaseModel)
        is_lib_bm   = isinstance(data, braceletBaseModel) or isinstance(data, braceletRedisModel)

        if validate and validator_cls is None:
            raise RuntimeError(
                f"This class doesn't have a valid validator for this operation, class: {cls.Model}"
            )
        elif is_pydantic and not isinstance(data, validator_cls):
            raise RuntimeError(
                f"You need to pass the correct model validator class, found: {type(data)}, expected: {validator_cls}"
            )
        elif is_lib_bm and not isinstance(data, cls.Model):
            raise RuntimeError(
                f"You need to pass the correct model class, found: {type(data)}, expected: {cls.Model}"
            )

        # Don't need to revalidate if data is already a pydantic instance
        if validate and not is_pydantic:
            if is_lib_bm:
                data = data.dict()

            # Not validating dynamic properties
            for dyn_col in cls.Model.dynamic_properties:
                data.pop(dyn_col, None)

            # noinspection PyTypeChecker
            data        = validator_cls( **dict(data.items()) )
            is_pydantic = True

        # At this point data could be of any type if it hasn't been validated,
        # validated ones would be always 'validator_cls' class
        ret = data
        if is_pydantic:
            ret = data.dict(exclude_unset=True)
        elif is_lib_bm:
            ret = data.dict()

        return ret


class braceletRedisCtrl(BaseCtrl):
    """
    Base class for Redis based models
    """

    Model: Type[TbraceletRedisModel] = None

    def __init__(self, **kwargs):
        pass

    @classmethod
    async def get(
            cls,
            id              : Union[int, str],
            raise_not_found : bool = True
    ) -> Optional[TbraceletRedisModel]:
        """
        Get a specific record from Redis using id

        :param id: Can be the value of the primary key, being a scalar o a tuple, it can also be a value of a UQ col
        :param raise_not_found: raise not found error if the record is not found

        :raises NotFoundError: When the record is not found

        :return: serialized record found
        """
        return await cls.Model.get_static(id, raise_not_found=raise_not_found)

    @classmethod
    async def delete(cls, id: Union[int, str], raise_not_found : bool = True) -> None:
        await cls.Model.delete_static(id, raise_not_found=raise_not_found)

    @classmethod
    async def create(
            cls,
            data      : Union[pydantic.BaseModel, TbraceletRedisModel, Dict],
            validate  : bool = True
    ) -> Optional[TbraceletRedisModel]:
        prep_data = cls._prepare_data(data, cls.Model.CreateValidator, validate=validate)

        return await cls.Model.save_static(prep_data)

    @classmethod
    async def update(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            data            : Union[pydantic.BaseModel, TbraceletRedisModel, Dict],
            validate        : bool = True,
            raise_not_found : bool = True
    ) -> Optional[TbraceletRedisModel]:
        prep_data = cls._prepare_data(data, cls.Model.UpdateValidator, validate=validate)

        return await cls.Model.update_static(id, prep_data, raise_not_found=raise_not_found)

    @classmethod
    async def merge(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            data            : Union[pydantic.BaseModel, TbraceletRedisModel, Dict],
            validate        : bool = True,
            raise_not_found : bool = True
    ) -> Optional[TbraceletRedisModel]:
        prep_data   = cls._prepare_data(data, cls.Model.MergeValidator, validate=validate)
        stored_data = (await cls.Model.get_static(id)).dict()

        stored_data.update(prep_data)
        merged = await cls.Model.update_static(id, stored_data, raise_not_found=raise_not_found)

        return merged


class braceletBaseCtrl(BaseCtrl):
    """
    Base class for controllers
    """

    Model: Type[TbraceletModel] = None
    OwnerColumn: Column            = None  # Used to check owner in permissions
    AdminPermissionColumn: Column  = None  # In some cases this is used to override default behaviour for admins

    def __init__(self, **kwargs):
        pass

    # noinspection PyDefaultArgument
    @classmethod
    def get_filtered_builder(
            cls,
            builder       : Optional[QueryBuilder]               = None,
            joins_meta    : List[JoinMeta]                       = (),
            where_clauses : Dict[Column, Union[int, float, str]] = {}
    ) -> QueryBuilder:
        if not builder:
            builder = QueryBuilder(cls.Model)

        for meta in joins_meta:
            builder = builder.add_join(meta)

        for col, value in where_clauses.items():
            builder = builder.where(
                text( f"{col.table.name}.{col.name} = '{value}'"
                      if isinstance(value, str)
                      else f'{col.table.name}.{col.name} = {value}' )
            )

        return builder

    @classmethod
    @functools.lru_cache()
    def _get_permissions_path(cls, owner_col) -> List[relation.Relation]:
        owner_table_name = owner_col.table.name
        our_table_name   = cls.Model.Table.name

        if owner_table_name == our_table_name:
            return []

        def get_belong_relations(model):
            return (
                rel for rel in model.get_relations().values()
                if rel.rel_type == relation.RelationType.BelongsToOneRelation
            )

        def recursive_search(path, rel):
            path.append(rel)

            if rel.table.name == owner_table_name:
                return path

            for rel in get_belong_relations(rel.model):
                return recursive_search(path, rel)

        found_paths = []
        for rel_ in get_belong_relations(cls.Model):
            found_path = recursive_search([], rel_)
            if found_path:
                found_paths.append(found_path)

        if not found_paths:
            raise exceptions.DataConflictError(
                loc  = [f'{cls.Model.Table.name}'],
                msg  = f'The OwnerColumn is not available as a relation to this model',
                type = exceptions.ErrorType.DATA_CONFLICT
            )

        # We return the shorted path found
        return sorted(found_paths, key=lambda x: len(x))[0]

    @classmethod
    def _owner_user_status_builder(
            cls,
            path_relations : list[Relation],
            builder        : Optional[QueryBuilder],
            owner_col      : Column
    ) -> QueryBuilder:
        if path_relations:
            # The last cached relation should be the owner col one
            for rel_ in path_relations[-1].model.get_relations().values():
                if rel_.join.left == owner_col and rel_.model is UserAccount:
                    builder = builder.add_relation( rel_ )
                    break

        elif cls.Model is not UserAccount and owner_col.table is cls.Model.Table:
            for rel_ in cls.Model.get_relations().values():
                if rel_.model is UserAccount:
                    builder = builder.add_relation( rel_ )
                    break

        # if cls.Model is UserAccount or builder.is_joined(UserAccount.Table):
        #     builder = builder.where(
        #         UserAccount.Table.c.user_status_name != 'deleted'
        #     )

        return builder

    @classmethod
    def get_records_by_owner_builder(
            cls,
            owner_id  : Union[int, str, List[Union[int, str]]],
            user_role : str = 'owner',
            builder   : QueryBuilder = None
    ) -> Optional[QueryBuilder]:
        path_relations = []
        if not builder:
            builder = QueryBuilder(cls.Model)

        owner_col = cls.OwnerColumn

        if user_role == 'admin' and cls.AdminPermissionColumn:
            owner_col = cls.AdminPermissionColumn

        if owner_col is not None:
            for rel in cls._get_permissions_path(owner_col):
                path_relations.append(rel)
                builder = builder.add_relation(rel)

            builder = cls._owner_user_status_builder(path_relations, builder, owner_col)
            builder = builder.where(owner_col == owner_id)

        return builder

    @classmethod
    async def is_record_owner(
            cls,
            record_id : Union[int, str, List[Union[int, str]]],
            owner_id  : Union[int, str, List[Union[int, str]]],
            user_role : str
    ) -> bool:
        path_relations = []
        ok        = True
        owner_col = cls.OwnerColumn

        if user_role == 'admin' and cls.AdminPermissionColumn:
            owner_col = cls.AdminPermissionColumn

        if owner_col is not None:
            builder = QueryBuilder(cls.Model)

            for rel in cls._get_permissions_path(owner_col):
                path_relations.append(rel)
                builder = builder.add_relation(rel)

            builder = cls._owner_user_status_builder(path_relations, builder, owner_col)
            builder.add_column( owner_col )  # only interested in this column from the resultant join

            query  = cls.Model.apply_id_where(builder.build(), record_id)
            record = await database_manager.get_db_conn().fetch_one(query)

            if not record:
                raise exceptions.NotFoundError()

            ok = record[owner_col] == owner_id

        return ok

    @classmethod
    async def is_create_record_owner(
            cls,
            record    : TBaseModel,
            owner_id  : Union[int, str, List[Union[int, str]]],
            user_role : str
    ) -> bool:
        """
        This is used to check permissions before writing an entity, it loads parent information if needed
        :param record:  Record to check, this will be the one created if check passes
        :param owner_id: Owner to check for
        :param user_role: The role of the user whom permissions will be checked
        :return:
        """
        ok        = True
        owner_col = cls.OwnerColumn

        if user_role == 'admin' and cls.AdminPermissionColumn:
            owner_col = cls.AdminPermissionColumn

        if owner_col is not None:
            if owner_col.table == record.Table:
                ok = getattr(record, owner_col.name, None) == owner_id
            else:
                builder = None
                for rel in cls._get_permissions_path(owner_col):
                    if builder is None:  # First model
                        builder   = QueryBuilder(rel.model)
                        left_col  = rel.join.left
                        right_col = rel.join.right
                    else:
                        builder = builder.add_relation(rel)

                builder.add_column( owner_col )  # only interested in this column from the resultant join

                # Get the needed values for the record
                # noinspection PyUnboundLocalVariable
                left_cols  = left_col if isinstance(left_col, tuple) else (left_col,)
                # noinspection PyUnboundLocalVariable
                right_cols = right_col if isinstance(right_col, tuple) else (right_col,)

                left_values = []
                for col in left_cols:
                    l_value = col
                    if isinstance(col, Column):
                        l_value = getattr(record, col.name, None)

                    left_values.append(l_value)

                for r_col, l_val in zip(right_cols, left_values):
                    builder = builder.where( r_col == l_val )

                query = builder.build()
                record = await database_manager.get_db_conn().fetch_one(query)

                if not record:
                    raise exceptions.NotFoundError()

                ok = record[owner_col] == owner_id

        return ok

    # noinspection PyDefaultArgument
    @staticmethod
    def apply_special_sort(
            builder    : QueryBuilder,
            column     : Column,
            sort_order : str,
            fields_map : Dict[Union[str, Column], Any],
            sort_map   : OrderedDict
    ) -> QueryBuilder:
        # If some fields are defined, the one used to sort will need to be defined as well
        if fields_map:
            fields_map[column] = True
        else:
            # If not, we need to add all the model columns and later on add our custom column
            # noinspection PyTypeChecker
            util.consume( map(builder.add_column, builder.table.columns) )
            builder = builder.add_column( column )

        # We update the sort_map with this added field, the field needs to be the first for pagination to work ok
        sort_map[column] = sort_order
        sort_map.move_to_end(column, last=False)

        return builder

    # noinspection PyDefaultArgument, Duplicates
    @classmethod
    async def apply_embed(
            cls,
            records             : List[TbraceletModel],
            fields_map          : Dict[Union[str, Column], Any],
            embed_map           : Dict,
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> None:
        """
        This functions modifies a list of SQLAlchemy records in place adding the specified entities in the embed field
        :param records: List of TbraceletModel records
        :param fields_map: Map with the fields to get from the database
        :param embed_map: Map with the entities to embed
        :param dynamic_rel_context: used to create dynamic relations from models to do nested embed
        :return: None: it's a modification in place
        """
        dyn_relations = await cls.Model.build_dynamic_relations(context=dynamic_rel_context)
        all_relations = { **cls.Model.get_relations(), **dyn_relations }

        async def embed_field(
                cname        : str,
                c_records    : List[Union[TbraceletModel, Dict]],
                c_relation   : Relation,
                c_fields_map : Dict,
                c_embed_map  : Union[Dict, bool]
        ):
            # noinspection PyArgumentList
            records_map         = defaultdict(list)
            left_cols           = c_relation.join.left
            join_               = c_relation.table
            embed_multi         = c_relation.rel_type in (RelationType.HasManyRelation, RelationType.ManyToManyRelation)
            reverse_cols        = c_relation.join.right
            remove_cols         = set()
            through_link_prefix = '_link_'
            multi_column        = True

            # We manually put left a right columns in a tuple if the relation is single-column
            if not isinstance(left_cols, tuple):
                multi_column = False
                left_cols    = (left_cols,)
                reverse_cols = (reverse_cols,)

            # Default to all columns
            col_list = list(c_relation.table.c)

            # If Fields is defined we check if cname are in
            if c_fields_map:

                # If cname are in Fields we check what columns show
                if cname in c_fields_map:

                    # If cname value in Field is a dict with values, we embed those columns
                    if isinstance(c_fields_map[cname], dict) and c_fields_map[cname]:
                        try:
                            if c_relation.is_dynamic():
                                col_list = [
                                    c_relation.table.c[n] for n in c_fields_map[cname]
                                    if fields_map[cname][n] is True
                                ]
                            else:
                                col_list = [
                                    c_relation.model.get_column_by_name(n) for n in c_fields_map[cname]
                                    if n not in c_relation.model.get_relations()
                                ]

                        except KeyError as col:
                            raise exceptions.ValidationError(
                                loc  = [ 'query', 'fields', cname, str(col) ],
                                msg  = f"the column {str(col)} specified in {cname} field "
                                       f"is not found on related data model",
                                type = exceptions.ErrorType.BAD_REQUEST
                            )

                # Cname not defined into Fields then we ignore this embed op
                else:
                    return

            for rec in c_records:
                # We operate with dicts here, one of the reason is we needed to test against instance set values,
                # the class has None values for all the attributes, so the attribute always exists at class level
                if isinstance(rec, braceletBaseModel):
                    rec = rec.dict()

                # Check duplicated name
                if cname in rec:
                    raise exceptions.DataConflictError(
                        loc  = [f'relation with {cname}'],
                        msg  = f"There is a problem with the model, it's using the same name for the embed "
                               f"as one of the columns, {cname}",
                        type = exceptions.ErrorType.DATA_CONFLICT
                    )

                # Init empty value
                rec[cname]  = [] if embed_multi else {}
                left_values = []

                for left in left_cols:
                    left_value = left  # This is for custom values as literal strings

                    if isinstance(left, Column):  # This is the usual case
                        # noinspection PyUnresolvedReferences
                        if left.name not in rec:
                            # noinspection PyUnresolvedReferences
                            translated_name = cls.Model.get_attr_name_by_column(left.name)
                            raise exceptions.ValidationError(
                                loc  = [ 'query', 'fields', 'embed' ],
                                msg  = f'You need to include {translated_name} to the list of fields to include,'
                                       f' because is needed to apply embed for {cname}',
                                type = exceptions.ErrorType.BAD_REQUEST
                            )

                        # noinspection PyUnresolvedReferences
                        left_value = rec[left.name]

                    left_values.append(left_value)

                if multi_column:
                    records_map[tuple(left_values)].append(rec)
                else:
                    records_map[left_values[0]].append(rec)

            if c_relation.is_dynamic():
                # If dynamic relations the reverse column is always added because is part of the custom query
                # This is needed for being able to create a relation.join.right column, we remove it from the results
                for col in reverse_cols:
                    remove_cols.add( col.name )

            for col in reverse_cols:
                if col not in col_list:
                    # In the case of static relations, if the column to use for the join is not included in the fields
                    # list we include it silently here, we will remove it before returning the results
                    remove_cols.add( col.name )
                    col_list.append( col )

            # If the entity to be included is using a link table we handle it here.
            if c_relation.join.through:
                multi_column = False  # Not supported here
                # tuple is needed to support the general multi column case
                reverse_cols = ( c_relation.join.through.left, )

                # Specifying through what table columns to join (to avoid AmbiguousForeignKeysError)
                join_ = join(
                    c_relation.table,
                    c_relation.join.through.table_class,
                    c_relation.join.right == c_relation.join.through.right
                )

                # We add the column to be used and remove it later from the results
                remove_cols.add( reverse_cols[0].name )
                col_list.append( reverse_cols[0] )

                # If this is set we need to add the link table fields
                if c_relation.join.through.add_link:
                    # noinspection PyTypeChecker
                    col_list.extend(
                        c.label(f'{through_link_prefix}{c.name}')
                        for c in c_relation.join.through.table_class.columns
                    )

            # noinspection PyTypeChecker
            if multi_column:
                where_expr = tuple_(*reverse_cols).in_( cval for cval in records_map if None not in cval )
            else:
                where_expr = reverse_cols[0].in_( cval for cval in records_map if cval is not None)

            # We need to filter out nones for cases when left_value is None in record, we are not going to find those
            # in the database
            query = select(col_list)\
                .select_from(join_)\
                .where( where_expr )

            for rec in await database_manager.get_db_conn().fetch_all(query):
                if multi_column:
                    right_values = []
                    for rcol in reverse_cols:
                        if isinstance(rcol, str):  # This is for custom values as literal strings
                            right_value = rcol
                        else:
                            right_value = rec[rcol]

                        right_values.append(right_value)

                    d_list = records_map[tuple(right_values)]
                else:
                    d_list = records_map[rec[reverse_cols[0]]]

                rec = dict(rec)
                for rcol in remove_cols:
                    del rec[rcol]

                # We need to move the joined tables a _link children
                if c_relation.join.through and c_relation.join.through.add_link:
                    link = {}
                    for col_name in list(rec):
                        if col_name.startswith(through_link_prefix):
                            clean_col_name       = col_name.replace(through_link_prefix, '', 1)
                            link[clean_col_name] = rec.pop(col_name)

                    if c_relation.join.through.additional_fields:
                        for col in c_relation.join.through.additional_fields:
                            rec[col] = link[col]
                    else:
                        rec['_link'] = link

                if c_relation.model:
                    embed_obj = c_relation.model.from_db(rec).dict()
                else:
                    embed_obj = dict(rec)

                for d in d_list:
                    # We create shallow copy for the object, this is needed in cases where some nested embeds
                    # is using a multi_embed, because if a copy is not created here all the items would be a reference
                    # to the same object in memory, ex: ticket lines with same product where we want to embed articles.
                    embed_obj_copy = embed_obj.copy()

                    # We cast here dict embedded data to the model
                    if c_relation.model:
                        embed_obj_copy = c_relation.model.from_dict(embed_obj_copy)

                    if embed_multi:
                        d[cname].append(embed_obj_copy)
                    else:
                        d[cname] = embed_obj_copy

            nested_coroutines = []
            # noinspection PyTypeChecker
            if isinstance(c_embed_map, dict):  # Do nested embed
                if c_relation.is_dynamic():
                    raise exceptions.ValidationError(
                        loc  = [ 'query', 'embed', cname ],
                        msg  = 'Nested embeds not supported for dynamic relations',
                        type = exceptions.ErrorType.BAD_REQUEST
                    )

                nested_model             = c_relation.model
                nested_dynamic_relations = await nested_model.build_dynamic_relations(context=dynamic_rel_context)
                nested_all_relations     = { **nested_model.get_relations(), **nested_dynamic_relations }

                for nested_cname in c_embed_map.keys():
                    if nested_cname in nested_model.get_dynamic_relations()\
                            and nested_cname not in nested_all_relations:
                        raise exceptions.ValidationError(
                            loc  = [ 'query', 'embed', cname, nested_cname ],
                            msg  = f'Some context information is missing to build the'
                                   f' dynamic relation for {nested_cname}',
                            type = exceptions.ErrorType.BAD_REQUEST
                        )

                    if nested_cname not in nested_all_relations:
                        raise exceptions.ValidationError(
                            loc  = [ 'query', 'embed', cname, nested_cname ],
                            msg  = f'The relation {nested_cname} does not exists in related model',
                            type = exceptions.ErrorType.BAD_REQUEST
                        )

                    # flat the list of lists!list(chain.from_iterable(l))'
                    nested_records = []
                    for ent_record in itertools.chain.from_iterable(records_map.values()):
                        ent_value = ent_record[cname]
                        # Only process items with values
                        if ent_value:
                            if isinstance(ent_value, list):
                                nested_records.extend(ent_value)
                            else:
                                nested_records.append(ent_value)

                    nested_relation   = nested_all_relations[nested_cname]
                    nested_embed_map  = c_embed_map[nested_cname]
                    nested_fields_map = {}

                    if isinstance(c_fields_map, dict):
                        nested_fields_map = c_fields_map.get(cname, {})

                    nested_coroutines.append(
                        embed_field(
                            nested_cname,
                            nested_records,
                            nested_relation,
                            nested_fields_map,
                            nested_embed_map
                        )
                    )

                if nested_coroutines:
                    await asyncio.gather( *nested_coroutines )

            return

        def get_relation(cname):
            if cname not in all_relations:
                raise exceptions.ValidationError(
                    loc  = [ 'query', 'embed', cname ],
                    msg  = f'The relation {cname} does not exists in model',
                    type = exceptions.ErrorType.BAD_REQUEST
                )

            return all_relations[cname]

        # We parallelize all embeds
        await asyncio.gather(
            *list(
                embed_field(cname, records, get_relation(cname), fields_map, embed_map[cname])
                for cname in embed_map.keys()
            )
        )

    # noinspection PyDefaultArgument
    @classmethod
    async def search(
            cls,
            builder            : QueryBuilder                  = None,
            fields_map         : Dict[Union[str, Column], Any] = {},
            embed_map          : Dict[str, Union[bool, Dict]]  = {},
            sort_map           : Union[OrderedDict, Dict]      = {},
            reverse_query_sort : bool                          = False,
            reverse_records    : bool                          = False,
            limit              : Optional[int]                 = None,
            offset             : Optional[int]                 = None,
            where_conds        : Sequence[Tuple[str, Mapping]] = (),
            extra_args         : Dict[str, Any]                = {},  # This is added to allow flexibility in children
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Tuple[List[TbraceletModel], bool]:
        if not builder:
            builder = QueryBuilder(cls.Model)

        if limit:
            builder = builder.limit(limit + 1)

        if offset:
            builder = builder.offset(offset)

        if fields_map:
            builder = builder.apply_fields_map(fields_map, sort_map=sort_map)

        if sort_map:
            builder = builder.apply_sort_map(
                sort_map,
                reverse_order       = reverse_query_sort,
                dynamic_rel_context = dynamic_rel_context
            )

        for where_text, values in where_conds:
            builder = builder.where( text(where_text).bindparams(**values) )

        db_records   = await database_manager.get_db_conn().fetch_all(builder.build())
        records      = db_records[:limit]
        is_last_page = len(db_records) == len(records)

        if reverse_records:
            records = list(reversed(records))

        records = list( cls.Model.from_db_multi(records) )

        if embed_map:
            await cls.apply_embed(
                records,
                fields_map,
                embed_map,
                dynamic_rel_context = dynamic_rel_context
            )

        return records, is_last_page

    # noinspection PyDefaultArgument
    @classmethod
    async def get(
            cls,
            id                 : Union[int, str, List[Union[int, str]]],
            fields_map         : Optional[Dict[Union[str, Column], Any]] = None,
            embed_map          : Optional[Dict[str, Union[bool, Dict]]]  = None,
            builder            : QueryBuilder         = None,
            field_name         : str                  = None,
            raise_not_found    : bool                 = True,
            extra_args         : Mapping[str, Any]    = {},  # This is added to allow flexibility in children
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Optional[TbraceletModel]:
        """
        Get a specific record from database using id or a UNIQUE column

        :param id: Can be the value of the primary key, being a scalar o a tuple, it can also be a value of a UQ col
        :param fields_map: fields to return for the model class
        :param embed_map: other entities to embed with the result
        :param builder: if set, this builder than can be pre-filtered will be use instead of creating a new one
        :param field_name: if set, this will be the field to use for search instead of the pkey for the table
        :param raise_not_found: if set, not found error will be raised if the record is not found
        :param extra_args: Use by some children to add custom configurations or filters
        :param dynamic_rel_context: Used to build dynamic relationships for embeds

        :raises NotFoundError: When the record is not found

        :return: serialized record found
        """
        if not builder:
            builder = QueryBuilder(cls.Model)

        if fields_map:
            builder.apply_fields_map(fields_map)

        if not field_name:  # Use pkey
            query = cls.Model.apply_id_where(builder.build(), id)
        else:
            query = builder.where( cls.Model.get_column_by_name(field_name) == id ).build()

        record = await database_manager.get_db_conn().fetch_one(query)

        # raise NotFound
        if not record and raise_not_found:
            raise exceptions.NotFoundError()

        ret = None
        if record:
            # If found we need to apply embed
            records = [ cls.Model.from_db( record ) ]

            if embed_map:
                await cls.apply_embed(
                    records,
                    fields_map,
                    embed_map,
                    dynamic_rel_context = dynamic_rel_context
                )

            ret = records[0]

        return ret

    # noinspection PyDefaultArgument
    @classmethod
    async def create(
            cls,
            data                : Union[pydantic.BaseModel, TbraceletModel, Dict],
            validate            : bool = True,
            embed_map           : Optional[Dict[str, Union[bool, Dict]]] = None,
            with_transaction    : bool = True,
            extra_args          : Mapping[str, Any] = {},  # This is added to allow flexibility in children
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {},
            ignore_rel_entities : bool = False  # Used when we don't want to automatically update related entities
       ) -> TbraceletModel:
        prep_data = cls._prepare_data(data, cls.Model.CreateValidator, validate=validate)

        created = await cls.Model.save_static(
            prep_data,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )

        if not embed_map:
            return created

        created    = created.dict()
        created_id = []
        for col in cls.Model.get_primary_key_columns():
            created_id.append( created[ col.name ] )

        return await cls.get(created_id, embed_map=embed_map, dynamic_rel_context=dynamic_rel_context)

    @classmethod
    def _check_id_in_sync(
            cls,
            id   : Union[int, str, List[Union[int, str]]],
            data : Mapping
    ):
        pkey_cols = [c for c in cls.Model.Table.primary_key.columns]
        id_list   = id if isinstance(id, list) else [id]

        for col, value in zip(pkey_cols, id_list):
            data_value = data.get(col.name)  # Needed for merge, the id column/s could not be in the payload
            if data_value is not None and value != data_value:
                raise exceptions.ValidationError(
                    loc  = [col.name],
                    msg  = f'Path {col.name} and body {col.name} are not in sync',
                    type = exceptions.ErrorType.BAD_REQUEST
                )

    # noinspection PyDefaultArgument
    @classmethod
    async def update(
            cls,
            id                  : Union[int, str, List[Union[int, str]]],
            data                : Union[pydantic.BaseModel, TbraceletModel, Dict],
            validate            : bool = True,
            raise_not_found     : bool = True,
            embed_map           : Optional[Dict[str, bool]] = None,
            with_transaction    : bool = True,
            extra_args          : Mapping[str, Any] = {},  # This is added to allow flexibility in children
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {},
            ignore_rel_entities : bool = False  # Used when we don't want to automatically update related entities
    ) -> Optional[TbraceletModel]:
        prep_data = cls._prepare_data(data, cls.Model.UpdateValidator, validate=validate)
        print('merge??', id,prep_data)
        cls._check_id_in_sync(id, prep_data)

        updated = await cls.Model.update_static(
            id,
            prep_data,
            raise_not_found     = raise_not_found,
            with_transaction    = with_transaction,
            ignore_rel_entities = ignore_rel_entities
        )

        if embed_map is not None:
            updated = await cls.get(id, embed_map=embed_map, dynamic_rel_context=dynamic_rel_context)

        return updated

    # noinspection PyDefaultArgument
    @classmethod
    async def merge(
            cls,
            id                  : Union[int, str, List[Union[int, str]]],
            data                : Union[pydantic.BaseModel, TbraceletModel, Dict],
            validate            : bool = True,
            raise_not_found     : bool = True,
            embed_map           : Optional[Dict[str, bool]] = None,
            with_transaction    : bool = True,
            extra_args          : Mapping[str, Any] = {},  # This is added to allow flexibility in children
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Optional[TbraceletModel]:
        prep_data = cls._prepare_data(data, cls.Model.MergeValidator, validate=validate)
        cls._check_id_in_sync(id, prep_data)


        merged = await cls.Model.update_static(
            id,
            prep_data,
            raise_not_found  = raise_not_found,
            with_transaction = with_transaction
        )
        if embed_map is not None:
            merged = await cls.get(id, embed_map=embed_map, dynamic_rel_context=dynamic_rel_context)

        return merged

    # noinspection PyDefaultArgument
    @classmethod
    async def delete(
            cls,
            id              : Union[int, str, List[Union[int, str]]],
            raise_not_found  : bool = True,
            extra_args       : Mapping[str, Any] = {},  # This is added to allow flexibility in children
            with_transaction : bool = True    ) -> None:
        await cls.Model.delete_static(id, raise_not_found=raise_not_found, with_transaction=with_transaction)

    # noinspection PyDefaultArgument
    @classmethod
    async def get_dynamic_model_relations(
            cls,
            context: Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Dict[str, Relation]:
        return await cls.Model.build_dynamic_relations(context)


# This is needed for places where the expected types are subclasses of this model
TbraceletCtrl = TypeVar('TbraceletCtrl', bound=braceletBaseCtrl)
TMBaseCtrl      = TypeVar('TMBaseCtrl', bound=BaseCtrl)
