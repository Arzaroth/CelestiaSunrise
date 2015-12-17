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
from celestia.utility.config import Config

class Gui(object):
    def __init__(self, savedata):
        self.savedata = savedata

    def start(self):
        if Config.config["startup_check"]:
            pass
        ok = False
        while not ok:
            loading = Loading(self.savedata)
            ok = not loading.go_next and not loading.unload
            if loading.go_next:
                ponygui = PonyGui(loading.savedata)
                ok = ponygui.loaded and not ponygui.unload
