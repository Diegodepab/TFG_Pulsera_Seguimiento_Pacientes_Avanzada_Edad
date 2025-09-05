# Generated from org/antlrQueryParser/sort.g4 by ANTLR 4.9.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\22")
        buf.write("?\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\4\n\t\n\4\13\t\13\3\2\3\2\3\3\3\3\3\3\3\3")
        buf.write("\3\3\5\3\36\n\3\3\4\3\4\3\4\3\4\3\4\5\4%\n\4\3\5\3\5\3")
        buf.write("\5\3\5\3\5\3\5\3\5\5\5.\n\5\3\6\3\6\3\7\3\7\3\7\5\7\65")
        buf.write("\n\7\3\b\3\b\3\t\3\t\3\n\3\n\3\13\3\13\3\13\2\2\f\2\4")
        buf.write("\6\b\n\f\16\20\22\24\2\3\3\2\3\6\28\2\26\3\2\2\2\4\35")
        buf.write("\3\2\2\2\6$\3\2\2\2\b-\3\2\2\2\n/\3\2\2\2\f\64\3\2\2\2")
        buf.write("\16\66\3\2\2\2\208\3\2\2\2\22:\3\2\2\2\24<\3\2\2\2\26")
        buf.write("\27\5\4\3\2\27\3\3\2\2\2\30\36\5\6\4\2\31\32\5\20\t\2")
        buf.write("\32\33\5\6\4\2\33\34\5\22\n\2\34\36\3\2\2\2\35\30\3\2")
        buf.write("\2\2\35\31\3\2\2\2\36\5\3\2\2\2\37%\5\b\5\2 !\5\b\5\2")
        buf.write("!\"\5\16\b\2\"#\5\6\4\2#%\3\2\2\2$\37\3\2\2\2$ \3\2\2")
        buf.write("\2%\7\3\2\2\2&\'\5\f\7\2\'(\5\24\13\2()\5\n\6\2).\3\2")
        buf.write("\2\2*+\5\f\7\2+,\5\4\3\2,.\3\2\2\2-&\3\2\2\2-*\3\2\2\2")
        buf.write(".\t\3\2\2\2/\60\t\2\2\2\60\13\3\2\2\2\61\65\7\7\2\2\62")
        buf.write("\63\7\7\2\2\63\65\5\f\7\2\64\61\3\2\2\2\64\62\3\2\2\2")
        buf.write("\65\r\3\2\2\2\66\67\7\20\2\2\67\17\3\2\2\289\7\b\2\29")
        buf.write("\21\3\2\2\2:;\7\t\2\2;\23\3\2\2\2<=\7\17\2\2=\25\3\2\2")
        buf.write("\2\6\35$-\64")
        return buf.getvalue()


