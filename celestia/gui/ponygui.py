#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponygui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import binascii
import sys
import requests
try:
    # py3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import N, S, E, W, NSEW, HORIZONTAL, BOTH
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    from tkinter.messagebox import showerror, showinfo
    from queue import Queue
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import N, S, E, W, NSEW, HORIZONTAL, BOTH
    from tkFileDialog import askopenfilename, asksaveasfilename
    from tkMessageBox import showerror, showinfo
    from Queue import Queue
from .basegui import BaseGui
from .missingponiesframe import MissingPoniesFrame
from .currenciesframe import CurrenciesFrame
from .poniesframe import PoniesFrame
from .zonesframe import ZonesFrame
from .threaded import ThreadedLoad
from .threaded import process_loadqueue
from celestia.save import decompress_data, compress_data
from celestia.utility.gluid import retrieve_gluid
from celestia.utility.update import check_version

class LoadingDialog(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.transient()
        self.title("Loading...")
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill=BOTH)
        self.label = ttk.Label(frame, text="Loading...", font=20)
        self.pb = ttk.Progressbar(frame, mode="indeterminate", length=200, orient=HORIZONTAL)
        self.label.pack(padx=10, pady=10)
        self.pb.pack(padx=10, pady=10)
        self.pb.start()


class PonyGui(BaseGui):
    def __init__(self, savedata):
        BaseGui.__init__(self, savedata)
        self.loaded = False
        self.withdraw()
        self._load_xml()

    def _load_xml(self):
        loadingbox = LoadingDialog(self)
        queue = Queue()
        ThreadedLoad(queue,
                     self.savedata).start()

        def error_callback():
            self.destroy()

        def success_callback(res):
            self.loaded = True
            self._save_manager = res["save_manager"]
            self.save_number = res["save_number"]
            self._xml_handle = res["xml_handle"]
            BaseGui.init(self)
            self.deiconify()
            self.update_idletasks()
        self.after(100, process_loadqueue,
                   self, loadingbox, queue,
                   success_callback, error_callback)

    def _unload(self):
        self.loaded = False
        self.destroy()

    def _export_xml(self):
        filename = asksaveasfilename()
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self._xml_handle.prettify())
            except Exception as e:
                showerror("Error",
                          "Was unable to write to file, reason: {}".format(str(e)))

    def _import_xml(self):
        filename = askopenfilename()
        if filename:
            self.withdraw()
            loadingbox = LoadingDialog(self)
            queue = Queue()
            ThreadedLoad(queue,
                         self.savedata,
                         filename).start()

            def success_callback(res):
                self._xml_handle = res["xml_handle"]
                BaseGui.reinit(self)
                self.deiconify()
                self.update_idletasks()
            self.after(100, process_loadqueue,
                       self, loadingbox, queue,
                       success_callback)

    def _check_update(self):
        ver = check_version()
        if ver["error"]:
            showerror("Error", ver["error"])
        elif ver["up_to_date"]:
            showinfo("Up to date", "You're running the latest version")
        else:
            pass

    def _about_popup(self):
        from __main__ import INTRO, AUTHOR
        showinfo("About",
                 """{intro}
                 {author}""".format(intro=INTRO, author=AUTHOR))

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
        self._menu = tk.Menu(self)
        self._filemenu = tk.Menu(self)
        self._filemenu.add_command(label="Open another file", command=self._unload)
        self._filemenu.add_separator()
        self._filemenu.add_command(label="Export XML...", command=self._export_xml)
        self._filemenu.add_command(label="Import XML...", command=self._import_xml)
        self._menu.add_cascade(label="File", menu=self._filemenu)
        self._aboutmenu = tk.Menu(self)
        self._aboutmenu.add_command(label="Check for update", command=self._check_update)
        self._aboutmenu.add_separator()
        self._aboutmenu.add_command(label="About", command=self._about_popup)
        self._menu.add_cascade(label="About", menu=self._aboutmenu)
        self.config(menu=self._menu)

    def _create_frames(self):
        BaseGui._create_frames(self)
        self._notebook = ttk.Notebook(self)
        self._currencies_frame = CurrenciesFrame(self, self._xml_handle)
        self._zones_frame = ZonesFrame(self, self._xml_handle)
        self._ponies_frame = PoniesFrame(self, self._xml_handle)
        self._missing_ponies_frame = MissingPoniesFrame(self, self._xml_handle)
        self._notebook.add(self._currencies_frame,
                           text="Currencies")
        self._notebook.add(self._ponies_frame,
                           text="Ponies")
        self._notebook.add(self._zones_frame,
                           text="Zones")
        self._notebook.add(self._missing_ponies_frame,
                           text="Missing ponies")
        self._save_button = ttk.Button(self,
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

    def _save(self):
        try:
            if not self.legacy:
                gluid = retrieve_gluid(self.dbfile) if self.usedb else self.gluid
                gluid = binascii.a2b_base64(gluid)
            else:
                gluid = b''
        except:
            showerror("Error", "Bad encryption key")
        else:
            loadingbox = LoadingDialog(self)
            try:
                self._currencies_frame.commit()
                self._ponies_frame.commit()
                self._zones_frame.commit()
                self._missing_ponies_frame.commit()
                try:
                    data = self._xml_handle.to_string().encode('utf-8')
                except UnicodeDecodeError:
                    data = self._xml_handle.to_string()
                self._save_manager.save(compress_data(data),
                                        self.savefile,
                                        self.save_number,
                                        gluid,
                                        self.legacy)
            except Exception as e:
                showerror("Error",
                          "Was unable to write to file, reason: {}".format(str(e)))
            finally:
                loadingbox.destroy()
