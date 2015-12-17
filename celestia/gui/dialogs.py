#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: dialogs.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals, division

import six
try:
    # py3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import N, S, E, W, NSEW, HORIZONTAL
    from tkinter.constants import BOTH, X, Y
    from tkinter.constants import TOP, BOTTOM, RIGHT, LEFT
    from tkinter.filedialog import asksaveasfilename
    from queue import Queue
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import N, S, E, W, NSEW, HORIZONTAL
    from Tkconstants import BOTH, X, Y
    from Tkconstants import TOP, BOTTOM, RIGHT, LEFT
    from tkFileDialog import asksaveasfilename
    from Queue import Queue
try:
    from celestia.utility.monotonic import monotonic
except RuntimeError:
    # no suitable implementation of monotonic for this system
    # using time.time() instead
    from time import time as monotonic
from .threaded import ThreadedVersionDownload
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
        try:
            kbps = self.current / (monotonic() - self.start) / 1024
        except ZeroDivisionError:
            kbps = 0
        self.percent = "{:.2f}% ({:.2f} KiB/s)".format(percent, kbps)

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
