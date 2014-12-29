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

def docopt_cmd(func):
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
