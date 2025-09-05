import urllib.parse
import sqlalchemy as sa

from datetime import datetime, date, timezone
from dataclasses import dataclass
from collections import OrderedDict
from typing import List, Type, Dict, Any, Sequence, Tuple, Union, Callable

from sqlalchemy import text, Column, select
from sqlalchemy.sql.elements import TextClause, UnaryExpression, ColumnClause, BooleanClauseList
from sqlalchemy.testing.schema import Table

from ..models.base_model import braceletBaseModel
from ..models.relation import Relation
from ..exceptions import ValidationError, ErrorType


@dataclass
class JoinMeta:

    @dataclass
    class OnClause:
        left    : Union[Column, Tuple[Union[Column, str, bool, int], ...]]
        right   : Union[Column, Tuple[Union[Column, str, bool, int], ...]]

    table    : Table
    onclause : OnClause
    isouter  : bool = False


class QueryBuilder:
    _pre_build_callbacks : List[Callable]
    _query               : select

    def __init__(self, model: Type[braceletBaseModel]):
        self.model                = model
        self.table                = model.Table
        self._columns             = []
        self._where_list          = []
        self._order_by_list       = []
        self._limit               = None
        self._offset              = None
        self._join_list           = []
        self._q_rel_entities      = []
        self._pre_build_callbacks = []
        self._query               = None
        self._distinct            = False

    def apply_distinct(self, value: bool):
        self._distinct = value
        return self

    def limit(self, limit: int) -> 'QueryBuilder':
        self._limit = limit
        return self

    def offset(self, offset: int) -> 'QueryBuilder':
        self._offset = offset
        return self

    def where(self, expr: Union[UnaryExpression, TextClause, BooleanClauseList, text]) -> 'QueryBuilder':
        self._where_list.append(expr)
        return self
    def order_by(self, expr: Union[UnaryExpression, TextClause]) -> 'QueryBuilder':
        self._order_by_list.append(expr)
        return self

    def add_column(self, column: Column) -> 'QueryBuilder':
        self._columns.append(column)
        return self

    def add_column_by_name(self, name: str) -> 'QueryBuilder':
        self._columns.append( self.model.get_column_by_name(name) )
        return self

    def add_join(self, join_meta: JoinMeta) -> 'QueryBuilder':
        self._join_list.append(join_meta)
        return self

    def add_pre_build_callback(self, fn) -> 'QueryBuilder':
        self._pre_build_callbacks.append(fn)
        return self

    def primary_key_columns(self) -> List[Column]:
        return self.model.get_primary_key_columns()

    def is_joined(self, table: Table) -> bool:
        for join in self._join_list:
            if join.table == table:
                return True

        return False

    def add_relation(self, rel: Relation) -> 'QueryBuilder':
        if rel.join.through:
            self.add_join(
                JoinMeta(
                    table    = rel.join.through.table_class,
                    onclause = JoinMeta.OnClause(
                        left  = rel.join.left,
                        right = rel.join.through.left
                    )
                )
            )

            self.add_join(
                JoinMeta(
                    table    = rel.table,
                    onclause = JoinMeta.OnClause(
                        left  = rel.join.through.left,
                        right = rel.join.right
                    )
                )
            )

        else:
            self.add_join(
                JoinMeta(
                    table    = rel.table,
                    onclause = JoinMeta.OnClause(
                        left  = rel.join.left,
                        right = rel.join.right
                    )
                )
            )

        return self

    # noinspection PyDefaultArgument
    def apply_fields_map(
            self,
            fields_map : Dict[Union[str, Column], Any],
            sort_map   : OrderedDict = {}
    ) -> 'QueryBuilder':
        # checking that sort columns are included in fields
        for sort_col in sort_map.keys():
            if sort_col not in fields_map:
                raise ValidationError(
                    loc  = ['query', 'sort_by', sort_col],
                    msg  = f"the column {sort_col} used for sorting is not available in the fields list",
                    type = ErrorType.BAD_REQUEST
                )

        for col, value in fields_map.items():
            if value is True:  # embedded relations are managed in apply_embed
                if isinstance(col, str):  # If the column is still a string, we need to map it back to sa.Column
                    try:
                        col = self.model.get_column_by_name(col)
                    except KeyError:
                        raise ValidationError(
                            loc  = [ 'query', 'fields', col ],
                            msg  = f"the column {col} specified in fields param is not found on the data model",
                            type = ErrorType.BAD_REQUEST
                        )

                self.add_column(col)

        return self

    # noinspection PyDefaultArgument, PyUnusedLocal
    def apply_sort_map(
            self,
            sort_map            : Dict[Union[str, Column], str],
            reverse_order       : bool = False,
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> 'QueryBuilder':
        # relation_fields = self.model.get_relation_fields()
        # if col in relation_fields:  # Don't process here relation fields
        #     continue
        # relations_found = {}

        for col, order in sort_map.items():
            if isinstance(col, str):  # If the column is still a string, we need to map it back to sa.Column
                # Can be a composite sort key, for example while using embed fields, for example owner_user.name
                # col_fields = col.split('.')
                # if len(col_fields) > 1:
                #     # We need relations if we get here
                #     if all_relations is None:
                #         dyn_relations = await self.model.build_dynamic_relations(context=dynamic_rel_context)
                #         all_relations = { **self.model.get_relations(), **dyn_relations }
                # for elem in col_fields:
                #     if elem not in relations_found:

                try:
                    col = self.model.get_column_by_name(col)
                except KeyError:
                    raise ValidationError(
                        loc  = ['query', 'sort_by', col],
                        msg  = f"the column {col} specified in sort_by param of URL is not found on the data model",
                        type = ErrorType.BAD_REQUEST
                    )

            if reverse_order:  # Reverse_order is used in pagination, for previous pages
                sort_fn = sa.asc if order == 'desc' else sa.desc
            else:
                sort_fn = sa.asc if order == 'asc' else sa.desc

            self.order_by( sort_fn(col) )

        return self

    def apply_q_rel_entities(self, q_rel_entities: List[Tuple]):
        self._q_rel_entities = q_rel_entities
        return self

    def get_q_rel_entities(self) -> List[Tuple]:
        """
        This is needed for some checks in some controllers and to clean app some the q_rel_entities sometimes
        for optimization, for being able to merge some filters
        :return:
        """
        return self._q_rel_entities

    def get_query(self) -> select:
        """
        This is used in some callbacks that needs to be processed before the final build function
        :return:
        """
        return self._query

    def build(self) -> select:
        if self._columns:
            query = select(self._columns)
        else:
            query = self.table.select()

        self._query = query  # Used by some callbacks

        for fn in self._pre_build_callbacks:
            fn()

        for expr in self._where_list:
            query = query.where(expr)

        for expr in self._order_by_list:
            query = query.order_by(expr)

        if self._limit:
            query = query.limit(self._limit)

        if self._offset:
            query = query.offset(self._offset)

        if self._join_list:
            _join = self.table
            for meta in self._join_list:
                join_cond = meta.onclause.left == meta.onclause.right
                if not isinstance( meta.onclause.left, Column ):
                    assert len(meta.onclause.left) == len(meta.onclause.right)

                    join_cond = []
                    for join in zip( meta.onclause.left, meta.onclause.right ):
                        join_cond.append(join[0] == join[1])

                    join_cond = sa.and_(*join_cond)

                _join = _join.join(meta.table, join_cond, isouter=meta.isouter)

            query = query.select_from(_join)

        for relation, where_text, values in self._q_rel_entities:
            rel_model_t = relation.table
            rel_join    = relation.join
            rel_through = rel_join.through

            if rel_through:
                rel_t = rel_through.table_class
                query = query\
                    .where(
                        sa.exists(
                            rel_t.select().select_from(
                                rel_t.join(rel_model_t, rel_join.right == rel_through.right)
                            ).where(
                                sa.and_(
                                    rel_join.left == rel_through.left,
                                    text(where_text).bindparams(**values)
                                )
                            )
                        )
                    )
            else:
                query = query\
                    .where(
                        sa.exists(
                            rel_model_t.select().where(
                                sa.and_(
                                    rel_join.left == rel_join.right,
                                    text(where_text).bindparams(**values)
                                )
                            )
                        )
                    )

        if self._distinct:
            query = query.group_by(
                *list(query.exported_columns)
            )

        return query


class URLPaginatedHelper:
    @classmethod
    def get_base_url(cls, parsed_url: urllib.parse.SplitResult, request_headers: Dict[str, str]) -> str:
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        for header, value in request_headers.items():
            lower_header = header.lower()
            if lower_header == 'x-forwarded-proto':
                scheme = value
            elif lower_header == 'x-forwarded-host':
                netloc = value

        return f"{scheme}://{netloc}{parsed_url.path}"

    @classmethod
    def calculate_pagination(
            cls,
            parsed_url           : urllib.parse.SplitResult,
            request_headers      : Dict[str, str],
            request_query_params : Dict[str, Any],
            records              : Sequence,
            is_last_page         : bool,
            sort_map             : OrderedDict,
            from_prev            : bool
    ) -> Dict[str, str]:

        first_item = None
        last_item  = None

        if records:
            first_item = records[0]
            last_item  = records[-1]

        if is_last_page:
            if from_prev:
                first_item = None
            else:
                last_item  = None

        # noinspection PyTypeChecker
        old_params     = OrderedDict( request_query_params.items() )
        exclude_params = ['pq', 'from_prev']

        if 'pq' not in old_params:
            first_item = None

        for p in exclude_params:
            old_params.pop(p, None)  # Not raise if not found

        new_params = urllib.parse.urlencode(old_params)
        base_url   = cls.get_base_url(parsed_url, request_headers)

        def create_pag_link(item, key):
            is_prev         = key == 'previous'
            pag_params_list = [ cls.build_paginate_query(item, sort_map, is_prev) ]

            if is_prev:
                pag_params_list.append('from_prev=true')

            pag_params = '&'.join(pag_params_list)

            return f"{base_url}?{pag_params}{'&'+new_params if new_params else ''}"

        result = {
            "first"    : base_url,
            "next"     : '',
            "previous" : ''
        }

        if first_item:
            result['previous'] = create_pag_link(first_item, 'previous')

        if last_item:
            result['next'] = create_pag_link(last_item, 'next')

        if new_params:
            result['first'] = f"{result['first']}?{new_params}"

        return result

    @staticmethod
    def build_paginate_query(item, sort_map: OrderedDict, is_prev_link: bool) -> str:

        def build_query_param(field, op, value):
            if isinstance(value, date) or isinstance(value, datetime):
                value = value.isoformat()

            if isinstance(value, str):
                value = f"'{value}'"

            return f"{field}.{op}:{value}"

        sentences = []
        for col, order in sort_map.items():
            if is_prev_link:
                # If we come from a previous link we need to reverse order
                ope = 'lt' if order.lower() == 'asc' else 'gt'
            else:
                ope = 'gt' if order.lower() == 'asc' else 'lt'

            if isinstance(col, ColumnClause):  # If the sort_map field is using a Column we need to translate it to text
                col = col.name

            col_value = item[col]
            if col_value:
                # We need to handle this here because we are using the mapping from tz to non-tz aware datetime
                if isinstance(col_value, datetime) and col_value.tzinfo is not None:
                    col_value = col_value.astimezone(tz=timezone.utc).replace(tzinfo=None)

                sentences.append({
                    'field'  : col,
                    'op'     : ope.upper(),
                    'value'  : col_value
                })

        first_filter  = ""
        added_filters = []

        for i, cond in enumerate(sentences):
            query_param = build_query_param( **cond )

            # this is special because is the first one, it needs to be added with different conditions to the two groups
            if i == 0:
                first_filter = query_param
                added_filters.append( build_query_param(cond['field'], 'EQ', cond['value']) )
            else:
                added_filters.append( query_param )

        paginate_query = first_filter

        # If we need to add other filters to the main query we do it here
        if len(added_filters) > 1:
            added_filters_str = ' AND '.join(added_filters)
            paginate_query    = f"{paginate_query} OR ({added_filters_str})"

        paginate_query = urllib.parse.urlencode({'pq': paginate_query})

        return paginate_query
