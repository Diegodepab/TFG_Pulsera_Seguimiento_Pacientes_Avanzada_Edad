import antlr4
import typing

from antlr4.error.ErrorStrategy import BailErrorStrategy
from antlr4.tree.Tree import ParseTreeWalker
from collections import OrderedDict

from query_parser.sortParser import sortParser
from query_parser.sortListener import sortListener
from query_parser.sortLexer import sortLexer
from lib.exceptions import ParserErrorListener


class SortWalker(sortListener):
    sort_data: typing.List

    def __init__(self):
        super().__init__()

    def enterSort(self, ctx: sortParser.SortContext):
        self.sort_data = []

    def enterSort_expression(self, ctx: sortParser.Sort_expressionContext):
        txt = ctx.getText()

        # This heuristic is difficult to read, a refactor should be done in the grammar to allow proper parent detection
        while txt.find('(') != -1:
            l_pos = txt.find('(')
            r_pos = txt.find(')')

            l_block = txt.rfind(',', 0, l_pos)
            r_block = txt.find(',', r_pos)

            if l_block == -1:
                l_block = 0
            if r_block == -1:
                r_block = len(txt)

            txt = txt[:l_block] + txt[r_block:]

            # It will be empty if we are processing a children relation
            if not txt:
                return

            if txt[0] == ',':
                txt = txt[1:]
            if txt[-1] == ',':
                txt = txt[:-1]

        for expr in txt.split(','):
            field, order = ( t.strip() for t in expr.split(':') )
            self.sort_data.append({
                'expr'  : field,
                'order' : order
            })

    def get_data(self):
        return self.sort_data


walker                  = ParseTreeWalker()
sort_walker             = SortWalker()
throwing_error_listener = ParserErrorListener('sort_by', 'Invalid sort_by syntax')


def create_sort_map(
        sort_by           : str,
        id_cols           : typing.Sequence[str],
        extra_sort_fields : typing.Sequence[str] = ()
) -> OrderedDict:
    sort_fields = OrderedDict()

    if sort_by:
        chars_sort = antlr4.InputStream(sort_by)

        lexer_sort = sortLexer(chars_sort)
        lexer_sort.removeErrorListeners()
        lexer_sort.addErrorListener(throwing_error_listener)
        lexer_sort._errHandler = BailErrorStrategy()

        tokens_sort = antlr4.CommonTokenStream(lexer_sort)

        parser_sort = sortParser(tokens_sort)
        parser_sort.removeErrorListeners()
        parser_sort.addErrorListener(throwing_error_listener)
        parser_sort._errHandler = BailErrorStrategy()

        tree_sort = parser_sort.sort()

        walker.walk(sort_walker, tree_sort)

        for elem in sort_walker.get_data():
            sort_fields[elem['expr']] = elem['order'].lower()

    # The primary key columns will be included in the sort if extra_sort_fields is empty
    extra_fields    = extra_sort_fields if extra_sort_fields else id_cols
    extra_direction = 'asc' if extra_sort_fields else 'desc'

    for col in extra_fields:
        if col not in sort_fields:
            sort_fields[col] = extra_direction

    return sort_fields
