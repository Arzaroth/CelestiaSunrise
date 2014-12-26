#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponygui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import base64
from tkinter import Label, Button, Frame, Toplevel
from tkinter.ttk import Notebook
from tkinter.constants import N, S, E, W, NSEW
from tkinter.messagebox import showerror
from src.basegui import BaseGui
from src.currenciesframe import CurrenciesFrame
from src.zonesframe import ZonesFrame
from src import SaveManager, SaveError
from src import decompress_data, compress_data
from src import XmlHandler

class LoadingDialog(Toplevel):

    def __init__(self, parent):
        super(LoadingDialog, self).__init__()
        Label(self, text="Loading...", font=25, height=3, width=25).pack()
        self.update()


class PonyGui(BaseGui):

    def __init__(self, savefile, gluid, legacy):
        super(PonyGui, self).__init__(savefile, gluid, legacy)
        self.loaded = False
        self.withdraw()
        self._load_xml()
        if self.loaded:
            super(PonyGui, self).init()
            self.deiconify()
            self.update_idletasks()

    def _load_xml(self):
        loadingbox = LoadingDialog(self)
        if not self.legacy:
            gluid = base64.b64decode(self.gluid)
        else:
            gluid = b''
        self._save_manager = SaveManager(self.savefile,
                                         gluid)
        try:
            data, self.save_number = self._save_manager.load(self.legacy)
            if not self.legacy:
                data = decompress_data(data)
        except Exception as e:
            showerror("Error",
                      "Was unable to load from file, reason: {}".format(str(e)))
            self.destroy()
        else:
            self.loaded = True
            self._xml_handle = XmlHandler(data.decode('utf-8'))
            self._xml_handle.pre_load()
            loadingbox.destroy()

    def _create_variables(self):
        super(PonyGui, self)._create_variables()
        self._notebook = Notebook(self)

    def _create_frames(self):
        super(PonyGui, self)._create_frames()
        self._currencies_frame = CurrenciesFrame(self, self._xml_handle)
        self._zones_frame = ZonesFrame(self, self._xml_handle)
        self._notebook.add(self._currencies_frame,
                           text="Currencies")
        self._notebook.add(self._zones_frame,
                           text="Zones")
        self._save_button = Button(self,
                                   text="Save to file",
                                   command=self._save)

    def _grid_frames(self):
        super(PonyGui, self)._grid_frames()
        self._file_frame.grid(row=0, column=0, pady=5, sticky=NSEW)
        self._key_frame.grid(row=1, column=0, pady=10, sticky=NSEW)
        self._notebook.grid(row=3, column=0, sticky=NSEW)

    def _grid_widgets(self):
        super(PonyGui, self)._grid_widgets()
        self._save_button.grid(row=2, column=0, sticky=NSEW, padx=3, pady=4)

    def _save(self):
        try:
            if not self.legacy:
                gluid = base64.b64decode(self.gluid)
            else:
                gluid = b''
        except:
            showerror("Error", "Bad encryption key")
        else:
            loadingbox = LoadingDialog(self)
            self._currencies_frame.commit()
            self._zones_frame.commit()
            try:
                self._save_manager.save(compress_data(repr(self._xml_handle)
                                                      .encode('utf-8')),
                                        self.savefile,
                                        self.save_number,
                                        gluid,
                                        self.legacy)
            except Exception as e:
                showerror("Error",
                          "Was unable to write to file, reason: {}".format(str(e)))
            loadingbox.destroy()
