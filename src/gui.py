#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import base64
from src.loading import Loading
from src.ponygui import PonyGui

class Gui(object):

    def __init__(self, savefile="", gluid="", legacy=False):
        self.savefile = savefile
        self.gluid = gluid
        self.legacy = legacy

    def start(self):
        ok = False
        loading = Loading(self.savefile,
                          self.gluid,
                          self.legacy)
        loading.mainloop()
        if loading.go_next:
            ponygui = PonyGui(loading.filename,
                              base64.b64decode(loading.gluid),
                              loading.legacy)
            ponygui.mainloop()
