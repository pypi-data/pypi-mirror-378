/** Token type definitions. REMINDER: NEITHER of the token constant values given by
 *  "pycore_token.h" nor "token.py" keep consistent acrosss python versions. The int value which represents certain 
 *  token type DOES NOT necessarily mean it represents the same type in other 
 *  python versions.
 * 
 *  This header unifies the token type values to those of python 3.14.
 */

#ifndef _TOKEN_H
#define _TOKEN_H


#undef TILDE   /* Prevent clash of our definition with system macro. Ex AIX, ioctl.h */

#define ENDMARKER       0
#define NAME            1
#define NUMBER          2
#define STRING          3
#define NEWLINE         4
#define INDENT          5
#define DEDENT          6

#define LPAR            7
#define RPAR            8
#define LSQB            9
#define RSQB            10
#define COLON           11
#define COMMA           12
#define SEMI            13
#define PLUS            14
#define MINUS           15
#define STAR            16
#define SLASH           17
#define VBAR            18
#define AMPER           19
#define LESS            20
#define GREATER         21
#define EQUAL           22
#define DOT             23
#define PERCENT         24
#define LBRACE          25
#define RBRACE          26
#define EQEQUAL         27
#define NOTEQUAL        28
#define LESSEQUAL       29
#define GREATEREQUAL    30
#define TILDE           31
#define CIRCUMFLEX      32
#define LEFTSHIFT       33
#define RIGHTSHIFT      34
#define DOUBLESTAR      35
#define PLUSEQUAL       36
#define MINEQUAL        37
#define STAREQUAL       38
#define SLASHEQUAL      39
#define PERCENTEQUAL    40
#define AMPEREQUAL      41
#define VBAREQUAL       42
#define CIRCUMFLEXEQUAL 43
#define LEFTSHIFTEQUAL  44
#define RIGHTSHIFTEQUAL 45
#define DOUBLESTAREQUAL 46
#define DOUBLESLASH     47
#define DOUBLESLASHEQUAL 48
#define AT              49
#define ATEQUAL         50
#define RARROW          51
#define ELLIPSIS        52
#define COLONEQUAL      53
#define EXCLAMATION     54
#define OP              55

#define TYPE_IGNORE     56
#define TYPE_COMMENT    57
#define SOFT_KEYWORD    58
#define FSTRING_START   59
#define FSTRING_MIDDLE  60
#define FSTRING_END     61
#define TSTRING_START   62
#define TSTRING_MIDDLE  63
#define TSTRING_END     64
#define COMMENT         65
#define NL              66
#define ERRORTOKEN      67
#define ENCODING        68  // this is addtional for pyi
#define N_TOKENS        69
#define NT_OFFSET       256

/* Special definitions for cooperation with parser */

#define ISTERMINAL(x)           ((x) < NT_OFFSET)
#define ISNONTERMINAL(x)        ((x) >= NT_OFFSET)
#define ISEOF(x)                ((x) == ENDMARKER)
#define ISWHITESPACE(x)         ((x) == ENDMARKER || \
                                 (x) == NEWLINE   || \
                                 (x) == INDENT    || \
                                 (x) == DEDENT)
#define ISSTRINGLIT(x)          ((x) == STRING           || \
                                 (x) == FSTRING_MIDDLE   || \
                                 (x) == TSTRING_MIDDLE)

#endif  // !_TOKEN_H
