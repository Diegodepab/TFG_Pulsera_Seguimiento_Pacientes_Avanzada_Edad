from sqlalchemy import Column
import sqlalchemy as sa

from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.patients import Patient, GenderType
from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List

from ..models.query_builder import QueryBuilder, JoinMeta
from ..models import unaccent_text


class PatientCtrl(braceletBaseCtrl):
    Model       = Patient
    OwnerColumn = Patient.Table.c.owner_user_id

    @classmethod
    async def apply_user_access_filter(
            cls,
            builder: QueryBuilder,
            auth_user_info: Dict[str, Union[str, int]],
            extra_args: Dict[str, Any] = {}
    ) -> QueryBuilder:
        """
        Aplicar filtros de acceso basados en el rol del usuario.
        - Admin: ve todos los pacientes
        - User (doctor): ve solo sus pacientes (owner_user_id)
        - Patient: ve solo su propia información (patient_user_id)
        """
        user_role = auth_user_info.get('user_role')
        user_id = auth_user_info.get('user_id')
        
        if user_role == 'admin':
            # Admin puede ver todos los pacientes
            return builder
        elif user_role == 'user':
            # Doctor ve solo sus pacientes
            builder = builder.add_where_condition(
                cls.Model.Table.c.owner_user_id == user_id
            )
        elif user_role == 'patient':
            # Paciente ve solo su propia información
            builder = builder.add_where_condition(
                cls.Model.Table.c.patient_user_id == user_id
            )
        else:
            # Si no tiene un rol reconocido, no puede ver nada
            builder = builder.add_where_condition(
                sa.literal(False)
            )
            
        return builder

    # noinspection PyDefaultArgument
    @classmethod
    async def _apply_fts_sort_builder(
            cls,
            builder    : QueryBuilder                  = None,
            fts        : str                           = "",
            fields_map : Dict[Union[str, Column], Any] = {},
            sort_map   : OrderedDict                   = {}
    ):
        if not builder:
            builder = QueryBuilder(cls.Model)

        patient_t = cls.Model.Table

        fts_query = sa.select([
            patient_t.c.id,
            sa.cast(
                patient_t.c.code.op('<->')(fts),
                sa.Numeric(5, 4)
            ).label('match_distance')
        ]).select_from(
            patient_t
        ).where(
            sa.or_(
                unaccent_text(patient_t.c.code) % unaccent_text(fts),
                unaccent_text(patient_t.c.code).op('%>')(unaccent_text(fts))
            )
        ).alias('fts')

        builder = builder.add_join(
            JoinMeta(
                table    = fts_query,
                onclause = JoinMeta.OnClause(
                    left  = cls.Model.Table.c.id,
                    right = fts_query.c.id
                )
            )
        )

        builder = cls.apply_special_sort(
            builder    = builder,
            column     = fts_query.c.match_distance,
            sort_order = 'asc',
            fields_map = fields_map,
            sort_map   = sort_map
        )

        return builder

    # noinspection PyDefaultArgument
    @classmethod
    async def search(
            cls,
            builder            : QueryBuilder                             = None,
            fields_map         : Dict[Union[str, Column], Any]            = {},
            embed_map          : Dict[str, Union[bool, Dict]]             = {},
            sort_map           : Union[OrderedDict, Dict]                 = {},
            reverse_query_sort : bool                                     = False,
            reverse_records    : bool                                     = False,
            limit              : Optional[int]                            = None,
            offset             : Optional[int]                            = None,
            where_conds        : Sequence[Tuple[str, Mapping]]            = (),
            extra_args         : Dict[str, Any]                           = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Tuple[List[Patient], bool]:
        fts_text = extra_args.get('fts')
        auth_user_info = extra_args.get('auth_user_info', {})

        if not builder:
            builder = QueryBuilder(cls.Model)

        # Aplicar filtros de acceso de usuario
        if auth_user_info:
            builder = await cls.apply_user_access_filter(
                builder=builder,
                auth_user_info=auth_user_info,
                extra_args=extra_args
            )

        if fts_text is not None:
            builder = await cls._apply_fts_sort_builder(
                builder    = builder,
                fts        = fts_text,
                fields_map = fields_map,
                sort_map   = sort_map
            )

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

    @classmethod
    async def find_by_id(
            cls,
            id: Union[int, str],
            embed_map: Dict[str, Union[bool, Dict]] = {},
            extra_args: Dict[str, Any] = {}
    ) -> Optional[Patient]:
        """
        Sobrescribir find_by_id para aplicar filtros de acceso de usuario.
        """
        auth_user_info = extra_args.get('auth_user_info', {})
        
        if not auth_user_info:
            return await super().find_by_id(id, embed_map, extra_args)
            
        builder = QueryBuilder(cls.Model)
        builder = builder.add_where_condition(cls.Model.Table.c.id == id)
        
        # Aplicar filtros de acceso
        builder = await cls.apply_user_access_filter(
            builder=builder,
            auth_user_info=auth_user_info,
            extra_args=extra_args
        )
        
        results, _ = await cls.search(
            builder=builder,
            embed_map=embed_map,
            extra_args=extra_args,
            limit=1
        )
        
        return results[0] if results else None


class GenderTypeCtrl(braceletBaseCtrl):
    Model = GenderType
