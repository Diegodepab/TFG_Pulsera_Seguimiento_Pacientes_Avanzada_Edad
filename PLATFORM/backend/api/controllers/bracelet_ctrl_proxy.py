from enum import Enum

import pydantic
import sqlalchemy as sa
from typing import Union, Sequence, Type, Any, Dict, List, Optional, Callable
from starlette.requests import Request
from cache import AsyncLRU

from bracelet_lib.models.base_model import TBaseModel
from bracelet_lib.models.query_builder import QueryBuilder, URLPaginatedHelper
from bracelet_lib.controllers.base_ctrl import TbraceletCtrl
from bracelet_lib.controllers.users import UserAccountCtrl, PermissionCtrl

from lib import config, exceptions
from walkers.fields import create_embed_fields_maps
from walkers.search import create_db_search_where, create_db_search_into_rel_entities
from walkers.sort import create_sort_map


class PermissionType(str, Enum):
    read   = 'read'
    write  = 'write'
    delete = 'delete'


class PermissionGrantType(str, Enum):
    all  = 'all'
    own  = 'own'
    none = 'none'


class OperationType(str, Enum):
    search = 'search'
    get    = 'get'
    create = 'create'
    update = 'update'
    merge  = 'merge'
    delete = 'delete'

    def get_perm_type(self):
        if self.value in ('search', 'get'):
            return PermissionType.read
        elif self.value in ('create', 'update', 'merge'):
            return PermissionType.write
        else:
            return PermissionType.delete


@AsyncLRU()
async def _get_permission_rec(user_id, user_role, ctrl, perm_type) -> Optional[PermissionGrantType]:
    entity_name  = ctrl.Model.Table.name
    owner_column = ctrl.OwnerColumn

    permission_rec = await PermissionCtrl.get_user_permission(user_id, entity_name=entity_name)
    if permission_rec is not None and permission_rec[perm_type.value] != PermissionGrantType.own:
        return permission_rec[perm_type.value]

    if ctrl.AdminPermissionColumn is not None and user_role == 'admin':
        owner_column = ctrl.AdminPermissionColumn

    if owner_column is not None:
        entity_name = owner_column.table.name

    permission_rec = await PermissionCtrl.get_user_permission(user_id, entity_name=entity_name)
    if permission_rec is not None:
        return permission_rec[perm_type.value]


