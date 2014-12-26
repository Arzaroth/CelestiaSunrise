#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from src import Loading

class Gui(object):

    def __init__(self, savefile="", gluid=""):
        self.loading = Loading(savefile, gluid)

    def start(self):
        self.loading.mainloop()
        if self.loading.go_next:
            print(self.loading.filename)
            print(self.loading.gluid)
