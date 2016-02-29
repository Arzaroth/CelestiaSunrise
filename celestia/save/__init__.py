#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: __init__.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from .savemanager import SaveManager, SaveError
from .savemanager import decompress_data, compress_data
from .savedata import SaveData

__all__ = [
    'SaveManager',
    'SaveError',
    'SaveData',
    'decompress_data',
    'compress_data',
]
