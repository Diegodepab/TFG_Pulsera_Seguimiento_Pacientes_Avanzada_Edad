import antlr4
import datetime
import orjson

from contextvars import ContextVar
from dataclasses import dataclass
from sqlalchemy import Table, select, Column
from sqlalchemy.sql import Alias
from typing import Dict, List, Mapping, Tuple, Union, Any
from antlr4.error.Errors import ParseCancellationException
from antlr4.error.ErrorStrategy import BailErrorStrategy
from antlr4.tree.Tree import ParseTreeWalker
from query_parser.searchParser import searchParser
from query_parser.searchListener import searchListener
from query_parser.searchLexer import searchLexer
from bracelet_lib.models.relation import Relation

from lib.exceptions import ParserErrorListener
from bracelet_lib.exceptions import ValidationError, ErrorType


field_counter: ContextVar[int] = ContextVar('field_counter', default=0)


def strip_quotes(value):
    if isinstance(value, str) and value[0] == "'" and value[-1] == "'":
        value = value[1:-1]

    return value


@dataclass
class ColCache:
    table_name  : str
    column      : Column
    python_type : Any


class SearchWalker(searchListener):
    rewriter         : str
    values           : Dict
    main_query       : Union[Table, Alias, select]
    field_table_map  : Dict[str, ColCache]

    like_ops = [
        'beg',
        'con',
        'end'
    ]

    def __init__(self):
        super().__init__()

        self.reset()

    def set_main_query(self, main_query: Union[Table, Alias, select]):
        self.main_query      = main_query
        self.field_table_map = {}

        def _get_python_type(col_):
            col_type_str = str(col_.type)
            if col_type_str == 'JSONB':
                cast_func = orjson.loads
            else:
                cast_func = col_.type.python_type

            return cast_func

        try:  # This is used in sub-queries and selects
            for full_col in main_query.inner_columns:
                tbl_, col = str(full_col).split('.')
                python_type = _get_python_type(full_col)

                self.field_table_map[col] = ColCache(tbl_, full_col, python_type)

            # We amplify the query ones with all the available fields in the froms list
            tbl: Union[Table, Alias]
            for tbl in main_query.froms:
                # noinspection PyTypeChecker
                for col in tbl.columns:
                    tbl_name, field_name = str(col).split('.')
                    python_type = _get_python_type(col)
                    if field_name not in self.field_table_map:
                        self.field_table_map[field_name] = ColCache(tbl_name, col, python_type)

        except AttributeError:  # This is the normal route for Table and Alias
            # noinspection PyTypeChecker
            for col in main_query.columns:
                tbl_name, field_name             = str(col).split('.')
                self.field_table_map[field_name] = ColCache(tbl_name, col, col.type.python_type)

    # noinspection PyTypeChecker
    def reset(self):
        self.rewriter          = ''
        self.values            = {}
        self.main_query        = None
        self.field_table_map   = {}

    def enterQuery(self, ctx: searchParser.QueryContext):
        self.rewriter += '('

    def exitQuery(self, ctx: searchParser.QueryContext):
        self.rewriter += ')'

    def enterLog_op(self, ctx: searchParser.Log_opContext):
        self.rewriter += f" {ctx.getText()} "

    def enterTerm_name(self, ctx: searchParser.Term_nameContext):
        operator   = ctx.parentCtx.com_op().getText().lower()
        field_raw  = ctx.getText()

        try:
            table = self.field_table_map[field_raw].table_name
        except KeyError:
            raise ValidationError(
                loc  = ['query', 'q'],
                msg  = f"the column {field_raw} specified in q param of URL is not found on the data model",
                type = ErrorType.QUERY_PARSER_ERROR
            )

        field = f'"{table}".{field_raw}'

        if operator in self.like_ops:
            field = f"lower({field})"

        self.rewriter += field

    def enterValue(self, ctx: searchParser.ValueContext):
        operator = ctx.parentCtx.com_op().getText().lower()
        # NOTE: ctx.children can be a string|number value, or a special_op, or even both.
        # @improvements: check the value's type, if is a special_op, do the "special op flow",
        #   if not (is a string|number value), do the "normal flow" for value

        # @future @improvements: support the combination of special_op + string|number, this is allowed by the parser
        # at this moment
        value = strip_quotes( ctx.getText() )

        if value == '~':
            if operator not in ('eq', 'ne'):
                raise ValidationError(
                    loc=['query', 'q'],
                    msg= f'Error trying to parse q URL param, value {value} is not supported by operator {operator}',
                    type=ErrorType.QUERY_PARSER_ERROR
                )

            if operator == 'eq':
                self.rewriter = self.rewriter.replace('=', 'is null')
            else:
                self.rewriter = self.rewriter.replace('<>', 'is not null')
            return

        next_index_value = field_counter.get()
        field_counter.set(next_index_value + 1)

        field        = ctx.parentCtx.term_name().getText().lower()
        mapping_name = f"{self.field_table_map[field].table_name}_{field}_{next_index_value}"
        cast_func    = self.field_table_map[field].python_type

        if cast_func in (datetime.datetime, datetime.date, datetime.time):
            cast_func = cast_func.fromisoformat
        elif cast_func == bool:
            value = value.lower() in ('true', '1')

        # These operators are case-sensitive so we lower the value before
        if operator in self.like_ops:
            value = value.lower()

        if operator == 'beg':
            value = f"{value}%"
        elif operator == 'con':
            value = f"%{value}%"
        elif operator == 'end':
            value = f"%{value}"
        elif operator == 'in' or operator == 'nin':
            value = [ cast_func(v.strip()) for v in value.split(',') ]

        if isinstance(value, list):
            _field         = mapping_name
            map_values     = [ f":{_field}{i}" for i in range(len(value)) ]
            self.rewriter += f'( {",".join( map_values )} )'

            for n, v in zip(map_values, value):
                self.values[n[1:]] = v
        else:
            self.rewriter             += f':{mapping_name}'
            self.values[mapping_name]  = cast_func(value)

    def enterCom_op(self, ctx: searchParser.Com_opContext):
        txt = ctx.getText().lower()

        if txt == 'eq':
            self.rewriter += ' = '

        elif txt == 'gt':
            self.rewriter += ' > '

        elif txt == 'ge':
            self.rewriter += ' >= '

        elif txt == 'lt':
            self.rewriter += ' < '

        elif txt == 'le':
            self.rewriter += ' <= '

        elif txt == 'ne':
            self.rewriter += ' <> '

        elif txt == 'in':
            self.rewriter += ' IN '

        elif txt == 'nin':
            self.rewriter += ' NOT IN '

        else:
            self.rewriter += ' LIKE '


