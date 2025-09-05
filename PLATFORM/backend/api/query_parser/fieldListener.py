# Generated from org/antlrQueryParser/field.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .fieldParser import fieldParser
else:
    from fieldParser import fieldParser

# This class defines a complete listener for a parse tree produced by fieldParser.
class fieldListener(ParseTreeListener):

    # Enter a parse tree produced by fieldParser#fields.
    def enterFields(self, ctx:fieldParser.FieldsContext):
        pass

    # Exit a parse tree produced by fieldParser#fields.
    def exitFields(self, ctx:fieldParser.FieldsContext):
        pass


    # Enter a parse tree produced by fieldParser#fields_expression.
    def enterFields_expression(self, ctx:fieldParser.Fields_expressionContext):
        pass

    # Exit a parse tree produced by fieldParser#fields_expression.
    def exitFields_expression(self, ctx:fieldParser.Fields_expressionContext):
        pass


    # Enter a parse tree produced by fieldParser#field_set.
    def enterField_set(self, ctx:fieldParser.Field_setContext):
        pass

    # Exit a parse tree produced by fieldParser#field_set.
    def exitField_set(self, ctx:fieldParser.Field_setContext):
        pass


    # Enter a parse tree produced by fieldParser#qualified_field.
    def enterQualified_field(self, ctx:fieldParser.Qualified_fieldContext):
        pass

    # Exit a parse tree produced by fieldParser#qualified_field.
    def exitQualified_field(self, ctx:fieldParser.Qualified_fieldContext):
        pass


    # Enter a parse tree produced by fieldParser#lparen.
    def enterLparen(self, ctx:fieldParser.LparenContext):
        pass

    # Exit a parse tree produced by fieldParser#lparen.
    def exitLparen(self, ctx:fieldParser.LparenContext):
        pass


    # Enter a parse tree produced by fieldParser#rparen.
    def enterRparen(self, ctx:fieldParser.RparenContext):
        pass

    # Exit a parse tree produced by fieldParser#rparen.
    def exitRparen(self, ctx:fieldParser.RparenContext):
        pass


    # Enter a parse tree produced by fieldParser#field.
    def enterField(self, ctx:fieldParser.FieldContext):
        pass

    # Exit a parse tree produced by fieldParser#field.
    def exitField(self, ctx:fieldParser.FieldContext):
        pass


    # Enter a parse tree produced by fieldParser#negation.
    def enterNegation(self, ctx:fieldParser.NegationContext):
        pass

    # Exit a parse tree produced by fieldParser#negation.
    def exitNegation(self, ctx:fieldParser.NegationContext):
        pass


    # Enter a parse tree produced by fieldParser#sep.
    def enterSep(self, ctx:fieldParser.SepContext):
        pass

    # Exit a parse tree produced by fieldParser#sep.
    def exitSep(self, ctx:fieldParser.SepContext):
        pass



del fieldParser