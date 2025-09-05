# Generated from org/antlrQueryParser/search.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .searchParser import searchParser
else:
    from searchParser import searchParser

# This class defines a complete listener for a parse tree produced by searchParser.
class searchListener(ParseTreeListener):

    # Enter a parse tree produced by searchParser#query.
    def enterQuery(self, ctx:searchParser.QueryContext):
        pass

    # Exit a parse tree produced by searchParser#query.
    def exitQuery(self, ctx:searchParser.QueryContext):
        pass


    # Enter a parse tree produced by searchParser#query_terms.
    def enterQuery_terms(self, ctx:searchParser.Query_termsContext):
        pass

    # Exit a parse tree produced by searchParser#query_terms.
    def exitQuery_terms(self, ctx:searchParser.Query_termsContext):
        pass


    # Enter a parse tree produced by searchParser#term.
    def enterTerm(self, ctx:searchParser.TermContext):
        pass

    # Exit a parse tree produced by searchParser#term.
    def exitTerm(self, ctx:searchParser.TermContext):
        pass


    # Enter a parse tree produced by searchParser#term_name.
    def enterTerm_name(self, ctx:searchParser.Term_nameContext):
        pass

    # Exit a parse tree produced by searchParser#term_name.
    def exitTerm_name(self, ctx:searchParser.Term_nameContext):
        pass


    # Enter a parse tree produced by searchParser#value.
    def enterValue(self, ctx:searchParser.ValueContext):
        pass

    # Exit a parse tree produced by searchParser#value.
    def exitValue(self, ctx:searchParser.ValueContext):
        pass


    # Enter a parse tree produced by searchParser#com_op.
    def enterCom_op(self, ctx:searchParser.Com_opContext):
        pass

    # Exit a parse tree produced by searchParser#com_op.
    def exitCom_op(self, ctx:searchParser.Com_opContext):
        pass


    # Enter a parse tree produced by searchParser#log_op.
    def enterLog_op(self, ctx:searchParser.Log_opContext):
        pass

    # Exit a parse tree produced by searchParser#log_op.
    def exitLog_op(self, ctx:searchParser.Log_opContext):
        pass


    # Enter a parse tree produced by searchParser#special_op.
    def enterSpecial_op(self, ctx:searchParser.Special_opContext):
        pass

    # Exit a parse tree produced by searchParser#special_op.
    def exitSpecial_op(self, ctx:searchParser.Special_opContext):
        pass



del searchParser