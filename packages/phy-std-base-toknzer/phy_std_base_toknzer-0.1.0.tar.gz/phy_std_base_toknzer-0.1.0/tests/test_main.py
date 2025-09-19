# pylint: disable=missing-function-docstring,unused-import
""" main test cases """
# imports
from io import BytesIO
from pprint import pprint
import pytest


@pytest.mark.skip()
def test_mod_avaiable():
    # pylint: disable=import-outside-toplevel
    import std_base_toknzer
    pprint(std_base_toknzer.__dict__)


# @pytest.mark.skip()
def test_std_base_toknzer():
    code = '''print(f"hello world to {greeter}!")\ntemplate=t"input a {name}"\n'''
    code_readline = BytesIO(code.encode('utf-8')).readline

    # pylint: disable=import-outside-toplevel
    import std_base_toknzer

    # pylint: disable=c-extension-no-member
    _iter = std_base_toknzer.TokenizerIter(code_readline, encoding='utf-8')
    for _token in _iter:
        print(_token)
        print(type(_token))