class braceletCtrlProxy:

    @classmethod
    async def _check_user_permission(
            cls,
            ctrl      : Type[TbraceletCtrl],
            op_type   : OperationType,
            user_id   : Union[int, str, List[Union[int, str]]],
            user_role : str,
            record_id : Union[int, str, Sequence[Union[int, str]]] = None,
            record    : TBaseModel = None,
            builder   : QueryBuilder = None
    ) -> Optional[QueryBuilder]:
        # Here we manage the general case
        perm_type        = op_type.get_perm_type()
        permission_grant = await _get_permission_rec(user_id, user_role, ctrl, perm_type)
        if permission_grant is None or permission_grant == PermissionGrantType.all:
            return builder if op_type == OperationType.search else None

        if permission_grant == PermissionGrantType.none:
            raise exceptions.AuthException(msg='Not enough permissions to use this resource')

        # own permissions
        if op_type == OperationType.search:
            return ctrl.get_records_by_owner_builder(user_id, user_role=user_role, builder=builder)

        elif op_type in (OperationType.get, OperationType.update, OperationType.merge, OperationType.delete):
            assert record_id is not None, "Record_id argument should be filled for this operation type"

            # If we have the id we only need to check if the user it's the owner
            if not (await ctrl.is_record_owner(record_id, user_id, user_role)):
                raise exceptions.AuthException(msg='Not enough permissions to use this resource')

        else:  # Create
            assert record is not None, "Record should be filled for this operation type"
            if not (await ctrl.is_create_record_owner(record, user_id, user_role)):
                raise exceptions.AuthException(msg='Not enough permissions to use this resource')

    # noinspection PyDefaultArgument
    @staticmethod
    async def get(
            ctrl           : Type[TbraceletCtrl],
            id             : Union[int, str, Sequence[Union[int, str]]],
            fields         : str = None,
            embed          : str = None,
            auth_user_info      : Optional[Dict[str, Union[str, int]]] = None,
            extra_args          : Dict[str, Any] = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ):
        fields_embed_data = create_embed_fields_maps( fields, embed, relation_fields=ctrl.Model.get_relation_fields() )

        if auth_user_info:
            await braceletCtrlProxy._check_user_permission(
                ctrl,
                op_type   = OperationType.get,
                user_id   = auth_user_info['user_id'],
                user_role = auth_user_info['user_role'],
                record_id = id
            )

        record = await ctrl.get(
            id,
            fields_map          = fields_embed_data['fields'],
            embed_map           = fields_embed_data['embed'],
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )

        if record:
            record = ctrl.Model.FullValidator.from_model(record)

        return record

    # noinspection PyDefaultArgument
    @staticmethod
    async def search(
            ctrl                : Type[TbraceletCtrl],
            request             : Request,
            builder             : QueryBuilder    = None,
            q                   : str             = None,
            limit               : int             = None,
            offset              : int             = None,
            sort_by             : str             = None,
            fields              : str             = None,
            embed               : str             = None,
            pq                  : str             = None,
            from_prev           : bool            = None,
            max_limit           : int             = None,  # This is used by some special entities that need longer page size
            auth_user_info      : Optional[Dict[str, Union[str, int]]] = None,
            extra_args          : Dict[str, Any]  = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ):
        max_page_size = config.settings.pag_max_size if max_limit is None else max_limit
        limit         = min( limit or config.settings.pag_default_size, max_page_size )

        if auth_user_info:
            builder = await braceletCtrlProxy._check_user_permission(
                ctrl,
                op_type   = OperationType.search,
                user_id   = auth_user_info['user_id'],
                user_role = auth_user_info['user_role']
            )

        if not builder:
            builder = QueryBuilder(ctrl.Model)

        fields_embed_data = create_embed_fields_maps(fields, embed, relation_fields=ctrl.Model.get_relation_fields())
        # fields_embed_data['fields'] come in this form, here 'tipo' is an embedded entity
        #    {'nombre': True, 'id_tipo': True, 'tipo': {'tipo_id': True, 'nombre': True}}

        sort_map = create_sort_map(
            sort_by,
            [c.name for c in builder.primary_key_columns()],
            list( fi for fi, val in fields_embed_data['fields'].items() if not isinstance(val, dict) )
        )

        def add_where(q_text, get_main_query_func):
            where_text, values = create_db_search_where(q_text, get_main_query_func())
            builder.where( sa.text(where_text).bindparams(**values) )

        if pq:
            builder = builder.add_pre_build_callback(
                lambda _pq=pq, y=builder.get_query: add_where(_pq, y)
            )

        if q:
            builder = builder.add_pre_build_callback(
                lambda _q=q, y=builder.get_query: add_where(_q, y)
            )

        if extra_args.get('q_extra'):
            dyn_relations  = await ctrl.Model.build_dynamic_relations(context=dynamic_rel_context)
            q_rel_entities = create_db_search_into_rel_entities(
                extra_args.pop('q_extra'),
                { **ctrl.Model.get_relations(), **dyn_relations }
            )
            builder = builder.apply_q_rel_entities(q_rel_entities)

        records, is_last_page = await ctrl.search(
            builder             = builder,
            fields_map          = fields_embed_data['fields'],
            embed_map           = fields_embed_data['embed'],
            sort_map            = sort_map,
            reverse_query_sort  = from_prev,
            reverse_records     = from_prev,
            limit               = limit,
            offset              = offset,
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )

        pag_links = URLPaginatedHelper.calculate_pagination(
            request.url.components,
            dict(request.headers),
            dict(request.query_params),
            records,
            is_last_page,
            sort_map,
            from_prev
        )

        serial_records = ( o.dict() for o in records )

        return ctrl.Model.SearchValidator(items=serial_records, **pag_links)

    # noinspection PyDefaultArgument
    @classmethod
    async def create(
            cls,
            ctrl                : Type[TbraceletCtrl],
            data                : Union[pydantic.BaseModel, TBaseModel, Dict],
            validate            : bool = True,
            embed               : str  = None,
            auth_user_info      : Optional[Dict[str, Union[str, int]]] = None,
            extra_args          : Dict[str, Any] = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ):
        fields_embed_data = create_embed_fields_maps( None, embed, relation_fields=ctrl.Model.get_relation_fields() )

        if auth_user_info:
            record : TBaseModel = ctrl.cast_as_model(data)
            await braceletCtrlProxy._check_user_permission(
                ctrl,
                op_type   = OperationType.create,
                user_id   = auth_user_info['user_id'],
                user_role = auth_user_info['user_role'],
                record    = record
            )

        record = await ctrl.create(
            data       = data,
            validate   = validate,
            embed_map  = fields_embed_data['embed'],
            extra_args = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )

        if record:
            record = ctrl.Model.FullValidator.from_model(record)

        return record

    # noinspection PyDefaultArgument
    @classmethod
    async def update(
            cls,
            ctrl           : Type[TbraceletCtrl],
            id             : Union[int, str, List[Union[int, str]]],
            data           : Union[pydantic.BaseModel, TBaseModel, Dict],
            validate       : bool = True,
            embed          : str  = None,
            auth_user_info      : Optional[Dict[str, Union[str, int]]] = None,
            extra_args          : Dict[str, Any] = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ):
        fields_embed_data = create_embed_fields_maps( None, embed, relation_fields=ctrl.Model.get_relation_fields() )

        if auth_user_info:
            await braceletCtrlProxy._check_user_permission(
                ctrl,
                op_type   = OperationType.update,
                user_id   = auth_user_info['user_id'],
                user_role = auth_user_info['user_role'],
                record_id = id
            )

        record = await ctrl.update(
            id,
            data                = data,
            validate            = validate,
            embed_map           = fields_embed_data['embed'],
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )

        if record:
            record = ctrl.Model.FullValidator.from_model(record)

        return record

    # noinspection PyDefaultArgument
    @classmethod
    async def merge(
            cls,
            ctrl           : Type[TbraceletCtrl],
            id             : Union[int, str, List[Union[int, str]]],
            data           : Union[pydantic.BaseModel, TBaseModel, Dict],
            validate       : bool          = True,
            embed          : str           = None,
            auth_user_info : Optional[Dict[str, Union[str, int]]] = None,
            extra_args     : Dict[str, Any] = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ):
        fields_embed_data = create_embed_fields_maps( None, embed, relation_fields=ctrl.Model.get_relation_fields() )

        if auth_user_info:
            await braceletCtrlProxy._check_user_permission(
                ctrl,
                op_type   = OperationType.merge,
                user_id   = auth_user_info['user_id'],
                user_role = auth_user_info['user_role'],
                record_id = id
            )

        record = await ctrl.merge(
            id,
            data                = data,
            validate            = validate,
            embed_map           = fields_embed_data['embed'],
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )

        if record:
            record = ctrl.Model.FullValidator.from_model(record)

        return record

    # noinspection PyDefaultArgument
    @classmethod
    async def delete(
            cls,
            ctrl           : Type[TbraceletCtrl],
            id             : Union[int, str, List[Union[int, str]]],
            extra_args     : Dict[str, Any] = {},
            auth_user_info : Optional[Dict[str, Union[str, int]]] = None
    ):
        if auth_user_info:
            await braceletCtrlProxy._check_user_permission(
                ctrl,
                op_type   = OperationType.delete,
                user_id   = auth_user_info['user_id'],
                user_role = auth_user_info['user_role'],
                record_id = id
            )

        await ctrl.delete(id, extra_args=extra_args)

    # noinspection PyDefaultArgument
    @staticmethod
    async def custom_ctrl_method(
            ctrl            : Type[TbraceletCtrl],
            exec_method     : Callable,
            func_params     : Dict                                 = {},
            id_field        : Optional[str]                        = None,
            record          : Optional[TBaseModel]                 = None,
            auth_user_info  : Optional[Dict[str, Union[str, int]]] = None,
            op_type         : OperationType                        = OperationType.get
    ):
        if auth_user_info:
            await braceletCtrlProxy._check_user_permission(
                ctrl,
                op_type   = op_type,
                user_id   = auth_user_info['user_id'],
                user_role = auth_user_info['user_role'],
                record_id = func_params[id_field] if id_field else None,
                record    = record
            )

        return await exec_method(**func_params)
