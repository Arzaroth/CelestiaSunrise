#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: basegui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
try:
    # py3
    from tkinter import (Tk, Frame,
                         Label, Entry,
                         Button, Checkbutton,
                         StringVar, BooleanVar)
    from tkinter.filedialog import askopenfilename
    from tkinter.constants import N, S, E, W, NSEW
except ImportError:
    # py2
    from Tkinter import (Tk, Frame,
                         Label, Entry,
                         Button, Checkbutton,
                         StringVar, BooleanVar)
    from tkFileDialog import askopenfilename
    from Tkconstants import N, S, E, W, NSEW

class BaseGui(Tk):

    def __init__(self, savefile, gluid, legacy):
        Tk.__init__(self)
        self.__savefile = savefile
        self.__gluid = gluid
        self.__legacy = legacy
        self.grid()
        self.wm_title("Celestia Sunrise")
        self.resizable(False, False)
        self.bind('<Escape>', lambda _: self.destroy())
        self._create_variables()

    def init(self):
        self._create_frames()
        self._create_widgets()
        self._grid_frames()
        self._grid_widgets()
        self._legacy_clicked()

    def _create_variables(self):
        self._savefile = StringVar(self, self.__savefile)
        self._gluid = StringVar(self, self.__gluid)
        self._legacy = BooleanVar(self, self.__legacy)

    def _create_frames(self):
        self._file_frame = Frame(self)
        self._key_frame = Frame(self)

    def _create_widgets(self):
        self._file_label = Label(self._file_frame,
                                 text="Savegame file: ")
        self._file_entry = Entry(self._file_frame,
                                 textvariable=self._savefile)
        self._file_button = Button(self._file_frame,
                                   text="Browse",
                                   command=lambda: self._savefile.set(askopenfilename()))
        self._file_legacy = Checkbutton(self._file_frame,
                                        text="Legacy file",
                                        variable=self._legacy,
                                        command=self._legacy_clicked)

        self._key_label = Label(self._key_frame,
                                text="Key (GLUID): ")
        self._key_entry = Entry(self._key_frame,
                                textvariable=self._gluid)

    def _grid_frames(self):
        pass

    def _grid_widgets(self):
        options = dict(sticky=NSEW, padx=3, pady=4)
        self._file_label.grid(row=0, column=0, **options)
        self._file_entry.grid(row=0, column=1, **options)
        self._file_button.grid(row=0, column=2, **options)
        self._file_legacy.grid(row=1, column=0, **options)
        self._key_label.grid(row=0, column=0, **options)
        self._key_entry.grid(row=0, column=1, **options)

    def _legacy_clicked(self):
        if self.legacy:
            self._key_frame.grid_remove()
        else:
            self._key_frame.grid()

    @property
    def savefile(self):
        return self._savefile.get()

    @property
    def gluid(self):
        return self._gluid.get()

    @property
    def legacy(self):
        return self._legacy.get()
