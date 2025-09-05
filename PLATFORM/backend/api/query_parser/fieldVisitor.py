# Generated from org/antlrQueryParser/field.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .fieldParser import fieldParser
else:
    from fieldParser import fieldParser

# This class defines a complete generic visitor for a parse tree produced by fieldParser.

class fieldVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by fieldParser#fields.
    def visitFields(self, ctx:fieldParser.FieldsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#fields_expression.
    def visitFields_expression(self, ctx:fieldParser.Fields_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#field_set.
    def visitField_set(self, ctx:fieldParser.Field_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#qualified_field.
    def visitQualified_field(self, ctx:fieldParser.Qualified_fieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#lparen.
    def visitLparen(self, ctx:fieldParser.LparenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#rparen.
    def visitRparen(self, ctx:fieldParser.RparenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#field.
    def visitField(self, ctx:fieldParser.FieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#negation.
    def visitNegation(self, ctx:fieldParser.NegationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by fieldParser#sep.
    def visitSep(self, ctx:fieldParser.SepContext):
        return self.visitChildren(ctx)



del fieldParser