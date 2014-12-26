#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: window.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import base64
from tkinter import Label, Button, Frame, StringVar, BooleanVar
from tkinter.constants import N, S, E, W, NSEW
from tkinter.messagebox import showerror
from src.basegui import BaseGui

class Loading(BaseGui):

    def __init__(self, savefile="", gluid="", legacy=False):
        super(Loading, self).__init__(savefile, gluid, legacy)
        self.go_next = False
        super(Loading, self).init()

    def _create_frames(self):
        super(Loading, self)._create_frames()
        self._disclaimer_frame = Frame(self)

    def _create_widgets(self):
        super(Loading, self)._create_widgets()
        self._disclaimer_label1 = Label(self._disclaimer_frame,
                                        text='Your savegame is most likely called "mlp_save_prime.dat".')
        self._disclaimer_label2 = Label(self._disclaimer_frame,
                                        text="Make backups before using this tool.")
        self._ok_button = Button(self,
                                 text="Go !",
                                 command=self._next)

    def _grid_frames(self):
        super(Loading, self)._grid_frames()
        self._disclaimer_frame.grid(row=0, column=0, sticky=NSEW)
        self._file_frame.grid(row=1, column=0, pady=10, sticky=NSEW)
        self._key_frame.grid(row=2, column=0, pady=5, sticky=NSEW)

    def _grid_widgets(self):
        super(Loading, self)._grid_widgets()
        options = dict(sticky=W, padx=0, pady=2)
        self._disclaimer_label1.grid(row=0, column=0,
                                     **options)
        self._disclaimer_label2.grid(row=1, column=0,
                                     **options)
        self._ok_button.grid(row=3, column=0, sticky=NSEW, padx=3, pady=4)

    def _next(self):
        try:
            if not self.legacy:
                base64.b64decode(self.gluid)
        except:
            showerror("Error", "Bad decryption key")
        else:
            self.go_next = True
            self.destroy()
