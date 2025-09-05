from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List
from sqlalchemy import Column
from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.messages import Message
from ..models.query_builder import QueryBuilder

class MessageCtrl(braceletBaseCtrl):
    """
    Controller for Message model. Supports CRUD and optional filtering by chat_id and sender_id.
    """
    Model = Message
    OwnerColumn = None  # Messages are not 'owned' by a single user, access control via chat membership

    # noinspection PyDefaultArgument
    @classmethod
    async def search(
            cls,
            builder            : QueryBuilder = None,
            fields_map         : Dict[Union[str, Column], Any] = {},
            embed_map          : Dict[str, Union[bool, Dict]] = {},
            sort_map           : Union[OrderedDict, Dict] = {},
            reverse_query_sort : bool = False,
            reverse_records    : bool = False,
            limit              : Optional[int] = None,
            offset             : Optional[int] = None,
            where_conds        : Sequence[Tuple[str, Mapping]] = (),
            extra_args         : Dict[str, Any] = {},
            dynamic_rel_context: Dict[str, Dict[str, Union[str, int]]] = {}
    ) -> Tuple[List[Message], bool]:
        """
        Allows filtering by:
        - chat_id via extra_args['chat_id']
        - sender_id via extra_args['sender_id']
        - time range via extra_args['ts_from'], extra_args['ts_to']
        Default sort: ts ascending
        """
        chat_id = extra_args.get('chat_id')
        if chat_id is not None:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.where(
                cls.Model.Table.c.chat_id == chat_id
            )
        sender_id = extra_args.get('sender_id')
        if sender_id is not None:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.where(
                cls.Model.Table.c.sender_id == sender_id
            )
        ts_from = extra_args.get('ts_from')
        ts_to   = extra_args.get('ts_to')
        if ts_from:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.where(
                cls.Model.Table.c.ts >= ts_from
            )
        if ts_to:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.where(
                cls.Model.Table.c.ts <= ts_to
            )
        # Default sort by message timestamp ascending
        if not sort_map:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.order_by(cls.Model.Table.c.ts.asc())

        return await super().search(
            builder             = builder,
            fields_map          = fields_map,
            embed_map           = embed_map,
            sort_map            = sort_map,
            reverse_query_sort  = reverse_query_sort,
            reverse_records     = reverse_records,
            limit               = limit,
            offset              = offset,
            where_conds         = where_conds,
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )
