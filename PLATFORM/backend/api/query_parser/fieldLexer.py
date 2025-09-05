# Generated from org/antlrQueryParser/field.g4 by ANTLR 4.9.1
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\r")
        buf.write("M\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\3\2\3\2\3\2")
        buf.write("\5\2\35\n\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7\7")
        buf.write("\7)\n\7\f\7\16\7,\13\7\3\b\6\b/\n\b\r\b\16\b\60\3\b\3")
        buf.write("\b\6\b\65\n\b\r\b\16\b\66\7\b9\n\b\f\b\16\b<\13\b\3\t")
        buf.write("\3\t\3\n\3\n\3\13\6\13C\n\13\r\13\16\13D\3\f\6\fH\n\f")
        buf.write("\r\f\16\fI\3\f\3\f\2\2\r\3\3\5\4\7\5\t\6\13\7\r\b\17\t")
        buf.write("\21\n\23\13\25\f\27\r\3\2\b\4\2//aa\5\2C\\aac|\6\2\62")
        buf.write(";C\\aac|\3\2\62;\3\2\"\"\5\2\13\f\17\17\"\"\2T\2\3\3\2")
        buf.write("\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2")
        buf.write("\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2")
        buf.write("\25\3\2\2\2\2\27\3\2\2\2\3\34\3\2\2\2\5\36\3\2\2\2\7 ")
        buf.write("\3\2\2\2\t\"\3\2\2\2\13$\3\2\2\2\r&\3\2\2\2\17.\3\2\2")
        buf.write("\2\21=\3\2\2\2\23?\3\2\2\2\25B\3\2\2\2\27G\3\2\2\2\31")
        buf.write("\35\5\13\6\2\32\35\5\r\7\2\33\35\5\17\b\2\34\31\3\2\2")
        buf.write("\2\34\32\3\2\2\2\34\33\3\2\2\2\35\4\3\2\2\2\36\37\7*\2")
        buf.write("\2\37\6\3\2\2\2 !\7+\2\2!\b\3\2\2\2\"#\7#\2\2#\n\3\2\2")
        buf.write("\2$%\t\2\2\2%\f\3\2\2\2&*\t\3\2\2\')\t\4\2\2(\'\3\2\2")
        buf.write("\2),\3\2\2\2*(\3\2\2\2*+\3\2\2\2+\16\3\2\2\2,*\3\2\2\2")
        buf.write("-/\t\5\2\2.-\3\2\2\2/\60\3\2\2\2\60.\3\2\2\2\60\61\3\2")
        buf.write("\2\2\61:\3\2\2\2\62\64\5\21\t\2\63\65\t\5\2\2\64\63\3")
        buf.write("\2\2\2\65\66\3\2\2\2\66\64\3\2\2\2\66\67\3\2\2\2\679\3")
        buf.write("\2\2\28\62\3\2\2\29<\3\2\2\2:8\3\2\2\2:;\3\2\2\2;\20\3")
        buf.write("\2\2\2<:\3\2\2\2=>\7\60\2\2>\22\3\2\2\2?@\7.\2\2@\24\3")
        buf.write("\2\2\2AC\t\6\2\2BA\3\2\2\2CD\3\2\2\2DB\3\2\2\2DE\3\2\2")
        buf.write("\2E\26\3\2\2\2FH\t\7\2\2GF\3\2\2\2HI\3\2\2\2IG\3\2\2\2")
        buf.write("IJ\3\2\2\2JK\3\2\2\2KL\b\f\2\2L\30\3\2\2\2\n\2\34*\60")
        buf.write("\66:DI\3\b\2\2")
        return buf.getvalue()


class fieldLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    DASH_LETTER_DIGIT = 1
    LPAREN = 2
    RPAREN = 3
    NEGATION = 4
    DASH = 5
    LETTER = 6
    DIGIT = 7
    DOT = 8
    SEP = 9
    SPACE = 10
    WS = 11

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'('", "')'", "'!'", "'.'", "','" ]

    symbolicNames = [ "<INVALID>",
            "DASH_LETTER_DIGIT", "LPAREN", "RPAREN", "NEGATION", "DASH", 
            "LETTER", "DIGIT", "DOT", "SEP", "SPACE", "WS" ]

    ruleNames = [ "DASH_LETTER_DIGIT", "LPAREN", "RPAREN", "NEGATION", "DASH", 
                  "LETTER", "DIGIT", "DOT", "SEP", "SPACE", "WS" ]

    grammarFileName = "field.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


