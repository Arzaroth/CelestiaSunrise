#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gluid.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
import sqlite3
import json

class SQLError(Exception):
    pass


def retrieve_gluid(db_path):
    try:
        db = sqlite3.connect(db_path)
        cur = db.execute('SELECT value FROM glshare WHERE key = ?',
                         ('ANMP.GloftPOHM_GAIA_ENC_KEY_GLUID',))
        value, = cur.fetchone()
        res = json.loads(value)
        gluid = res['data']
    except:
        raise SQLError('Unable to retrieve GLUID from file')
    return gluid
