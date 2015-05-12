#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: savedata.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import binascii
from celestia.utility.gluid import retrieve_gluid

class SaveData(object):
    def __init__(self,
                 savefile, gluid, dbfile,
                 usedb, legacy):
        self.savefile = savefile
        self._gluid = gluid
        self.dbfile = dbfile
        self.usedb = usedb
        self.legacy = legacy

    @property
    def gluid(self):
        if not self.legacy:
            gluid = retrieve_gluid(self.dbfile) if self.usedb else self._gluid
            gluid = binascii.a2b_base64(gluid)
        else:
            gluid = b''
        return gluid
