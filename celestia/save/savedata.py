#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: savedata.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import binascii
from celestia.utility.gluid import GluidError, retrieve_gluid

class SaveData(object):
    def __init__(self,
                 savefile, gluid, dbfile,
                 usedb, legacy):
        self.savefile = savefile
        self._gluid = gluid if gluid else b''
        self.dbfile = dbfile
        self.usedb = usedb
        self.legacy = legacy

    @property
    def gluid(self):
        if not self.legacy:
            gluid = retrieve_gluid(self.dbfile) if self.usedb else self._gluid
            try:
                gluid = binascii.a2b_base64(gluid)
            except binascii.Error:
                raise GluidError("Bad encryption key")
        else:
            gluid = b''
        return gluid
