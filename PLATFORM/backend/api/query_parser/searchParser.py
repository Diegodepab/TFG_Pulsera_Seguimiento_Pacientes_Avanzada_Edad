# Generated from org/antlrQueryParser/search.g4 by ANTLR 4.9.1
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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3(")
        buf.write("L\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\3\2\3\2\7\2\25\n\2\f\2\16\2\30\13\2\3\2\3")
        buf.write("\2\7\2\34\n\2\f\2\16\2\37\13\2\3\2\3\2\7\2#\n\2\f\2\16")
        buf.write("\2&\13\2\3\3\3\3\3\3\3\3\3\3\5\3-\n\3\3\4\3\4\3\4\3\4")
        buf.write("\3\4\3\4\3\5\6\5\66\n\5\r\5\16\5\67\3\6\3\6\3\6\3\6\3")
        buf.write("\6\3\6\5\6@\n\6\3\7\3\7\3\b\3\b\3\b\5\bG\n\b\3\t\5\tJ")
        buf.write("\n\t\3\t\2\2\n\2\4\6\b\n\f\16\20\2\7\4\2  \"\"\3\2!\"")
        buf.write("\3\2\3\30\3\2\31\34\3\2\35\36\2M\2\22\3\2\2\2\4,\3\2\2")
        buf.write("\2\6.\3\2\2\2\b\65\3\2\2\2\n?\3\2\2\2\fA\3\2\2\2\16C\3")
        buf.write("\2\2\2\20I\3\2\2\2\22$\5\4\3\2\23\25\7\'\2\2\24\23\3\2")
        buf.write("\2\2\25\30\3\2\2\2\26\24\3\2\2\2\26\27\3\2\2\2\27\31\3")
        buf.write("\2\2\2\30\26\3\2\2\2\31\35\5\16\b\2\32\34\7\'\2\2\33\32")
        buf.write("\3\2\2\2\34\37\3\2\2\2\35\33\3\2\2\2\35\36\3\2\2\2\36")
        buf.write(" \3\2\2\2\37\35\3\2\2\2 !\5\4\3\2!#\3\2\2\2\"\26\3\2\2")
        buf.write("\2#&\3\2\2\2$\"\3\2\2\2$%\3\2\2\2%\3\3\2\2\2&$\3\2\2\2")
        buf.write("\'-\5\6\4\2()\7%\2\2)*\5\2\2\2*+\7&\2\2+-\3\2\2\2,\'\3")
        buf.write("\2\2\2,(\3\2\2\2-\5\3\2\2\2./\5\b\5\2/\60\7#\2\2\60\61")
        buf.write("\5\f\7\2\61\62\7$\2\2\62\63\5\n\6\2\63\7\3\2\2\2\64\66")
        buf.write("\t\2\2\2\65\64\3\2\2\2\66\67\3\2\2\2\67\65\3\2\2\2\67")
        buf.write("8\3\2\2\28\t\3\2\2\29@\7\"\2\2:@\7!\2\2;@\5\20\t\2<=\5")
        buf.write("\20\t\2=>\t\3\2\2>@\3\2\2\2?9\3\2\2\2?:\3\2\2\2?;\3\2")
        buf.write("\2\2?<\3\2\2\2@\13\3\2\2\2AB\t\4\2\2B\r\3\2\2\2CF\t\5")
        buf.write("\2\2DE\7\'\2\2EG\t\6\2\2FD\3\2\2\2FG\3\2\2\2G\17\3\2\2")
        buf.write("\2HJ\7\37\2\2IH\3\2\2\2IJ\3\2\2\2J\21\3\2\2\2\n\26\35")
        buf.write("$,\67?FI")
        return buf.getvalue()


class searchParser ( Parser ):

    grammarFileName = "search.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'eq'", "'EQ'", "'gt'", "'GT'", "'ge'", 
                     "'GE'", "'lt'", "'LT'", "'le'", "'LE'", "'ne'", "'NE'", 
                     "'in'", "'IN'", "'nin'", "'NIN'", "'beg'", "'BEG'", 
                     "'con'", "'CON'", "'end'", "'END'", "'and'", "'AND'", 
                     "'or'", "'OR'", "'not'", "'NOT'", "'~'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'.'", "':'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "ALPHA", "STRING", "NUMBER", 
                      "DOT", "DOUBLE_DOT", "LPAREN", "RPAREN", "SPACE", 
                      "WS" ]

    RULE_query = 0
    RULE_query_terms = 1
    RULE_term = 2
    RULE_term_name = 3
    RULE_value = 4
    RULE_com_op = 5
    RULE_log_op = 6
    RULE_special_op = 7

    ruleNames =  [ "query", "query_terms", "term", "term_name", "value", 
                   "com_op", "log_op", "special_op" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    ALPHA=30
    STRING=31
    NUMBER=32
    DOT=33
    DOUBLE_DOT=34
    LPAREN=35
    RPAREN=36
    SPACE=37
    WS=38

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def query_terms(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(searchParser.Query_termsContext)
            else:
                return self.getTypedRuleContext(searchParser.Query_termsContext,i)


        def log_op(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(searchParser.Log_opContext)
            else:
                return self.getTypedRuleContext(searchParser.Log_opContext,i)


        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(searchParser.SPACE)
            else:
                return self.getToken(searchParser.SPACE, i)

        def getRuleIndex(self):
            return searchParser.RULE_query

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuery" ):
                listener.enterQuery(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuery" ):
                listener.exitQuery(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuery" ):
                return visitor.visitQuery(self)
            else:
                return visitor.visitChildren(self)




    def query(self):

        localctx = searchParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_query)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.query_terms()
            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << searchParser.T__22) | (1 << searchParser.T__23) | (1 << searchParser.T__24) | (1 << searchParser.T__25) | (1 << searchParser.SPACE))) != 0):
                self.state = 20
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==searchParser.SPACE:
                    self.state = 17
                    self.match(searchParser.SPACE)
                    self.state = 22
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 23
                self.log_op()
                self.state = 27
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==searchParser.SPACE:
                    self.state = 24
                    self.match(searchParser.SPACE)
                    self.state = 29
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 30
                self.query_terms()
                self.state = 36
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Query_termsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def term(self):
            return self.getTypedRuleContext(searchParser.TermContext,0)


        def LPAREN(self):
            return self.getToken(searchParser.LPAREN, 0)

        def query(self):
            return self.getTypedRuleContext(searchParser.QueryContext,0)


        def RPAREN(self):
            return self.getToken(searchParser.RPAREN, 0)

        def getRuleIndex(self):
            return searchParser.RULE_query_terms

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuery_terms" ):
                listener.enterQuery_terms(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuery_terms" ):
                listener.exitQuery_terms(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuery_terms" ):
                return visitor.visitQuery_terms(self)
            else:
                return visitor.visitChildren(self)




    def query_terms(self):

        localctx = searchParser.Query_termsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_query_terms)
        try:
            self.state = 42
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [searchParser.ALPHA, searchParser.NUMBER]:
                self.enterOuterAlt(localctx, 1)
                self.state = 37
                self.term()
                pass
            elif token in [searchParser.LPAREN]:
                self.enterOuterAlt(localctx, 2)
                self.state = 38
                self.match(searchParser.LPAREN)
                self.state = 39
                self.query()
                self.state = 40
                self.match(searchParser.RPAREN)
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


    class TermContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def term_name(self):
            return self.getTypedRuleContext(searchParser.Term_nameContext,0)


        def DOT(self):
            return self.getToken(searchParser.DOT, 0)

        def com_op(self):
            return self.getTypedRuleContext(searchParser.Com_opContext,0)


        def DOUBLE_DOT(self):
            return self.getToken(searchParser.DOUBLE_DOT, 0)

        def value(self):
            return self.getTypedRuleContext(searchParser.ValueContext,0)


        def getRuleIndex(self):
            return searchParser.RULE_term

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTerm" ):
                listener.enterTerm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTerm" ):
                listener.exitTerm(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTerm" ):
                return visitor.visitTerm(self)
            else:
                return visitor.visitChildren(self)




    def term(self):

        localctx = searchParser.TermContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_term)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.term_name()
            self.state = 45
            self.match(searchParser.DOT)
            self.state = 46
            self.com_op()
            self.state = 47
            self.match(searchParser.DOUBLE_DOT)
            self.state = 48
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Term_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALPHA(self, i:int=None):
            if i is None:
                return self.getTokens(searchParser.ALPHA)
            else:
                return self.getToken(searchParser.ALPHA, i)

        def NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(searchParser.NUMBER)
            else:
                return self.getToken(searchParser.NUMBER, i)

        def getRuleIndex(self):
            return searchParser.RULE_term_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTerm_name" ):
                listener.enterTerm_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTerm_name" ):
                listener.exitTerm_name(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTerm_name" ):
                return visitor.visitTerm_name(self)
            else:
                return visitor.visitChildren(self)




    def term_name(self):

        localctx = searchParser.Term_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_term_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 50
                _la = self._input.LA(1)
                if not(_la==searchParser.ALPHA or _la==searchParser.NUMBER):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 53 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==searchParser.ALPHA or _la==searchParser.NUMBER):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(searchParser.NUMBER, 0)

        def STRING(self):
            return self.getToken(searchParser.STRING, 0)

        def special_op(self):
            return self.getTypedRuleContext(searchParser.Special_opContext,0)


        def getRuleIndex(self):
            return searchParser.RULE_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue" ):
                listener.enterValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue" ):
                listener.exitValue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValue" ):
                return visitor.visitValue(self)
            else:
                return visitor.visitChildren(self)




    def value(self):

        localctx = searchParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_value)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.state = 55
                self.match(searchParser.NUMBER)
                pass

            elif la_ == 2:
                self.state = 56
                self.match(searchParser.STRING)
                pass

            elif la_ == 3:
                self.state = 57
                self.special_op()
                pass

            elif la_ == 4:
                self.state = 58
                self.special_op()
                self.state = 59
                _la = self._input.LA(1)
                if not(_la==searchParser.STRING or _la==searchParser.NUMBER):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Com_opContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return searchParser.RULE_com_op

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCom_op" ):
                listener.enterCom_op(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCom_op" ):
                listener.exitCom_op(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCom_op" ):
                return visitor.visitCom_op(self)
            else:
                return visitor.visitChildren(self)




    def com_op(self):

        localctx = searchParser.Com_opContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_com_op)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << searchParser.T__0) | (1 << searchParser.T__1) | (1 << searchParser.T__2) | (1 << searchParser.T__3) | (1 << searchParser.T__4) | (1 << searchParser.T__5) | (1 << searchParser.T__6) | (1 << searchParser.T__7) | (1 << searchParser.T__8) | (1 << searchParser.T__9) | (1 << searchParser.T__10) | (1 << searchParser.T__11) | (1 << searchParser.T__12) | (1 << searchParser.T__13) | (1 << searchParser.T__14) | (1 << searchParser.T__15) | (1 << searchParser.T__16) | (1 << searchParser.T__17) | (1 << searchParser.T__18) | (1 << searchParser.T__19) | (1 << searchParser.T__20) | (1 << searchParser.T__21))) != 0)):
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


    class Log_opContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SPACE(self):
            return self.getToken(searchParser.SPACE, 0)

        def getRuleIndex(self):
            return searchParser.RULE_log_op

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLog_op" ):
                listener.enterLog_op(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLog_op" ):
                listener.exitLog_op(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLog_op" ):
                return visitor.visitLog_op(self)
            else:
                return visitor.visitChildren(self)




    def log_op(self):

        localctx = searchParser.Log_opContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_log_op)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << searchParser.T__22) | (1 << searchParser.T__23) | (1 << searchParser.T__24) | (1 << searchParser.T__25))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 68
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.state = 66
                self.match(searchParser.SPACE)
                self.state = 67
                _la = self._input.LA(1)
                if not(_la==searchParser.T__26 or _la==searchParser.T__27):
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


    class Special_opContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return searchParser.RULE_special_op

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSpecial_op" ):
                listener.enterSpecial_op(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSpecial_op" ):
                listener.exitSpecial_op(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpecial_op" ):
                return visitor.visitSpecial_op(self)
            else:
                return visitor.visitChildren(self)




    def special_op(self):

        localctx = searchParser.Special_opContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_special_op)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==searchParser.T__28:
                self.state = 70
                self.match(searchParser.T__28)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





