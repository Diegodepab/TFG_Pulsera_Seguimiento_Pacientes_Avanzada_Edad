from sqlalchemy import Column
import sqlalchemy as sa

from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.pathologies import Pathology
from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List

from ..models.query_builder import QueryBuilder, JoinMeta
from ..models import unaccent_text

class PathologyCtrl(braceletBaseCtrl):
    Model       = Pathology
    OwnerColumn = Pathology.Table.c.id

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

        pathology_t = cls.Model.Table

        fts_query = sa.select([
            pathology_t.c.id,
            sa.cast(
                pathology_t.c.name.op('<->')(fts),
                sa.Numeric(5, 4)
            ).label('match_distance')
        ]).select_from(
            pathology_t
        ).where(
            sa.or_(
                unaccent_text(pathology_t.c.name) % unaccent_text(fts),
                unaccent_text(pathology_t.c.name).op('%>')(unaccent_text(fts))
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
    ) -> Tuple[List[Pathology], bool]:
        fts_text = extra_args.get('fts')

        if not builder:
            builder = QueryBuilder(cls.Model)

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
