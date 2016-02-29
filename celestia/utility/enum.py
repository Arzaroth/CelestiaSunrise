#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: enum.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

import copy

def enum(*args, **kwargs):
    enums = dict(zip(args, range(len(args))), **kwargs)
    enums['map'] = copy.copy(enums)
    enums['rmap'] = {}
    for k,v in enums.items():
        try:
            enums['rmap'][v] = k
        except TypeError:
            pass
    return type('Enum', (), enums)
