# Generated from org/antlrQueryParser/sort.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .sortParser import sortParser
else:
    from sortParser import sortParser

# This class defines a complete listener for a parse tree produced by sortParser.
class sortListener(ParseTreeListener):

    # Enter a parse tree produced by sortParser#sort.
    def enterSort(self, ctx:sortParser.SortContext):
        pass

    # Exit a parse tree produced by sortParser#sort.
    def exitSort(self, ctx:sortParser.SortContext):
        pass


    # Enter a parse tree produced by sortParser#sort_expression.
    def enterSort_expression(self, ctx:sortParser.Sort_expressionContext):
        pass

    # Exit a parse tree produced by sortParser#sort_expression.
    def exitSort_expression(self, ctx:sortParser.Sort_expressionContext):
        pass


    # Enter a parse tree produced by sortParser#sort_set.
    def enterSort_set(self, ctx:sortParser.Sort_setContext):
        pass

    # Exit a parse tree produced by sortParser#sort_set.
    def exitSort_set(self, ctx:sortParser.Sort_setContext):
        pass


    # Enter a parse tree produced by sortParser#qualified_sort.
    def enterQualified_sort(self, ctx:sortParser.Qualified_sortContext):
        pass

    # Exit a parse tree produced by sortParser#qualified_sort.
    def exitQualified_sort(self, ctx:sortParser.Qualified_sortContext):
        pass


    # Enter a parse tree produced by sortParser#order.
    def enterOrder(self, ctx:sortParser.OrderContext):
        pass

    # Exit a parse tree produced by sortParser#order.
    def exitOrder(self, ctx:sortParser.OrderContext):
        pass


    # Enter a parse tree produced by sortParser#field.
    def enterField(self, ctx:sortParser.FieldContext):
        pass

    # Exit a parse tree produced by sortParser#field.
    def exitField(self, ctx:sortParser.FieldContext):
        pass


    # Enter a parse tree produced by sortParser#sep.
    def enterSep(self, ctx:sortParser.SepContext):
        pass

    # Exit a parse tree produced by sortParser#sep.
    def exitSep(self, ctx:sortParser.SepContext):
        pass


    # Enter a parse tree produced by sortParser#lparen.
    def enterLparen(self, ctx:sortParser.LparenContext):
        pass

    # Exit a parse tree produced by sortParser#lparen.
    def exitLparen(self, ctx:sortParser.LparenContext):
        pass


    # Enter a parse tree produced by sortParser#rparen.
    def enterRparen(self, ctx:sortParser.RparenContext):
        pass

    # Exit a parse tree produced by sortParser#rparen.
    def exitRparen(self, ctx:sortParser.RparenContext):
        pass


    # Enter a parse tree produced by sortParser#double_dot.
    def enterDouble_dot(self, ctx:sortParser.Double_dotContext):
        pass

    # Exit a parse tree produced by sortParser#double_dot.
    def exitDouble_dot(self, ctx:sortParser.Double_dotContext):
        pass



del sortParser