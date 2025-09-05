from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List
from sqlalchemy import Column, and_
from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.alarm import Alarm
from ..models.patients import Patient
from ..models.query_builder import QueryBuilder


class AlarmCtrl(braceletBaseCtrl):
    """
    Controller for Alarm model. Soporta CRUD y filtrado por paciente, urgencia y rango de tiempo.
    """
    Model       = Alarm
    OwnerColumn = Patient.Table.c.owner_user_id

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
    ) -> Tuple[List[Alarm], bool]:
        """
        Permite filtrar por:
          - patient_id vía extra_args['patient_id']
          - is_urgent vía extra_args['is_urgent']
          - rango de ts vía extra_args['ts_from'] y ['ts_to']
        """
        # Inicializamos el builder si hace falta
        if not builder:
            builder = QueryBuilder(cls.Model)

        # Filtrar por paciente
        patient_id = extra_args.get('patient_id')
        if patient_id is not None:
            builder = builder.where(
                cls.Model.Table.c.patient_id == patient_id
            )

        # Filtrar por urgencia
        is_urgent = extra_args.get('is_urgent')
        if is_urgent is not None:
            builder = builder.where(
                cls.Model.Table.c.is_urgent == is_urgent
            )

        # Filtrar por rango de timestamp
        ts_from = extra_args.get('ts_from')
        ts_to   = extra_args.get('ts_to')
        if ts_from is not None:
            builder = builder.where(
                cls.Model.Table.c.ts >= ts_from
            )
        if ts_to is not None:
            builder = builder.where(
                cls.Model.Table.c.ts <= ts_to
            )

        # Orden por defecto: ts DESC si no vienen instrucciones de sort
        if not sort_map:
            builder = builder.order_by(cls.Model.Table.c.ts.desc())

        # Llamamos al padre para ejecutar la búsqueda
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
