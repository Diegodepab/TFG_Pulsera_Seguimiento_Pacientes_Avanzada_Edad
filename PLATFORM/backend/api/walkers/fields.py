from __future__ import annotations

import antlr4
import json
import typing

from antlr4.error.ErrorStrategy import BailErrorStrategy
from antlr4.tree.Tree import ParseTreeWalker

from query_parser.fieldParser import fieldParser
from query_parser.fieldListener import fieldListener
from query_parser.fieldLexer import fieldLexer

from lib.exceptions import ParserErrorListener


class FieldWalker(fieldListener):
    def __init__(self):
        super().__init__()
        self.rewriter = ""

    def enterFields(self, ctx: fieldParser.FieldsContext):
        self.rewriter = "{"

    def exitQualified_field(self, ctx: fieldParser.Qualified_fieldContext):
        if '(' in ctx.getText():
            self.rewriter += "}"

    def enterQualified_field(self, ctx: fieldParser.Qualified_fieldContext):
        text = ctx.getText()

        if '(' in text:
            tmp_split      = text.split('(')
            self.rewriter += f'"{tmp_split[0]}":{{'
        else:
            self.rewriter += f'"{text}": true'

    def enterSep(self, ctx: fieldParser.SepContext):
        self.rewriter += ","

    def exitFields(self, ctx: fieldParser.FieldsContext):
        self.rewriter += "}"


walker                  = ParseTreeWalker()
field_walker            = FieldWalker()
throwing_error_listener = ParserErrorListener('fields OR embed', 'Invalid fields, or embed, syntax')
bail_error_strategy     = BailErrorStrategy()


def create_fields_object(txt) -> typing.Dict[str, typing.Union[bool, typing.Dict]]:
    chars_field = antlr4.InputStream(txt)

    lexer_field = fieldLexer(chars_field)
    lexer_field.removeErrorListeners()
    lexer_field.addErrorListener(throwing_error_listener)
    lexer_field._errHandler = bail_error_strategy

    tokens_field = antlr4.CommonTokenStream(lexer_field)

    parser_field = fieldParser(tokens_field)
    parser_field.removeErrorListeners()
    parser_field.addErrorListener(throwing_error_listener)
    parser_field._errHandler = bail_error_strategy

    tree_field = parser_field.fields()
    walker.walk(field_walker, tree_field)

    return json.loads(field_walker.rewriter)


# noinspection PyDefaultArgument
def create_embed_fields_maps(
        fields          : typing.Optional[str],
        embed           : typing.Optional[str],
        relation_fields : typing.Set[str] = ()
) -> typing.Dict:
    ret = {
        'fields' : {},
        'embed'  : {}
    }

    if fields:
        ret['fields'] = create_fields_object(fields)
        for field, value in ret['fields'].items():
            # empty fields to embed relation is converted to {} from True
            if field in relation_fields and value is True:
                ret['fields'][field] = {}

    # Embed is implemented in controllers
    if embed:
        ret['embed'] = create_fields_object(embed)

    return ret
