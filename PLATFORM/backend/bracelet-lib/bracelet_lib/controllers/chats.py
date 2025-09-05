from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List
import sqlalchemy as sa
from sqlalchemy import Column, or_, asc, desc

from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.chats import Chat
from ..models.users import UserAccount
from ..models.query_builder import QueryBuilder, JoinMeta

class ChatCtrl(braceletBaseCtrl):
    """
    Controller for Chat model. Soporta CRUD, filtrado por participante
    y ordenamiento simple por nombre/apellidos del otro usuario.
    """
    Model       = Chat
    OwnerColumn = None

    @classmethod
    async def _check_administration_status(cls, user1_id: int, user2_id: int) -> bool:
        """
        Verifica si alguno de los dos usuarios es admin.
        Retorna True si al menos uno tiene role_name = 'admin'.
        """
        try:
            from ..models import database_manager
            
            query = sa.select(UserAccount.Table.c.role_name).where(
                UserAccount.Table.c.id.in_([user1_id, user2_id])
            )
            
            async with database_manager.get_session() as session:
                result = await session.execute(query)
                roles = [row[0] for row in result.fetchall()]
                
                # Verificar si alguno de los roles es 'admin'
                return 'admin' in roles
                
        except Exception as e:
            # En caso de error, retornar False por defecto
            print(f"Error checking administration status: {e}")
            return False

    @classmethod
    async def save_static(
        cls,
        data: Dict,
        with_transaction: bool = True,
        ignore_rel_entities: bool = False
    ) -> Chat:
        """
        Override save to automatically set administration field based on participants' roles.
        """
        # Extraer user IDs
        user1_id = data.get('user1_id')
        user2_id = data.get('user2_id')
        
        # Si no se especifica administration, calcularlo automáticamente
        if 'administration' not in data and user1_id and user2_id:
            data['administration'] = await cls._check_administration_status(user1_id, user2_id)
        
        return await super().save_static(
            data,
            with_transaction=with_transaction,
            ignore_rel_entities=ignore_rel_entities
        )

    @classmethod
    async def update_static(
        cls,
        id: Union[int, str],
        data: Dict,
        raise_not_found: bool = True,
        with_transaction: bool = True,
        ignore_rel_entities: bool = False
    ) -> Optional[Chat]:
        """
        Override update to recalculate administration field if participants change.
        """
        # Si se están actualizando los participantes, recalcular administration
        if ('user1_id' in data or 'user2_id' in data) and 'administration' not in data:
            # Obtener el chat actual para tener los IDs completos
            existing_chat = await cls.get_by_id_static(id)
            if existing_chat:
                user1_id = data.get('user1_id', existing_chat.user1_id)
                user2_id = data.get('user2_id', existing_chat.user2_id)
                data['administration'] = await cls._check_administration_status(user1_id, user2_id)
        
        return await super().update_static(
            id,
            data,
            raise_not_found=raise_not_found,
            with_transaction=with_transaction,
            ignore_rel_entities=ignore_rel_entities
        )

    @classmethod
    def _build_fields_map(cls):
        """
        Mapea claves de sort_map a columnas:
         - 'other_first_name', 'other_last_name' en UserAccount
         - 'create_ts' en Chat
         - 'administration' en Chat
        """
        chat_t = cls.Model.Table
        user_t = UserAccount.Table.alias('other_user')

        return {
            'create_ts'        : chat_t.c.create_ts,
            'administration'   : chat_t.c.administration,
            'other_first_name' : user_t.c.first_name,
            'other_last_name'  : user_t.c.last_name,
        }, user_t

    @classmethod
    async def _apply_sort_builder(
        cls,
        builder  : QueryBuilder,
        sort_map : OrderedDict[str, str]
    ) -> QueryBuilder:
        """
        Aplica JOIN y ORDER BY para cada campo en sort_map.
        Solo maneja other_first_name/other_last_name y create_ts.
        """
        chat_t = cls.Model.Table
        fields_map, user_t = cls._build_fields_map()

        for field, direction in sort_map.items():
            col = fields_map.get(field)
            if col is None:
                continue

            # Si es campo del otro usuario, agregamos el JOIN
            if field.startswith('other_'):
                builder = builder.add_join(
                    JoinMeta(
                        table    = user_t,
                        onclause = or_(
                            chat_t.c.user1_id == user_t.c.id,
                            chat_t.c.user2_id == user_t.c.id
                        )
                    )
                )

            # Aplicamos ASC o DESC
            if direction.upper() == 'ASC':
                builder = builder.order_by(asc(col))
            else:
                builder = builder.order_by(desc(col))

        return builder

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
    ) -> Tuple[List[Chat], bool]:
        """
        Filtra por extra_args['user_id'] y aplica orden dinámico
        por other_first_name/other_last_name si se especifica,
        o create_ts DESC por defecto.
        """
        # 1) Filtrado por participante
        user_id = extra_args.get('user_id')
        if user_id is not None:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.where(
                or_(
                    cls.Model.Table.c.user1_id == user_id,
                    cls.Model.Table.c.user2_id == user_id
                )
            )

        # 2) Orden dinámico si viene sort_map
        if sort_map:
            builder = builder or QueryBuilder(cls.Model)
            builder = await cls._apply_sort_builder(builder, OrderedDict(sort_map))
        else:
            # Orden por defecto: fecha de creación descendente
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.order_by(cls.Model.Table.c.create_ts.desc())

        # 3) Delegar paginación, filtros extra y embeddings
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
