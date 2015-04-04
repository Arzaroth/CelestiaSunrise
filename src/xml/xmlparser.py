#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: test.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from pyrser import grammar, meta
from pyrser.directives import ignore
from collections import OrderedDict

class XMLParser(grammar.Grammar):
    """Naive XML parser using pyrser"""
    entry = "xml"
    grammar = """
    xml = [ tag:>_ eof ]

    tag =
    [
        [
            inline_tag:>_
        ] | [
            opening_tag:>_
            [tag:v #add_tag(_, v) | text:t #add_text(_, t)]*
            closing_tag:ct
            #tag_matches(_, ct)
        ]
    ]

    opening_tag =
    [
        '<' #init_tag(_) id:n #name_tag(_, n) [attribute:a #add_attribute(_, a)]* '>'
    ]

    closing_tag =
    [
        "</" #init_tag(_) id:n #name_tag(_, n) '>'
    ]

    inline_tag =
    [
        '<' #init_tag(_) id:n #name_tag(_, n) [attribute:a #add_attribute(_, a)]* "/>"
    ]

    attribute_value = [ string:s #is_str(_, s) ]
    attribute = [ id:n '=' attribute_value:v #name_attribute(_, n, v) ]

    text = [ @ignore("null") #c_text(_) ]
"""

def append(dikt, key, value):
    if key in dikt:
        if type(dikt[key]) != list:
            dikt[key] = [dikt[key]]
        dikt[key].append(value)
    else:
        dikt[key] = value

@meta.hook(XMLParser)
def c_text(self, ast):
    self._stream.save_context()
    idx = self._stream.index
    if self.read_until('<'):
        self._stream.decpos()
        txt = self._stream[idx:self._stream.index]
        if not txt:
            return self._stream.restore_context()
        return self._stream.validate_context()
    return self._stream.restore_context()

@meta.hook(XMLParser)
def c_text(self, ast):
    self._stream.save_context()
    idx = self._stream.index
    if self.read_until('<'):
        self._stream.decpos()
        txt = self._stream[idx:self._stream.index]
        if not txt:
            return self._stream.restore_context()
        return self._stream.validate_context()
    return self._stream.restore_context()

@meta.hook(XMLParser)
def is_num(self, ast, n):
    ast.node = float(self.value(n))
    return True

@meta.hook(XMLParser)
def is_str(self, ast, s):
    ast.node = self.value(s).strip('"')
    return True

@meta.hook(XMLParser)
def init_tag(self, ast):
    ast.node = OrderedDict()
    return True

@meta.hook(XMLParser)
def add_tag(self, ast, tag):
    append(ast.node[ast.tagname], tag.tagname, tag.node[tag.tagname])
    return True

@meta.hook(XMLParser)
def add_text(self, ast, text):
    append(ast.node[ast.tagname], "#text", self.value(text).strip())
    return True

@meta.hook(XMLParser)
def name_tag(self, ast, tagname):
    ast.tagname = self.value(tagname)
    ast.node[ast.tagname] = OrderedDict()
    return True

@meta.hook(XMLParser)
def name_attribute(self, ast, name, value):
    ast.node = (self.value(name), value.node)
    return True

@meta.hook(XMLParser)
def add_attribute(self, ast, attribute):
    attr_name = '@' + attribute.node[0]
    append(ast.node[ast.tagname], attr_name, attribute.node[1])
    return True

@meta.hook(XMLParser)
def tag_matches(self, ast, closing_tag):
    return ast.tagname == closing_tag.tagname
