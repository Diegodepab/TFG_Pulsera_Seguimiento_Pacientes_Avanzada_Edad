# Generated from org/antlrQueryParser/field.g4 by ANTLR 4.9.1
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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\r")
        buf.write("<\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\4\n\t\n\3\2\3\2\3\2\3\2\5\2\31\n\2\3\3\3")
        buf.write("\3\3\3\3\3\3\3\5\3 \n\3\3\4\3\4\3\4\3\4\3\4\5\4\'\n\4")
        buf.write("\3\5\3\5\3\5\3\5\5\5-\n\5\3\6\3\6\3\7\3\7\3\b\3\b\3\b")
        buf.write("\5\b\66\n\b\3\t\3\t\3\n\3\n\3\n\2\2\13\2\4\6\b\n\f\16")
        buf.write("\20\22\2\2\2\67\2\30\3\2\2\2\4\37\3\2\2\2\6&\3\2\2\2\b")
        buf.write(",\3\2\2\2\n.\3\2\2\2\f\60\3\2\2\2\16\65\3\2\2\2\20\67")
        buf.write("\3\2\2\2\229\3\2\2\2\24\25\5\20\t\2\25\26\5\4\3\2\26\31")
        buf.write("\3\2\2\2\27\31\5\4\3\2\30\24\3\2\2\2\30\27\3\2\2\2\31")
        buf.write("\3\3\2\2\2\32 \5\6\4\2\33\34\5\n\6\2\34\35\5\6\4\2\35")
        buf.write("\36\5\f\7\2\36 \3\2\2\2\37\32\3\2\2\2\37\33\3\2\2\2 \5")
        buf.write("\3\2\2\2!\'\5\b\5\2\"#\5\b\5\2#$\5\22\n\2$%\5\6\4\2%\'")
        buf.write("\3\2\2\2&!\3\2\2\2&\"\3\2\2\2\'\7\3\2\2\2(-\5\16\b\2)")
        buf.write("*\5\16\b\2*+\5\4\3\2+-\3\2\2\2,(\3\2\2\2,)\3\2\2\2-\t")
        buf.write("\3\2\2\2./\7\4\2\2/\13\3\2\2\2\60\61\7\5\2\2\61\r\3\2")
        buf.write("\2\2\62\66\7\3\2\2\63\64\7\3\2\2\64\66\5\16\b\2\65\62")
        buf.write("\3\2\2\2\65\63\3\2\2\2\66\17\3\2\2\2\678\7\6\2\28\21\3")
        buf.write("\2\2\29:\7\13\2\2:\23\3\2\2\2\7\30\37&,\65")
        return buf.getvalue()


