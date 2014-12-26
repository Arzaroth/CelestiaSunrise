#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from src.loading import Loading
from src.ponygui import PonyGui

class Gui(object):

    def __init__(self, savefile="", gluid="", legacy=False):
        self.savefile = savefile
        self.gluid = gluid
        self.legacy = legacy

    def start(self):
        ok = False
        while not ok:
            loading = Loading(self.savefile,
                              self.gluid,
                              self.legacy)
            loading.mainloop()
            ok = not loading.go_next
            if loading.go_next:
                ponygui = PonyGui(loading.savefile,
                                  loading.gluid,
                                  loading.legacy)
                ponygui.mainloop()
                ok = ponygui.loaded