class sortParser ( Parser ):

    grammarFileName = "sort.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'asc'", "'ASC'", "'desc'", "'DESC'", 
                     "<INVALID>", "'('", "')'", "'!'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'.'", "':'", "','" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "DASH_LETTER_DIGIT", "LPAREN", "RPAREN", 
                      "NEGATION", "DASH", "LETTER", "DIGIT", "DOT", "DOUBLE_DOT", 
                      "SEP", "SPACE", "WS" ]

    RULE_sort = 0
    RULE_sort_expression = 1
    RULE_sort_set = 2
    RULE_qualified_sort = 3
    RULE_order = 4
    RULE_field = 5
    RULE_sep = 6
    RULE_lparen = 7
    RULE_rparen = 8
    RULE_double_dot = 9

    ruleNames =  [ "sort", "sort_expression", "sort_set", "qualified_sort", 
                   "order", "field", "sep", "lparen", "rparen", "double_dot" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    DASH_LETTER_DIGIT=5
    LPAREN=6
    RPAREN=7
    NEGATION=8
    DASH=9
    LETTER=10
    DIGIT=11
    DOT=12
    DOUBLE_DOT=13
    SEP=14
    SPACE=15
    WS=16

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class SortContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def sort_expression(self):
            return self.getTypedRuleContext(sortParser.Sort_expressionContext,0)


        def getRuleIndex(self):
            return sortParser.RULE_sort

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSort" ):
                listener.enterSort(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSort" ):
                listener.exitSort(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSort" ):
                return visitor.visitSort(self)
            else:
                return visitor.visitChildren(self)




    def sort(self):

        localctx = sortParser.SortContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_sort)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.sort_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Sort_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def sort_set(self):
            return self.getTypedRuleContext(sortParser.Sort_setContext,0)


        def lparen(self):
            return self.getTypedRuleContext(sortParser.LparenContext,0)


        def rparen(self):
            return self.getTypedRuleContext(sortParser.RparenContext,0)


        def getRuleIndex(self):
            return sortParser.RULE_sort_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSort_expression" ):
                listener.enterSort_expression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSort_expression" ):
                listener.exitSort_expression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSort_expression" ):
                return visitor.visitSort_expression(self)
            else:
                return visitor.visitChildren(self)




    def sort_expression(self):

        localctx = sortParser.Sort_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_sort_expression)
        try:
            self.state = 27
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [sortParser.DASH_LETTER_DIGIT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 22
                self.sort_set()
                pass
            elif token in [sortParser.LPAREN]:
                self.enterOuterAlt(localctx, 2)
                self.state = 23
                self.lparen()
                self.state = 24
                self.sort_set()
                self.state = 25
                self.rparen()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Sort_setContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def qualified_sort(self):
            return self.getTypedRuleContext(sortParser.Qualified_sortContext,0)


        def sep(self):
            return self.getTypedRuleContext(sortParser.SepContext,0)


        def sort_set(self):
            return self.getTypedRuleContext(sortParser.Sort_setContext,0)


        def getRuleIndex(self):
            return sortParser.RULE_sort_set

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSort_set" ):
                listener.enterSort_set(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSort_set" ):
                listener.exitSort_set(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSort_set" ):
                return visitor.visitSort_set(self)
            else:
                return visitor.visitChildren(self)




    def sort_set(self):

        localctx = sortParser.Sort_setContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_sort_set)
        try:
            self.state = 34
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 29
                self.qualified_sort()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 30
                self.qualified_sort()
                self.state = 31
                self.sep()
                self.state = 32
                self.sort_set()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Qualified_sortContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field(self):
            return self.getTypedRuleContext(sortParser.FieldContext,0)


        def double_dot(self):
            return self.getTypedRuleContext(sortParser.Double_dotContext,0)


        def order(self):
            return self.getTypedRuleContext(sortParser.OrderContext,0)


        def sort_expression(self):
            return self.getTypedRuleContext(sortParser.Sort_expressionContext,0)


        def getRuleIndex(self):
            return sortParser.RULE_qualified_sort

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQualified_sort" ):
                listener.enterQualified_sort(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQualified_sort" ):
                listener.exitQualified_sort(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQualified_sort" ):
                return visitor.visitQualified_sort(self)
            else:
                return visitor.visitChildren(self)




    def qualified_sort(self):

        localctx = sortParser.Qualified_sortContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_qualified_sort)
        try:
            self.state = 43
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 36
                self.field()
                self.state = 37
                self.double_dot()
                self.state = 38
                self.order()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 40
                self.field()
                self.state = 41
                self.sort_expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OrderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return sortParser.RULE_order

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrder" ):
                listener.enterOrder(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrder" ):
                listener.exitOrder(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrder" ):
                return visitor.visitOrder(self)
            else:
                return visitor.visitChildren(self)




    def order(self):

        localctx = sortParser.OrderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_order)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << sortParser.T__0) | (1 << sortParser.T__1) | (1 << sortParser.T__2) | (1 << sortParser.T__3))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DASH_LETTER_DIGIT(self):
            return self.getToken(sortParser.DASH_LETTER_DIGIT, 0)

        def field(self):
            return self.getTypedRuleContext(sortParser.FieldContext,0)


        def getRuleIndex(self):
            return sortParser.RULE_field

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterField" ):
                listener.enterField(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitField" ):
                listener.exitField(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitField" ):
                return visitor.visitField(self)
            else:
                return visitor.visitChildren(self)




    def field(self):

        localctx = sortParser.FieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_field)
        try:
            self.state = 50
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 47
                self.match(sortParser.DASH_LETTER_DIGIT)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 48
                self.match(sortParser.DASH_LETTER_DIGIT)
                self.state = 49
                self.field()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SepContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SEP(self):
            return self.getToken(sortParser.SEP, 0)

        def getRuleIndex(self):
            return sortParser.RULE_sep

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSep" ):
                listener.enterSep(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSep" ):
                listener.exitSep(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSep" ):
                return visitor.visitSep(self)
            else:
                return visitor.visitChildren(self)




    def sep(self):

        localctx = sortParser.SepContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_sep)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self.match(sortParser.SEP)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LparenContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(sortParser.LPAREN, 0)

        def getRuleIndex(self):
            return sortParser.RULE_lparen

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLparen" ):
                listener.enterLparen(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLparen" ):
                listener.exitLparen(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLparen" ):
                return visitor.visitLparen(self)
            else:
                return visitor.visitChildren(self)




    def lparen(self):

        localctx = sortParser.LparenContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_lparen)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 54
            self.match(sortParser.LPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RparenContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RPAREN(self):
            return self.getToken(sortParser.RPAREN, 0)

        def getRuleIndex(self):
            return sortParser.RULE_rparen

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRparen" ):
                listener.enterRparen(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRparen" ):
                listener.exitRparen(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRparen" ):
                return visitor.visitRparen(self)
            else:
                return visitor.visitChildren(self)




    def rparen(self):

        localctx = sortParser.RparenContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_rparen)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 56
            self.match(sortParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Double_dotContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLE_DOT(self):
            return self.getToken(sortParser.DOUBLE_DOT, 0)

        def getRuleIndex(self):
            return sortParser.RULE_double_dot

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDouble_dot" ):
                listener.enterDouble_dot(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDouble_dot" ):
                listener.exitDouble_dot(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDouble_dot" ):
                return visitor.visitDouble_dot(self)
            else:
                return visitor.visitChildren(self)




    def double_dot(self):

        localctx = sortParser.Double_dotContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_double_dot)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 58
            self.match(sortParser.DOUBLE_DOT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





