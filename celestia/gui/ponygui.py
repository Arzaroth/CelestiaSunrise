#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponygui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals, division

import binascii
try:
    # py3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import N, S, E, W, NSEW, HORIZONTAL
    from tkinter.constants import BOTH, X, Y
    from tkinter.constants import TOP, BOTTOM, RIGHT, LEFT
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    from tkinter.messagebox import showerror
    from queue import Queue
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import N, S, E, W, NSEW, HORIZONTAL
    from Tkconstants import BOTH, X, Y
    from Tkconstants import TOP, BOTTOM, RIGHT, LEFT
    from tkFileDialog import askopenfilename, asksaveasfilename
    from tkMessageBox import showerror
    from Queue import Queue
from .basegui import BaseGui
from .missingponiesframe import MissingPoniesFrame
from .currenciesframe import CurrenciesFrame
from .poniesframe import PoniesFrame
from .zonesframe import ZonesFrame
from .threaded import ThreadedLoad, ThreadedSave
from .threaded import process_queue
from .dialogs import LoadingDialog

class PonyGui(BaseGui):
    def __init__(self, *args):
        BaseGui.__init__(self, *args)
        self.loaded = False
        self.withdraw()
        self._load_xml()

    def _unload(self):
        self.loaded = False
        self.destroy()

    def _load_xml(self):
        loadingbox = LoadingDialog(self, False)
        queue = Queue()
        thread = ThreadedLoad(queue=queue,
                              savedata=self.savedata)
        thread.start()

        def success_callback(res):
            self.loaded = True
            self._save_manager = res["save_manager"]
            self.save_number = res["save_number"]
            self._xml_handle = res["xml_handle"]
            BaseGui.init(self)
            self.deiconify()
            self.update_idletasks()

        self.after(100, process_queue,
                   self, queue, loadingbox,
                   success_callback, self._unload)

    def _export_xml(self):
        filename = asksaveasfilename()
        if filename:
            loadingbox = LoadingDialog(self)
            queue = Queue()
            thread = ThreadedSave(queue=queue,
                                  savedata=self.savedata,
                                  xml_handle=self._xml_handle,
                                  save_manager=self._save_manager,
                                  save_number=self.save_number,
                                  xml=filename)
            thread.start()

            self.after(100, process_queue,
                       self, queue, loadingbox)

    def _import_xml(self):
        filename = askopenfilename()
        if filename:
            self.withdraw()
            loadingbox = LoadingDialog(self, False)
            queue = Queue()
            thread = ThreadedLoad(queue=queue,
                                  savedata=self.savedata,
                                  xml=filename)
            thread.start()

            def success_callback(res):
                self._xml_handle = res["xml_handle"]
                BaseGui.reinit(self)
                self.deiconify()
                self.update_idletasks()

            self.after(100, process_queue,
                       self, queue, loadingbox,
                       success_callback)

    def _remove_frames(self):
        BaseGui._remove_frames(self)
        self._file_frame.grid_forget()
        self._key_frame.grid_forget()
        self._notebook.grid_forget()

    def _remove_widgets(self):
        BaseGui._remove_widgets(self)
        self._save_button.grid_forget()

    def _create_widgets(self):
        BaseGui._create_widgets(self)
        self._filemenu.add_command(label="Open another file", command=self._unload)
        self._filemenu.add_separator()
        self._filemenu.add_command(label="Exit", command=self.destroy)
        self._editmenu.add_command(label="Export XML...", command=self._export_xml)
        self._editmenu.add_command(label="Import XML...", command=self._import_xml)
        self._editmenu.add_separator()
        self._editmenu.add_command(label="Preferences", command=self._preferences_popup)

    def _create_frames(self):
        BaseGui._create_frames(self)
        self._notebook = ttk.Notebook(self._main_frame)
        self._currencies_frame = CurrenciesFrame(self._main_frame,
                                                 self._xml_handle)
        self._zones_frame = ZonesFrame(self._main_frame,
                                       self._xml_handle)
        self._ponies_frame = PoniesFrame(self._main_frame,
                                         self._xml_handle)
        self._missing_ponies_frame = MissingPoniesFrame(self._main_frame,
                                                        self._xml_handle)
        self._notebook.add(self._currencies_frame,
                           text="Currencies")
        self._notebook.add(self._ponies_frame,
                           text="Ponies")
        self._notebook.add(self._zones_frame,
                           text="Zones")
        self._notebook.add(self._missing_ponies_frame,
                           text="Missing ponies")
        self._save_button = ttk.Button(self._main_frame,
                                       text="Save to file",
                                       command=self._save)

    def _grid_frames(self):
        BaseGui._grid_frames(self)
        self._file_frame.grid(row=0, column=0, pady=5, sticky=NSEW)
        self._key_frame.grid(row=1, column=0, pady=10, sticky=NSEW)
        self._notebook.grid(row=3, column=0, sticky=NSEW)

    def _grid_widgets(self):
        BaseGui._grid_widgets(self)
        self._save_button.grid(row=2, column=0, sticky=NSEW, padx=3, pady=4)

    def _commit(self):
        self._currencies_frame.commit()
        self._ponies_frame.commit()
        self._zones_frame.commit()
        self._missing_ponies_frame.commit()

    def _save(self):
        loadingbox = LoadingDialog(self)
        queue = Queue()
        try:
            self._commit()
        except Exception as e:
            loadingbox.destroy()
            showerror("Error", str(e))
        else:
            thread = ThreadedSave(queue=queue,
                                  savedata=self.savedata,
                                  xml_handle=self._xml_handle,
                                  save_manager=self._save_manager,
                                  save_number=self.save_number)
            thread.start()

            self.after(100, process_queue,
                       self, queue, loadingbox)
