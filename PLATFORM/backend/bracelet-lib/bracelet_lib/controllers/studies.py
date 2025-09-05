from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List
from sqlalchemy import Column

import sqlalchemy as sa
from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.patients import Patient
from ..models.studies import Study
from ..models.query_builder import QueryBuilder

class StudyCtrl(braceletBaseCtrl):
    """
    Controller for Study model. Supports CRUD, optional filtering by patient_id,
    range filtering by timestamp, and default ordering by timestamp desc.
    """
    Model = Study
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
    ) -> Tuple[List[Study], bool]:
        """
        Allows:
        - Filtering by patient_id via extra_args['patient_id']
        - Range filtering by timestamp: extra_args['ts_from'], extra_args['ts_to']
        - Default ordering by ts DESC if no sort_map provided
        """
        generic = extra_args.get('filters', [])
        for cond in generic:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.where(cond)
        # Filter by patient
        patient_id = extra_args.get('patient_id')
        if patient_id is not None:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.where(
                cls.Model.Table.c.patient_id == patient_id
            )
        # Filter by timestamp range
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
        # Default ordering by timestamp descending
        if not sort_map:
            builder = builder or QueryBuilder(cls.Model)
            builder = builder.order_by(cls.Model.Table.c.ts.desc())

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
