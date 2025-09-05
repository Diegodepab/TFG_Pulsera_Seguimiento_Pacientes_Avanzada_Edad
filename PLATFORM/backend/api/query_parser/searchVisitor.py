# Generated from org/antlrQueryParser/search.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .searchParser import searchParser
else:
    from searchParser import searchParser

# This class defines a complete generic visitor for a parse tree produced by searchParser.

class searchVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by searchParser#query.
    def visitQuery(self, ctx:searchParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by searchParser#query_terms.
    def visitQuery_terms(self, ctx:searchParser.Query_termsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by searchParser#term.
    def visitTerm(self, ctx:searchParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by searchParser#term_name.
    def visitTerm_name(self, ctx:searchParser.Term_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by searchParser#value.
    def visitValue(self, ctx:searchParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by searchParser#com_op.
    def visitCom_op(self, ctx:searchParser.Com_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by searchParser#log_op.
    def visitLog_op(self, ctx:searchParser.Log_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by searchParser#special_op.
    def visitSpecial_op(self, ctx:searchParser.Special_opContext):
        return self.visitChildren(ctx)



del searchParser