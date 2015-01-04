#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: docopt_utils.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
from functools import wraps
from collections import defaultdict
from docopt import ParentPattern, ChildPattern, Option
import shlex

def flatten(l, init=[]):
    res = init[:]
    for x in l:
        if type(x) is list:
            res.extend(flatten(x))
        else:
            res.append(x)
    return res

def noflat_parent(self):
    return [c.noflat() for c in self.children]
def noflat_children(self):
    return self.name
def noflat_option(self):
    return [self.short, self.long] if self.short and self.long else self.name
ParentPattern.noflat = noflat_parent
ChildPattern.noflat = noflat_children
Option.noflat = noflat_option

def docopt_cmd(docstring):
    def dekorator(func):
        func.__doc__ = docstring
        @wraps(func)
        def wrapper(self, args):
            from docopt import docopt, DocoptExit
            try:
                args = docopt(func.__doc__, args)
            except DocoptExit as e:
                print(e)
                return
            except SystemExit:
                return
            return func(self, args)
        return wrapper
    return dekorator

def docopt_cmd_completion(docstring, **kwargs):

    from docopt import (parse_defaults, parse_pattern,
                        formal_usage, printable_usage)
    options = parse_defaults(docstring)
    pattern = parse_pattern(formal_usage(printable_usage(docstring)),
                            options).children[0]

    def get_state(it, pattern):
        try:
            value = next(it)
        except StopIteration:
            return pattern
        res = []
        for x in pattern:
            if ((type(x[0]) == list and value in flatten(x[0])) or
                value == x[0]):
                res.append(x[1:])
        if res:
            return get_state(it, res)
        return []

    def dekorator(dekorated):
        @wraps(dekorated)
        def wrapper(self, text, line, begidx, endidx):
            argv = shlex.split(line[:endidx])[1:]
            if not line[endidx - 1].isspace():
                target = argv[-1]
                argv = argv[:-1]
            else:
                target = ''
            state = get_state(iter(argv), pattern.noflat())
            res = []
            for x in state:
                if type(x[0]) == list:
                    res.extend(flatten(x[0]))
                else:
                    res.append(x[0])
            return list(set(x for x in res if x.startswith(target)))
        return wrapper
    return dekorator
