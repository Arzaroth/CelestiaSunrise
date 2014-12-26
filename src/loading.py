#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: window.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import base64
from tkinter import Label, Button, Entry, Checkbutton, Frame, StringVar, BooleanVar
from tkinter.filedialog import askopenfilename
from tkinter.constants import N, S, E, W, NSEW
from tkinter.messagebox import showerror
from src.basegui import BaseGui

class Loading(BaseGui):

    def __init__(self, savefile="", gluid=b"", legacy=False):
        super(Loading, self).__init__()
        self.go_next = False

        self._create_variables(savefile, gluid, legacy)
        self._create_frames()
        self._create_widgets()
        self._grid_frames()
        self._grid_widgets()

        self._legacy_clicked()

    def _create_variables(self, savefile="", gluid="", legacy=False):
        print('ehlo')
        super(Loading, self)._create_variables()
        self._filename = StringVar(self, savefile)
        self._gluid = StringVar(self, gluid)
        self._legacy = BooleanVar(self, legacy)

    def _create_frames(self):
        super(Loading, self)._create_frames()
        self._disclaimer_frame = Frame(self)
        self._file_frame = Frame(self)
        self._key_frame = Frame(self)

    def _create_widgets(self):
        super(Loading, self)._create_widgets()
        self._disclaimer_label1 = Label(self._disclaimer_frame,
                                        text='Your savegame is most likely called "mlp_save_prime.dat".')
        self._disclaimer_label2 = Label(self._disclaimer_frame,
                                        text="Make backups before using this tool.")

        self._file_label = Label(self._file_frame,
                                 text="Savegame file: ")
        self._file_entry = Entry(self._file_frame,
                                 textvariable=self._filename)
        self._file_button = Button(self._file_frame,
                                   text="Browse",
                                   command=lambda: self._filename.set(askopenfilename()))
        self._file_legacy = Checkbutton(self._file_frame,
                                        text="Legacy file",
                                        variable=self._legacy,
                                        command=self._legacy_clicked)

        self._key_label = Label(self._key_frame,
                                text="Decryption key (GLUID): ")
        self._key_entry = Entry(self._key_frame,
                                textvariable=self._gluid)

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

        options = dict(sticky=NSEW, padx=3, pady=4)
        self._file_label.grid(row=0, column=0, **options)
        self._file_entry.grid(row=0, column=1, **options)
        self._file_button.grid(row=0, column=2, **options)
        self._file_legacy.grid(row=1, column=0, **options)

        self._key_label.grid(row=0, column=0, **options)
        self._key_entry.grid(row=0, column=1, **options)

        self._ok_button.grid(row=3, column=0, **options)

    def _legacy_clicked(self):
        if self.legacy:
            self._key_frame.grid_remove()
        else:
            self._key_frame.grid()

    def _next(self):
        try:
            base64.b64decode(self.gluid)
        except:
            showerror("Error", "Bad decryption key")
        else:
            self.go_next = True
            self.destroy()

    @property
    def filename(self):
        return self._filename.get()

    @property
    def gluid(self):
        return self._gluid.get()

    @property
    def legacy(self):
        return self._legacy.get()
