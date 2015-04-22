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
from src.utility.tkvardescriptor import TkVarDescriptor, TkVarDescriptorOwner
import six

@six.add_metaclass(TkVarDescriptorOwner)
class BaseGui(Tk, object):
    savefile = TkVarDescriptor(StringVar)
    gluid = TkVarDescriptor(StringVar)
    dbfile = TkVarDescriptor(StringVar)
    usedb = TkVarDescriptor(BooleanVar)
    legacy = TkVarDescriptor(BooleanVar)

    def __init__(self, savefile, gluid, dbfile, usedb, legacy):
        Tk.__init__(self)
        self.savefile = savefile or ""
        self.gluid = gluid or ""
        self.dbfile = dbfile or ""
        self.usedb = usedb
        self.legacy = legacy
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
        self._usedb_clicked()

    def reinit(self):
        self._remove_widgets()
        self._remove_frames()
        self.init()

    def _remove_frames(self):
        self._file_frame.grid_forget()
        self._key_frame.grid_forget()
        self._key_entry_frame.grid_forget()
        self._key_checkbox_frame.grid_forget()

    def _remove_widgets(self):
        self._file_label.grid_forget()
        self._file_entry.grid_forget()
        self._file_button.grid_forget()
        self._file_legacy.grid_forget()
        self._key_label.grid_forget()
        self._key_entry.grid_forget()
        self._key_button.grid_forget()
        self._key_dbfile.grid_forget()

    def _create_variables(self):
        pass

    def _create_frames(self):
        self._file_frame = Frame(self)
        self._key_frame = Frame(self)
        self._key_entry_frame = Frame(self._key_frame)
        self._key_checkbox_frame = Frame(self._key_frame)

    def _create_widgets(self):
        self._file_label = Label(self._file_frame,
                                 text="Savegame file: ")
        self._file_entry = Entry(self._file_frame,
                                 textvariable=BaseGui.savefile.raw_klass(self))
        self._file_button = Button(self._file_frame,
                                   text="Browse",
                                   command=lambda: BaseGui.savefile.__set__(self, askopenfilename()))
        self._file_legacy = Checkbutton(self._file_frame,
                                        text="Legacy file",
                                        variable=BaseGui.legacy.raw_klass(self),
                                        command=self._legacy_clicked)

        self._key_label = Label(self._key_entry_frame,
                                text="Key (GLUID): ")
        self._key_entry = Entry(self._key_entry_frame,
                                textvariable=BaseGui.gluid.raw_klass(self))
        self._key_button = Button(self._key_entry_frame,
                                  text="Browse",
                                  command=lambda: BaseGui.dbfile.__set__(self, askopenfilename()))
        self._key_dbfile = Checkbutton(self._key_checkbox_frame,
                                       text="Use gameloft_sharing database file",
                                       variable=BaseGui.usedb.raw_klass(self),
                                       command=self._usedb_clicked)

    def _grid_frames(self):
        options = dict(sticky=NSEW, padx=3, pady=4)
        self._key_entry_frame.grid(row=0, column=0, **options)
        self._key_checkbox_frame.grid(row=1, column=0, **options)

    def _grid_widgets(self):
        options = dict(padx=3, pady=4)
        self._file_label.grid(row=0, column=0, sticky=W, **options)
        self._file_entry.grid(row=0, column=1, sticky=NSEW, **options)
        self._file_button.grid(row=0, column=2, sticky=E, **options)
        self._file_legacy.grid(row=1, column=0, sticky=W, **options)
        self._key_label.grid(row=0, column=0, sticky=W, **options)
        self._key_entry.grid(row=0, column=1, **options)
        self._key_button.grid(row=0, column=2, sticky=E, **options)
        self._key_dbfile.grid(row=0, column=0, sticky=W, **options)

    def _legacy_clicked(self):
        if self.legacy:
            self._key_frame.grid_remove()
        else:
            self._key_frame.grid()

    def _usedb_clicked(self):
        if not self.usedb:
            self._key_button.grid_remove()
            self._key_entry.configure(textvariable=BaseGui.gluid.raw_klass(self))
        else:
            self._key_button.grid()
            self._key_entry.configure(textvariable=BaseGui.dbfile.raw_klass(self))
