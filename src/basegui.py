#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: basegui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from tkinter import Tk

class BaseGui(Tk):

    def __init__(self):
        super(BaseGui, self).__init__()
        self.grid()
        self.wm_title("Celestia Sunrise")
        self.resizable(False, False)
        self.bind('<Escape>', lambda _: self.destroy())
