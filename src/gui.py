#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
from src.loading import Loading
from src.ponygui import PonyGui

class Gui(object):

    def __init__(self, savefile, gluid, dbfile, legacy):
        self.savefile = savefile
        self.gluid = gluid
        self.dbfile = dbfile
        self.legacy = legacy

    def start(self):
        ok = False
        while not ok:
            loading = Loading(self.savefile,
                              self.gluid,
                              self.dbfile,
                              self.dbfile is not None,
                              self.legacy)
            loading.mainloop()
            ok = not loading.go_next
            if loading.go_next:
                ponygui = PonyGui(loading.savefile,
                                  loading.gluid,
                                  loading.dbfile,
                                  loading.usedb,
                                  loading.legacy)
                ponygui.mainloop()
                ok = ponygui.loaded
