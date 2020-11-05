import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
    ?start: value+
    ?value: atom | list_ | quote
    ?atom: number | char | string | boolean | name

    list_: "(" value+ ")"
    quote: "'" value

    number: /[-+]?[0-9]*\.?[0-9]+/
    char: /\#\\([A-Za-z]+|[\d]|[^\s0-9A-Za-z])/
    string: /('[^\n'\\]*(?:\\.[^\n'\\]*)*'|\"[^\n\"\\]*(?:\\.[^\n\"\\]*)*\")/
    boolean: /([#][t]|[#][f])/
    name: /([-+]|[.]{3}|[A-Za-z|*\/<=>!?:$%_&~^][\w|+-.*\/<=>!?:$%_&~^]*)/

    %ignore /[;][^\n]*/
    %ignore /\s+/
""")


class LispyTransformer(InlineTransformer):
    CHARS = {
        "altmode": "\x1b",
        "backnext": "\x1f",
        "backspace": "\b",
        "call": "SUB",
        "linefeed": "\n",
        "page": "\f",
        "return": "\r",
        "rubout": "\xc7",
        "space": " ",
        "tab": "\t",
    }

    def list_ (self, *arguments):
        return list(arguments)

    def number (self, token):
        return float(token)

    def string (self, token):
        return str(token[1:-1])
    
    def name (self, token):
        return Symbol(token)

    def boolean (self, token):
        if token == "#t":
            return True
        else:
            return False

    def char (self, token):
        token = token[2:]
        if token.lower() in self.CHARS:
            return self.CHARS[token.lower()]
        else:
            return token 

    def quote (self, token):
        return [Symbol('quote'), token]
    
    def start (self, *arguments):
        value_list = []
        value_list.append(Symbol('begin'))
        value_list = value_list + list(arguments)

        return value_list