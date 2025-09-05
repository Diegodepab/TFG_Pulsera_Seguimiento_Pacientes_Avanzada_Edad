grammar field;

fields            : negation fields_expression | fields_expression ;
fields_expression : field_set | lparen field_set rparen ;
field_set         : qualified_field | qualified_field sep field_set ;
qualified_field   : field | field fields_expression ;
lparen            : LPAREN;
rparen            : RPAREN;
field             : DASH_LETTER_DIGIT | DASH_LETTER_DIGIT field ;
negation          : NEGATION ;
sep               : SEP ;

/* ================================================================
 * =                     LEXER                                    =
 * ================================================================
 */

DASH_LETTER_DIGIT : DASH | LETTER | DIGIT;
LPAREN            : '(' ;
RPAREN            : ')' ;
NEGATION          : '!' ;
DASH              : '-' | '_' ;

LETTER            : [_A-Za-z] [_0-9A-Za-z]*  ;
DIGIT             : [0-9]+(DOT [0-9]+)* ;
DOT               : '.' ;
SEP               : ',';

SPACE: [ ]+ ;
WS : [ \t\n\r]+ -> skip;
