#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponygui.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals, division

import binascii
import six
try:
    # py3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import N, S, E, W, NSEW, HORIZONTAL
    from tkinter.constants import BOTH, X, Y
    from tkinter.constants import TOP, BOTTOM, RIGHT, LEFT
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    from tkinter.messagebox import showinfo
    from queue import Queue
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import N, S, E, W, NSEW, HORIZONTAL
    from Tkconstants import BOTH, X, Y
    from Tkconstants import TOP, BOTTOM, RIGHT, LEFT
    from tkFileDialog import askopenfilename, asksaveasfilename
    from tkMessageBox import showinfo
    from Queue import Queue
try:
    from celestia.utility.monotonic import monotonic
except RuntimeError:
    # no suitable implementation of monotonic for this system
    # using time.time() instead
    from time import time as monotonic
from .basegui import BaseGui
from .missingponiesframe import MissingPoniesFrame
from .currenciesframe import CurrenciesFrame
from .poniesframe import PoniesFrame
from .zonesframe import ZonesFrame
from .threaded import ThreadedLoad, ThreadedSave, ThreadedVersionCheck, ThreadedVersionDownload
from .threaded import process_queue
from celestia.utility.tkvardescriptor import TkVarDescriptor, TkVarDescriptorOwner

class LoadingDialog(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.transient()
        self.title("Loading...")
        self.bind('<Escape>', lambda _: self.destroy())

        frame = ttk.Frame(self)
        frame.pack(expand=True, fill=BOTH)
        self.label = ttk.Label(frame, text="Loading...", font=20)
        self.pb = ttk.Progressbar(frame, mode="indeterminate", length=200, orient=HORIZONTAL)
        self.label.pack(padx=10, pady=10)
        self.pb.pack(padx=10, pady=10)
        self.pb.start()


@six.add_metaclass(TkVarDescriptorOwner)
class DownloadDialog(tk.Toplevel, object):
    percent = TkVarDescriptor(tk.StringVar)

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.transient()
        self.title("Downloading...")
        self.protocol('WM_DELETE_WINDOW', lambda *args: None)
        self._curbytes = 0
        self._maxbytes = 0
        self.start = monotonic()
        self.update_percent()

        self.mainframe = ttk.Frame(self)
        self.mainframe.pack(side=TOP, fill=BOTH, expand=True)

        self.label = ttk.Label(self.mainframe,
                               text="The new version is currently downloading, please wait...",
                               font=20)
        self.progressframe = ttk.Frame(self.mainframe)
        self.pb = ttk.Progressbar(self.progressframe,
                                  mode="determinate",
                                  length=200,
                                  orient=HORIZONTAL)
        self.pblabel = ttk.Label(self.progressframe,
                                 textvariable=DownloadDialog.percent.raw_klass(self))

        options = dict(padx=3, pady=4)
        self.label.pack(side=TOP, fill=X, expand=False, **options)
        self.progressframe.pack(side=BOTTOM, fill=BOTH, expand=True, **options)
        self.pb.pack(side=LEFT, **options)
        self.pblabel.pack(side=LEFT, **options)

    def update_percent(self):
        try:
            percent = (self.current / self.total) * 100
        except ZeroDivisionError:
            percent = 0
        self.percent = "{:.2f}% ({:.2f} KiB/s)".format(percent,
                                                       self.current /
                                                       (monotonic() - self.start) /
                                                       1024)

    @property
    def total(self):
        return self._maxbytes

    @total.setter
    def total(self, value):
        self._maxbytes = int(value)
        self.pb["maximum"] = self._maxbytes
        self.update_percent()

    @property
    def current(self):
        return self._curbytes

    @current.setter
    def current(self, value):
        self._curbytes = int(value)
        self.pb["value"] = self._curbytes
        self.update_percent()


class RestartDialog(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.transient()
        self.title("Success")
        self.bind('<Escape>', lambda _: self.destroy())

        frame = ttk.Frame(self)
        frame.pack(expand=True, fill=BOTH)
        self.label = ttk.Label(frame,
                               text="The most recent version has successfully been downloaded",
                               font=16)
        self.button = ttk.Button(frame, text="Ok", command=self.destroy)
        self.label.pack(padx=10, pady=10)
        self.button.pack(padx=10, pady=10)


class NewVersionDialog(tk.Toplevel):
    def __init__(self, download_url, master, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.download_url = download_url
        self.transient()
        self.title("New version!")
        self.bind('<Escape>', lambda _: self.destroy())

        self.mainframe = ttk.Frame(self)
        self.mainframe.pack(side=TOP, fill=BOTH, expand=True)

        self.label = ttk.Label(self.mainframe,
                               text="A new version is avaible! Do you wish to download it?",
                               font=16)
        self.buttonframe = ttk.Frame(self.mainframe)
        self.okbuttonframe = ttk.Frame(self.buttonframe)
        self.nobuttonframe = ttk.Frame(self.buttonframe)
        self.okbutton = ttk.Button(self.okbuttonframe, text="Yes", command=self.download)
        self.nobutton = ttk.Button(self.nobuttonframe, text="No", command=self.destroy)

        options = dict(padx=3, pady=4)
        self.label.pack(side=TOP, fill=X, expand=False, **options)
        self.buttonframe.pack(side=BOTTOM, fill=BOTH, expand=True, **options)
        self.okbuttonframe.pack(side=LEFT, fill=X, expand=True, **options)
        self.nobuttonframe.pack(side=RIGHT, fill=X, expand=True, **options)
        self.okbutton.pack(side=RIGHT)
        self.nobutton.pack(side=LEFT)

    def download(self):
        filename = asksaveasfilename(initialfile="CelestiaSunrise.exe")
        if filename:
            downloadbox = DownloadDialog()
            queue = Queue()
            thread = ThreadedVersionDownload(queue, self.download_url, filename)
            thread.start()

            def process_callback(res):
                downloadbox.total = res["total"]
                downloadbox.current = res["current"]

            def success_callback(res):
                RestartDialog()

            self.master.after(100, process_queue,
                              self.master, downloadbox, queue,
                              success_callback, None,
                              process_callback)
        self.destroy()


class PonyGui(BaseGui):
    def __init__(self, savedata):
        BaseGui.__init__(self, savedata)
        self.loaded = False
        self.withdraw()
        self._load_xml()
        self.mainloop()

    def _load_xml(self):
        loadingbox = LoadingDialog(self)
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
                   self, loadingbox, queue,
                   success_callback, self._unload)

    def _unload(self):
        self.loaded = False
        self.destroy()

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
                       self, loadingbox, queue)

    def _import_xml(self):
        filename = askopenfilename()
        if filename:
            self.withdraw()
            loadingbox = LoadingDialog(self)
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
                       self, loadingbox, queue,
                       success_callback)

    def _check_update(self):
        loadingbox = LoadingDialog(self)
        queue = Queue()
        thread = ThreadedVersionCheck(queue=queue)
        thread.start()

        def success_callback(res):
            if res["up_to_date"]:
                showinfo("Up to date", "You're running the latest version")
            else:
                NewVersionDialog(res["download_url"], self)

        self.after(100, process_queue,
                   self, loadingbox, queue,
                   success_callback)

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
        self._commit()
        thread = ThreadedSave(queue=queue,
                              savedata=self.savedata,
                              xml_handle=self._xml_handle,
                              save_manager=self._save_manager,
                              save_number=self.save_number)
        thread.start()

        self.after(100, process_queue,
                   self, loadingbox, queue)
