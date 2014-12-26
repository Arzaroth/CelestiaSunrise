#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponygui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from tkinter import Label, Button, Entry, StringVar, Frame
from tkinter.ttk import Notebook
from tkinter.filedialog import askopenfilename
from tkinter.constants import N, S, E, W, NSEW
from src.basegui import BaseGui

class PonyGui(BaseGui):

    def __init__(self, savefile, gluid, legacy):
        super(PonyGui, self).__init__()

        self._notebook = Notebook(self)

        self._create_frames()
        self._grid_frames()

    def _create_frames(self):
        pass

    def _grid_frames(self):
        pass
