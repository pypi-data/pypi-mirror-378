""" Interfaces of module `std_base_toknzer`. 

These methods are strictly compatible with builtin `tokenize` module.
"""
__all__ = [
    'tokenize',
]


# imports
from tokenize import detect_encoding, TokenError, TokenInfo as BuiltinTokenInfo
import itertools
from typing import Generator

# local imports; pylint: disable=import-error,no-name-in-module
from std_base_toknzer._tokenize import TokenizerIter


# token type definitions; these are the same as python 3.14
ENDMARKER = 0
NAME = 1
NUMBER = 2
STRING = 3
NEWLINE = 4
INDENT = 5
DEDENT = 6
LPAR = 7
RPAR = 8
LSQB = 9
RSQB = 10
COLON = 11
COMMA = 12
SEMI = 13
PLUS = 14
MINUS = 15
STAR = 16
SLASH = 17
VBAR = 18
AMPER = 19
LESS = 20
GREATER = 21
EQUAL = 22
DOT = 23
PERCENT = 24
LBRACE = 25
RBRACE = 26
EQEQUAL = 27
NOTEQUAL = 28
LESSEQUAL = 29
GREATEREQUAL = 30
TILDE = 31
CIRCUMFLEX = 32
LEFTSHIFT = 33
RIGHTSHIFT = 34
DOUBLESTAR = 35
PLUSEQUAL = 36
MINEQUAL = 37
STAREQUAL = 38
SLASHEQUAL = 39
PERCENTEQUAL = 40
AMPEREQUAL = 41
VBAREQUAL = 42
CIRCUMFLEXEQUAL = 43
LEFTSHIFTEQUAL = 44
RIGHTSHIFTEQUAL = 45
DOUBLESTAREQUAL = 46
DOUBLESLASH = 47
DOUBLESLASHEQUAL = 48
AT = 49
ATEQUAL = 50
RARROW = 51
ELLIPSIS = 52
COLONEQUAL = 53
EXCLAMATION = 54
OP = 55
TYPE_IGNORE = 56
TYPE_COMMENT = 57
SOFT_KEYWORD = 58
FSTRING_START = 59
FSTRING_MIDDLE = 60
FSTRING_END = 61
TSTRING_START = 62
TSTRING_MIDDLE = 63
TSTRING_END = 64
COMMENT = 65
NL = 66
# These aren't used by the C tokenizer but are needed for tokenize.py
ERRORTOKEN = 67
ENCODING = 68
N_TOKENS = 69
# Special definitions for cooperation with parser
NT_OFFSET = 256


def tokenize(readline) -> Generator[BuiltinTokenInfo, None, None]:
    """
    The tokenize() generator requires one argument, readline, which
    must be a callable object which provides the same interface as the
    readline() method of built-in file objects.  Each call to the function
    should return one line of input as bytes.  Alternatively, readline
    can be a callable function terminating with StopIteration:
        readline = open(myfile, 'rb').__next__  # Example of alternate readline

    The generator produces 5-tuples with these members: the token type; the
    token string; a 2-tuple (srow, scol) of ints specifying the row and
    column where the token begins in the source; a 2-tuple (erow, ecol) of
    ints specifying the row and column where the token ends in the source;
    and the line on which the token was found.  The line passed is the
    physical line.

    The first token sequence will always be an ENCODING token
    which tells you which encoding was used to decode the bytes stream.
    """
    encoding, consumed = detect_encoding(readline)
    rl_gen = itertools.chain(consumed, iter(readline, b""))
    if encoding is not None:
        if encoding == "utf-8-sig":
            # BOM will already have been stripped.
            encoding = "utf-8"
        yield BuiltinTokenInfo(ENCODING, encoding, (0, 0), (0, 0), '')
    yield from _generate_tokens_from_c_tokenizer(rl_gen.__next__, encoding, extra_tokens=True)


def generate_tokens(readline):
    """Tokenize a source reading Python code as unicode strings.

    This has the same API as tokenize(), except that it expects the *readline*
    callable to return str objects instead of bytes.
    """
    return _generate_tokens_from_c_tokenizer(readline, extra_tokens=True)


def _transform_msg(msg):
    """Transform error messages from the C tokenizer into the Python tokenize

    The C tokenizer is more picky than the Python one, so we need to massage
    the error messages a bit for backwards compatibility.
    """
    if "unterminated triple-quoted string literal" in msg:
        return "EOF in multi-line string"
    return msg


def _generate_tokens_from_c_tokenizer(source, encoding=None, extra_tokens=False):
    """Tokenize a source reading Python code as unicode strings using the internal C tokenizer"""
    if encoding is None:
        it = TokenizerIter(source, extra_tokens=extra_tokens)
    else:
        it = TokenizerIter(source, encoding=encoding, extra_tokens=extra_tokens)
    try:
        for info in it:
            yield BuiltinTokenInfo._make(info)
    except SyntaxError as e:
        # pylint: disable=unidiomatic-typecheck
        if type(e) != SyntaxError:
            raise e from None
        msg = _transform_msg(e.msg)
        raise TokenError(msg, (e.lineno, e.offset)) from None
