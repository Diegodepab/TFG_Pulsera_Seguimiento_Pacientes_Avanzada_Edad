grammar search;

query       : query_terms (SPACE* log_op SPACE* query_terms)* ;
query_terms : term | LPAREN query RPAREN ;
term        : term_name DOT com_op DOUBLE_DOT value ;

term_name   : (ALPHA|NUMBER)+;
value       : (NUMBER|STRING|special_op|(special_op (NUMBER|STRING))) ;

com_op      : 'eq'  | 'EQ'
            | 'gt'  | 'GT'
            | 'ge'  | 'GE'
            | 'lt'  | 'LT'
            | 'le'  | 'LE'
            | 'ne'  | 'NE'
            | 'in'  | 'IN'
            | 'nin'  | 'NIN'
            | 'beg' | 'BEG'
            | 'con' | 'CON'
            | 'end' | 'END';

log_op      : ('and' | 'AND' | 'or' | 'OR') (SPACE ('not'|'NOT'))? ;
special_op  : ('~')? ;

/* ================================================================
 * =                     LEXER                                    =
 * ================================================================
 */

ALPHA       : [a-zA-Z\-_]+  ;
STRING      : '\'' ('\\\'' | .)*? '\'' ;
NUMBER      : [0-9]+(DOT [0-9]+)* ;
DOT         : '.' ;
DOUBLE_DOT  : ':' ;

LPAREN      : '(' ;
RPAREN      : ')' ;

SPACE       : [ ]+ ;
WS          : [ \t\r\n]+ -> skip ; // skip spaces, tabs, newlines
