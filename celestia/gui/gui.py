#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

from .loading import Loading
from .ponygui import PonyGui

class Gui(object):
    def __init__(self, savedata):
        self.savedata = savedata

    def start(self):
        ok = False
        while not ok:
            loading = Loading(self.savedata)
            loading.mainloop()
            ok = not loading.go_next
            if loading.go_next:
                ponygui = PonyGui(loading.savedata)
                ponygui.mainloop()
                ok = ponygui.loaded
