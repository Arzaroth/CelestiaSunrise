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
        self.loading = Loading(savefile, gluid, legacy)

    def start(self):
        self.loading.mainloop()
        if self.loading.go_next:
            self.ponygui = PonyGui(self.loading.filename,
                                   self.loading.gluid,
                                   self.loading.legacy)
            self.ponygui.mainloop()
