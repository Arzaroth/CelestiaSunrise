#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: loading.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import binascii
try:
    # py3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import N, S, E, W, NSEW
    from tkinter.messagebox import showerror
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import N, S, E, W, NSEW
    from tkMessageBox import showerror
from .basegui import BaseGui
from celestia.utility.gluid import retrieve_gluid
from celestia.utility.config import Config

class Loading(BaseGui):
    def __init__(self, *args):
        BaseGui.__init__(self, *args)
        self.go_next = False
        BaseGui.init(self)
        if Config.config["startup_check"]:
            self._check_update(True)

    def _remove_frames(self):
        BaseGui._remove_frames(self)
        self._disclaimer_frame.grid_forget()

    def _remove_widgets(self):
        BaseGui._remove_widgets(self)
        self._disclaimer_label1.grid_forget()
        self._disclaimer_label2.grid_forget()
        self._ok_button.grid_forget()

    def _create_frames(self):
        BaseGui._create_frames(self)
        self._disclaimer_frame = ttk.Frame(self._main_frame)

    def _create_widgets(self):
        BaseGui._create_widgets(self)
        self._disclaimer_label1 = ttk.Label(self._disclaimer_frame,
                                            text='Your savegame is most likely called "mlp_save_prime.dat".')
        self._disclaimer_label2 = ttk.Label(self._disclaimer_frame,
                                            text="Make backups before using this tool.")
        self._ok_button = ttk.Button(self._main_frame,
                                     text="Go!",
                                     command=self._next)
        self._filemenu.add_command(label="Exit", command=self.destroy)
        self._editmenu.add_command(label="Preferences", command=self._preferences_popup)

    def _grid_frames(self):
        BaseGui._grid_frames(self)
        self._disclaimer_frame.grid(row=0, column=0, sticky=NSEW)
        self._file_frame.grid(row=1, column=0, pady=10, sticky=NSEW)
        self._key_frame.grid(row=2, column=0, pady=5, sticky=NSEW)

    def _grid_widgets(self):
        BaseGui._grid_widgets(self)
        options = dict(sticky=W, padx=0, pady=2)
        self._disclaimer_label1.grid(row=0, column=0,
                                     **options)
        self._disclaimer_label2.grid(row=1, column=0,
                                     **options)
        self._ok_button.grid(row=3, column=0, sticky=NSEW, padx=3, pady=4)

    def _next(self):
        try:
            if not self.legacy:
                gluid = retrieve_gluid(self.dbfile) if self.usedb else self.gluid
                binascii.a2b_base64(gluid)
        except:
            showerror("Error", "Bad decryption key")
        else:
            self.go_next = True
            self.destroy()