class fieldParser ( Parser ):

    grammarFileName = "field.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "'('", "')'", "'!'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'.'", "','" ]

    symbolicNames = [ "<INVALID>", "DASH_LETTER_DIGIT", "LPAREN", "RPAREN", 
                      "NEGATION", "DASH", "LETTER", "DIGIT", "DOT", "SEP", 
                      "SPACE", "WS" ]

    RULE_fields = 0
    RULE_fields_expression = 1
    RULE_field_set = 2
    RULE_qualified_field = 3
    RULE_lparen = 4
    RULE_rparen = 5
    RULE_field = 6
    RULE_negation = 7
    RULE_sep = 8

    ruleNames =  [ "fields", "fields_expression", "field_set", "qualified_field", 
                   "lparen", "rparen", "field", "negation", "sep" ]

    EOF = Token.EOF
    DASH_LETTER_DIGIT=1
    LPAREN=2
    RPAREN=3
    NEGATION=4
    DASH=5
    LETTER=6
    DIGIT=7
    DOT=8
    SEP=9
    SPACE=10
    WS=11

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class FieldsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def negation(self):
            return self.getTypedRuleContext(fieldParser.NegationContext,0)


        def fields_expression(self):
            return self.getTypedRuleContext(fieldParser.Fields_expressionContext,0)


        def getRuleIndex(self):
            return fieldParser.RULE_fields

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFields" ):
                listener.enterFields(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFields" ):
                listener.exitFields(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFields" ):
                return visitor.visitFields(self)
            else:
                return visitor.visitChildren(self)




    def fields(self):

        localctx = fieldParser.FieldsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_fields)
        try:
            self.state = 22
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [fieldParser.NEGATION]:
                self.enterOuterAlt(localctx, 1)
                self.state = 18
                self.negation()
                self.state = 19
                self.fields_expression()
                pass
            elif token in [fieldParser.DASH_LETTER_DIGIT, fieldParser.LPAREN]:
                self.enterOuterAlt(localctx, 2)
                self.state = 21
                self.fields_expression()
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


    class Fields_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field_set(self):
            return self.getTypedRuleContext(fieldParser.Field_setContext,0)


        def lparen(self):
            return self.getTypedRuleContext(fieldParser.LparenContext,0)


        def rparen(self):
            return self.getTypedRuleContext(fieldParser.RparenContext,0)


        def getRuleIndex(self):
            return fieldParser.RULE_fields_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFields_expression" ):
                listener.enterFields_expression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFields_expression" ):
                listener.exitFields_expression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFields_expression" ):
                return visitor.visitFields_expression(self)
            else:
                return visitor.visitChildren(self)




    def fields_expression(self):

        localctx = fieldParser.Fields_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_fields_expression)
        try:
            self.state = 29
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [fieldParser.DASH_LETTER_DIGIT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 24
                self.field_set()
                pass
            elif token in [fieldParser.LPAREN]:
                self.enterOuterAlt(localctx, 2)
                self.state = 25
                self.lparen()
                self.state = 26
                self.field_set()
                self.state = 27
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


    class Field_setContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def qualified_field(self):
            return self.getTypedRuleContext(fieldParser.Qualified_fieldContext,0)


        def sep(self):
            return self.getTypedRuleContext(fieldParser.SepContext,0)


        def field_set(self):
            return self.getTypedRuleContext(fieldParser.Field_setContext,0)


        def getRuleIndex(self):
            return fieldParser.RULE_field_set

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterField_set" ):
                listener.enterField_set(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitField_set" ):
                listener.exitField_set(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitField_set" ):
                return visitor.visitField_set(self)
            else:
                return visitor.visitChildren(self)




    def field_set(self):

        localctx = fieldParser.Field_setContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_field_set)
        try:
            self.state = 36
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 31
                self.qualified_field()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 32
                self.qualified_field()
                self.state = 33
                self.sep()
                self.state = 34
                self.field_set()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Qualified_fieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field(self):
            return self.getTypedRuleContext(fieldParser.FieldContext,0)


        def fields_expression(self):
            return self.getTypedRuleContext(fieldParser.Fields_expressionContext,0)


        def getRuleIndex(self):
            return fieldParser.RULE_qualified_field

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQualified_field" ):
                listener.enterQualified_field(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQualified_field" ):
                listener.exitQualified_field(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQualified_field" ):
                return visitor.visitQualified_field(self)
            else:
                return visitor.visitChildren(self)




    def qualified_field(self):

        localctx = fieldParser.Qualified_fieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_qualified_field)
        try:
            self.state = 42
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 38
                self.field()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 39
                self.field()
                self.state = 40
                self.fields_expression()
                pass


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
            return self.getToken(fieldParser.LPAREN, 0)

        def getRuleIndex(self):
            return fieldParser.RULE_lparen

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

        localctx = fieldParser.LparenContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_lparen)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.match(fieldParser.LPAREN)
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
            return self.getToken(fieldParser.RPAREN, 0)

        def getRuleIndex(self):
            return fieldParser.RULE_rparen

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

        localctx = fieldParser.RparenContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_rparen)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            self.match(fieldParser.RPAREN)
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
            return self.getToken(fieldParser.DASH_LETTER_DIGIT, 0)

        def field(self):
            return self.getTypedRuleContext(fieldParser.FieldContext,0)


        def getRuleIndex(self):
            return fieldParser.RULE_field

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

        localctx = fieldParser.FieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_field)
        try:
            self.state = 51
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 48
                self.match(fieldParser.DASH_LETTER_DIGIT)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 49
                self.match(fieldParser.DASH_LETTER_DIGIT)
                self.state = 50
                self.field()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NegationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEGATION(self):
            return self.getToken(fieldParser.NEGATION, 0)

        def getRuleIndex(self):
            return fieldParser.RULE_negation

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNegation" ):
                listener.enterNegation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNegation" ):
                listener.exitNegation(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNegation" ):
                return visitor.visitNegation(self)
            else:
                return visitor.visitChildren(self)




    def negation(self):

        localctx = fieldParser.NegationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_negation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.match(fieldParser.NEGATION)
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
            return self.getToken(fieldParser.SEP, 0)

        def getRuleIndex(self):
            return fieldParser.RULE_sep

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

        localctx = fieldParser.SepContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_sep)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self.match(fieldParser.SEP)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





