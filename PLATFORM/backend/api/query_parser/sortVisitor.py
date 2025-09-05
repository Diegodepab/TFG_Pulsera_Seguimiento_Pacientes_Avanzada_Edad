# Generated from org/antlrQueryParser/sort.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .sortParser import sortParser
else:
    from sortParser import sortParser

# This class defines a complete generic visitor for a parse tree produced by sortParser.

class sortVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by sortParser#sort.
    def visitSort(self, ctx:sortParser.SortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#sort_expression.
    def visitSort_expression(self, ctx:sortParser.Sort_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#sort_set.
    def visitSort_set(self, ctx:sortParser.Sort_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#qualified_sort.
    def visitQualified_sort(self, ctx:sortParser.Qualified_sortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#order.
    def visitOrder(self, ctx:sortParser.OrderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#field.
    def visitField(self, ctx:sortParser.FieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#sep.
    def visitSep(self, ctx:sortParser.SepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#lparen.
    def visitLparen(self, ctx:sortParser.LparenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#rparen.
    def visitRparen(self, ctx:sortParser.RparenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by sortParser#double_dot.
    def visitDouble_dot(self, ctx:sortParser.Double_dotContext):
        return self.visitChildren(ctx)



del sortParser