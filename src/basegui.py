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

        self._create_variables()
        self._create_frames()
        self._create_widgets()
        self._grid_frames()
        self._grid_widgets()

    def _create_variables(self):
        pass

    def _create_frames(self):
        pass

    def _create_widgets(self):
        pass

    def _grid_frames(self):
        pass

    def _grid_widgets(self):
        pass
