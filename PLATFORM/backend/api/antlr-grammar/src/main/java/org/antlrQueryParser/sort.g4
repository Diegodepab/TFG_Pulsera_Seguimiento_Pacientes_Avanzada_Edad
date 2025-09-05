grammar sort;

sort              : sort_expression;
sort_expression   : sort_set | lparen sort_set rparen;
sort_set          : qualified_sort | qualified_sort sep sort_set;
qualified_sort    : field double_dot order | field sort_expression;
order             : 'asc'  | 'ASC'
                  | 'desc' | 'DESC';

field             : DASH_LETTER_DIGIT | DASH_LETTER_DIGIT field;
sep               : SEP;
lparen            : LPAREN;
rparen            : RPAREN;
double_dot        : DOUBLE_DOT;

/* ================================================================
 * =                     LEXER                                    =
 * ================================================================
 */

DASH_LETTER_DIGIT : DASH | LETTER | DIGIT | DOT;
LPAREN            : '(' ;
RPAREN            : ')' ;
NEGATION          : '!';
DASH              : '-' | '_';

LETTER            : [_A-Za-z] [_0-9A-Za-z]*  ;
DIGIT             : [0-9]+(DOT [0-9]+)*;
DOT               : '.' ;
DOUBLE_DOT        : ':' ;
SEP               : ',';

SPACE             : [ ]+ ;
WS : [ \t\n\r]+ -> skip;
