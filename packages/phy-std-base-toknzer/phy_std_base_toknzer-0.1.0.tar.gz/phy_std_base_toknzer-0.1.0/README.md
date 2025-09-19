# Consistent Tokenizer Across Python Versions

This project is part of [`phy`](https://github.com/phy-precompiler).

## Overview

Python's built-in [`token`](https://docs.python.org/3/library/token.html) module assigns an **integer value** to each token type. However, these numeric values are **not guaranteed to be stable** across Python versions.  

| token type       | python 3.10 | python 3.11 | python 3.12 | python 3.13 | python 3.14 |
|------------------|-------------|-------------|-------------|-------------|-------------|
| ENDMARKER        | 0           | 0           | 0           | 0           | 0           |
| NAME             | 1           | 1           | 1           | 1           | 1           |
| NUMBER           | 2           | 2           | 2           | 2           | 2           |
| STRING           | 3           | 3           | 3           | 3           | 3           |
| NEWLINE          | 4           | 4           | 4           | 4           | 4           |
| INDENT           | 5           | 5           | 5           | 5           | 5           |
| DEDENT           | 6           | 6           | 6           | 6           | 6           |
| LPAR             | 7           | 7           | 7           | 7           | 7           |
| RPAR             | 8           | 8           | 8           | 8           | 8           |
| LSQB             | 9           | 9           | 9           | 9           | 9           |
| RSQB             | 10          | 10          | 10          | 10          | 10          |
| COLON            | 11          | 11          | 11          | 11          | 11          |
| COMMA            | 12          | 12          | 12          | 12          | 12          |
| SEMI             | 13          | 13          | 13          | 13          | 13          |
| PLUS             | 14          | 14          | 14          | 14          | 14          |
| MINUS            | 15          | 15          | 15          | 15          | 15          |
| STAR             | 16          | 16          | 16          | 16          | 16          |
| SLASH            | 17          | 17          | 17          | 17          | 17          |
| VBAR             | 18          | 18          | 18          | 18          | 18          |
| AMPER            | 19          | 19          | 19          | 19          | 19          |
| LESS             | 20          | 20          | 20          | 20          | 20          |
| GREATER          | 21          | 21          | 21          | 21          | 21          |
| EQUAL            | 22          | 22          | 22          | 22          | 22          |
| DOT              | 23          | 23          | 23          | 23          | 23          |
| PERCENT          | 24          | 24          | 24          | 24          | 24          |
| LBRACE           | 25          | 25          | 25          | 25          | 25          |
| RBRACE           | 26          | 26          | 26          | 26          | 26          |
| EQEQUAL          | 27          | 27          | 27          | 27          | 27          |
| NOTEQUAL         | 28          | 28          | 28          | 28          | 28          |
| LESSEQUAL        | 29          | 29          | 29          | 29          | 29          |
| GREATEREQUAL     | 30          | 30          | 30          | 30          | 30          |
| TILDE            | 31          | 31          | 31          | 31          | 31          |
| CIRCUMFLEX       | 32          | 32          | 32          | 32          | 32          |
| LEFTSHIFT        | 33          | 33          | 33          | 33          | 33          |
| RIGHTSHIFT       | 34          | 34          | 34          | 34          | 34          |
| DOUBLESTAR       | 35          | 35          | 35          | 35          | 35          |
| PLUSEQUAL        | 36          | 36          | 36          | 36          | 36          |
| MINEQUAL         | 37          | 37          | 37          | 37          | 37          |
| STAREQUAL        | 38          | 38          | 38          | 38          | 38          |
| SLASHEQUAL       | 39          | 39          | 39          | 39          | 39          |
| PERCENTEQUAL     | 40          | 40          | 40          | 40          | 40          |
| AMPEREQUAL       | 41          | 41          | 41          | 41          | 41          |
| VBAREQUAL        | 42          | 42          | 42          | 42          | 42          |
| CIRCUMFLEXEQUAL  | 43          | 43          | 43          | 43          | 43          |
| LEFTSHIFTEQUAL   | 44          | 44          | 44          | 44          | 44          |
| RIGHTSHIFTEQUAL  | 45          | 45          | 45          | 45          | 45          |
| DOUBLESTAREQUAL  | 46          | 46          | 46          | 46          | 46          |
| DOUBLESLASH      | 47          | 47          | 47          | 47          | 47          |
| DOUBLESLASHEQUAL | 48          | 48          | 48          | 48          | 48          |
| AT               | 49          | 49          | 49          | 49          | 49          |
| ATEQUAL          | 50          | 50          | 50          | 50          | 50          |
| RARROW           | 51          | 51          | 51          | 51          | 51          |
| ELLIPSIS         | 52          | 52          | 52          | 52          | 52          |
| COLONEQUAL       | 53          | 53          | 53          | 53          | 53          |
| EXCLAMATION      |             |             | 54          | 54          | 54          |
| OP               | 54          | 54          | 55          | 55          | 55          |
| AWAIT            | 55          | 55          | 56          |             |             |
| ASYNC            | 56          | 56          | 57          |             |             |
| TYPE_IGNORE      | 57          | 57          | 58          | 56          | 56          |
| TYPE_COMMENT     | 58          | 58          | 59          | 57          | 57          |
| SOFT_KEYWORD     | 59          | 59          | 60          | 58          | 58          |
| FSTRING_START    |             |             | 61          | 59          | 59          |
| FSTRING_MIDDLE   |             |             | 62          | 60          | 60          |
| FSTRING_END      |             |             | 63          | 61          | 61          |
| TSTRING_START    |             |             |             |             | 62          |
| TSTRING_MIDDLE   |             |             |             |             | 63          |
| TSTRING_END      |             |             |             |             | 64          |
| COMMENT          |             |             | 64          | 62          | 65          |
| NL               |             |             | 65          | 63          | 66          |
| ERRORTOKEN       | 60          | 60          | 66          | 64          | 67          |
| N_TOKENS         | 64          | 64          | 68          | 66          | 69          |
| NT_OFFSET        | 256         | 256         | 256         | 256         | 256         |


This may lead to necessary extra works about token codes alignment if your project relies on consistent numeric token codes across environments (e.g., for serialization, tooling, or cross-version analysis).

---

## What this Project Does

This repository extracts the **core logic of `tokenize`** from the upcoming **Python 3.14 source code** and provides a compatibility layer that works consistently on:

- Python **3.10**
- Python **3.11**
- Python **3.12**
- Python **3.13**
- Python **3.14 (future release)**

With this library, the **same token type always maps to the same integer value** no matter which Python version you are running.

This library has **ZERO** dependencies.

---

## This library is helpeful for

- Tools like linters, formatters, or static analyzers often depend on token IDs.  
- If these IDs change between Python versions, cross-version compatibility needs extra works.  
- By standardizing on the **3.14 token ID mapping**, this project ensures stability and reproducibility.

Think of it as a **"frozen" token ID specification**: even as Python evolves, your code will see a consistent view of the token stream.

---

## Features

- ✅ Extracted directly from CPython 3.14’s `tokenize` implementation.  
- ✅ Compatible with Python 3.10–3.14.  
- ✅ Guarantees **stable token type IDs** across versions.  
- ✅ Drop-in replacement for projects that care about token stability.  

---

## Installation

```bash
pip install phy-std-base-toknzer
```

## How to use

Use this library is like using builtin method `tokenize.tokenize`:
+ first, import this module `std_base_toknzer`;
+ then, create an `io.IOBase.readline()` object from code string;
+ create an iterator by `TokenizerIter`, which will generate tokens.

The generated token are 4-elements tuple like builtin `tokenize.TokenInfo` object:
`(type, string, (start_lineno, start_col_offset), (end_lineno, end_col_offset))`.

It is not nameTuple like `tokenize.TokenInfo` gives, you can only get attributes by subscript. `type` is the 
token type int value defined in `token` module of python 3.14.

```python
from io import BytesIO
import std_base_toknzer

code = '''print(f"hello world to {greeter}!")\ntemplate=t"input a {name}"\n'''
code_readline = BytesIO(code.encode('utf-8')).readline

_iter = std_base_toknzer.TokenizerIter(code_readline, encoding='utf-8')
for _token in _iter:
    print(_token)
    print(type(_token))
```




## Development

This library use [`scikit-build-core`](https://github.com/scikit-build/scikit-build-core), `cmake` is needed for building the wheel.

```bash
pip install .
```
