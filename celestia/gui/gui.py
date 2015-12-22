#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

try:
    # py3
    import tkinter as tk
except ImportError:
    # py2
    import Tkinter as tk
from .loading import Loading
from .ponygui import PonyGui

class Gui(object):
    def __init__(self, savedata):
        self.savedata = savedata
        self.tk = tk.Tk()
        self.tk.withdraw()
        self.tk.after(100, self.start)
        self.tk.mainloop()

    def start(self):
        ok = False
        while not ok:
            loading = Loading(self.tk, self.savedata)
            self.tk.wait_window(loading)
            ok = not loading.go_next
            if loading.go_next:
                ponygui = PonyGui(self.tk, loading.savedata)
                self.tk.wait_window(ponygui)
                ok = ponygui.loaded
        self.tk.destroy()
