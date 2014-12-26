#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponygui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from collections import OrderedDict
from tkinter import Label, Button, Entry, StringVar, Frame, Toplevel
from tkinter.ttk import Notebook
from tkinter.filedialog import askopenfilename
from tkinter.constants import N, S, E, W, NSEW
from tkinter.messagebox import showerror
from src.basegui import BaseGui
from src import SaveManager, SaveError
from src import decompress_data, compress_data
from src import XmlHandler
from src.defaultordereddict import DefaultOrderedDict

class CurrencyFrame(Frame):

    def __init__(self, parent, text, value):
        super(CurrencyFrame, self).__init__(parent)

        self._value = StringVar(self, value)

        self._label = Label(self, text=text)
        self._entry = Entry(self, textvariable=self._value)

        options = dict(sticky=NSEW, padx=3, pady=4)
        self._label.grid(row=0, column=0, **options)
        self._entry.grid(row=0, column=1, **options)

    @property
    def value(self):
        return self._value.get()


class CurrenciesFrame(Frame):

    def __init__(self, parent, xml_handle):
        super(CurrenciesFrame, self).__init__(parent)

        self._xml_handle = xml_handle
        self._currencies = DefaultOrderedDict(OrderedDict)
        for name, typ in xml_handle.currencies.items():
            for cur, val in typ.items():
                self._currencies[name][cur] = CurrencyFrame(self, cur, val.value)
                self._currencies[name][cur].grid()

    def commit(self):
        for name, typ in xml_handle.currencies.items():
            for cur, val in typ.items():
                val.value = self._currencies[name][cur].value


class LoadingDialog(Toplevel):

    def __init__(self, parent):
        super(LoadingDialog, self).__init__()
        Label(self, text="Loading...").pack()


class PonyGui(BaseGui):

    def __init__(self, savefile, gluid, legacy):
        super(PonyGui, self).__init__()

        self.savefile = savefile
        self.gluid = gluid
        self.legacy = legacy
        self.withdraw()
        self._load_xml()
        self._notebook = Notebook(self)
        self._create_frames()
        self._grid_frames()
        self.deiconify()
        self.update_idletasks()

    def _load_xml(self):
        loadingbox = LoadingDialog(self)
        loadingbox.update()
        self._save_manager = SaveManager(self.savefile,
                                         self.gluid)
        data, self.save_number = self._save_manager.load(self.legacy)
        if not self.legacy:
            data = decompress_data(data)
        self._xml_handle = XmlHandler(data.decode('utf-8'))
        self._xml_handle.pre_load()
        loadingbox.destroy()

    def _create_frames(self):
        self._currencies_frame = CurrenciesFrame(self, self._xml_handle)
        self._notebook.add(self._currencies_frame,
                           text="Currencies")

    def _grid_frames(self):
        self._notebook.grid(row=0, column=0, sticky=NSEW)
