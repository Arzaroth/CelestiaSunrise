#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: docopt_utils.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from functools import wraps
from collections import defaultdict
from docopt import docopt, DocoptExit

def docopt_cmd(func):
    @wraps(func)
    def wrapper(self, args):
        try:
            args = docopt(func.__doc__, args)
        except DocoptExit as e:
            print(e)
            return
        except SystemExit:
            return
        return func(self, args)
    return wrapper