walker                  = ParseTreeWalker()
search_walker           = SearchWalker()
throwing_error_listener = ParserErrorListener('q', 'Invalid q syntax')
bail_error_strategy     = BailErrorStrategy()


def parse_search(q_text: str, main_table_query: Union[Table, Alias, select]) -> Tuple[str, Dict]:
    chars_search = antlr4.InputStream(q_text)

    lexer_search = searchLexer(chars_search)
    lexer_search.removeErrorListeners()
    lexer_search.addErrorListener(throwing_error_listener)
    lexer_search._errHandler = bail_error_strategy

    tokens_search = antlr4.CommonTokenStream(lexer_search)

    parser_search = searchParser(tokens_search)
    parser_search.removeErrorListeners()
    parser_search.addErrorListener(throwing_error_listener)
    parser_search._errHandler = bail_error_strategy

    tree_query  = parser_search.query()

    # Used to prefix column names if needed or get column types
    search_walker.set_main_query(main_table_query)

    walker.walk(search_walker, tree_query)

    where_text, values = search_walker.rewriter, search_walker.values

    search_walker.reset()

    return where_text, values


def create_db_search_where(q_text: str, main_table_query: Union[Table, Alias, select]) -> Tuple[str, Dict]:
    try:
        where_text, values = parse_search(q_text, main_table_query)
    except ParseCancellationException:
        raise ValidationError(
            loc  = [ 'query',  'q' ],
            msg  = 'Error trying to parse q URL param',
            type = ErrorType.QUERY_PARSER_ERROR
        )
    except KeyError as e:
        raise ValidationError(
            loc  = ['query', 'q'],
            msg  = f"the column {e} specified in q param of URL is not found into data model",
            type = ErrorType.QUERY_PARSER_ERROR
        )

    return where_text, values


def create_db_search_into_rel_entities(q_extra: Dict[str, str], relations: Mapping[str, Relation]) -> List[Tuple]:
    q_rel_entities  = []
    counter_q_extra = 1

    for q_rel, q_text in q_extra.items():
        relation     = relations[q_rel]
        rel_model_t  = relation.table

        try:
            where_text, _values = parse_search(q_text, rel_model_t)

            values = {}
            for k in _values.keys():
                new_key          = f"{k}_q_extra_{counter_q_extra}"
                where_text       = where_text.replace(f":{k}", f":{new_key}", 1)
                values[new_key]  = _values[k]
                counter_q_extra += 1

        except ParseCancellationException:
            raise ValidationError(
                loc  = [ 'query',  f'q.{q_rel}' ],
                msg  = f'Error trying to parse q.{q_rel} URL param',
                type = ErrorType.QUERY_PARSER_ERROR
            )
        except KeyError as e:
            raise ValidationError(
                loc  = ['query', f'q.{q_rel}'],
                msg  = f"the column {e} specified in q.{q_rel} param of URL is not found into related data model",
                type = ErrorType.QUERY_PARSER_ERROR
            )

        q_rel_entities.append(
            (relation, where_text, values)
        )

    return q_rel_entities
