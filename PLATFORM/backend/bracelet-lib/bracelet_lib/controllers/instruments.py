from sqlalchemy import Column
import sqlalchemy as sa

from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.instruments import Instrument
from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List

from ..models.query_builder import QueryBuilder, JoinMeta
from ..models import unaccent_text


class InstrumentCtrl(braceletBaseCtrl):
    Model       = Instrument
    OwnerColumn = Instrument.Table.c.id

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

        instrument_t = cls.Model.Table

        fts_query = sa.select([
            instrument_t.c.id,
            sa.cast(
                instrument_t.c.name.op('<->')(fts),
                sa.Numeric(5, 4)
            ).label('match_distance')
        ]).select_from(
            instrument_t
        ).where(
            sa.or_(
                unaccent_text(instrument_t.c.name) % unaccent_text(fts),
                unaccent_text(instrument_t.c.name).op('%>')(unaccent_text(fts))
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
    ) -> Tuple[List[Instrument], bool]:
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
    ) -> Optional[Instrument]:
        add_blob_display_url = extra_args.get('add_blob_display_url')

        instrument = await super().get(
            id                = id,
            fields_map        = fields_map,
            embed_map         = embed_map,
            builder           = builder,
            field_name        = field_name,
            raise_not_found   = raise_not_found,
            dynamic_rel_context = dynamic_rel_context
        )

        if add_blob_display_url:
            await InstrumentCtrl.bulk_add_signed_display_url([instrument])

        return instrument
