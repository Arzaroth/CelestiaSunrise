#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: dialogs.py
# by Arzaroth Lekva
# lekva@arzaroth.com
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
    from tkinter.messagebox import askyesno, showinfo
    from tkinter.filedialog import asksaveasfilename
    from tkinter.font import Font
    from queue import Queue
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import N, S, E, W, NSEW, HORIZONTAL
    from Tkconstants import BOTH, X, Y
    from Tkconstants import TOP, BOTTOM, RIGHT, LEFT
    from tkMessageBox import askyesno, showinfo
    from tkFileDialog import asksaveasfilename
    from tkFont import Font
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
from celestia.utility.config import Config

class BaseDiablog(tk.Toplevel, object):
    def __init__(self, master, title, exit_on_esc=False, transient=True):
        tk.Toplevel.__init__(self, master)
        self.master = master
        if transient:
            self.transient(master)
            self.grab_set()
        else:
            self.transient()
        self.title(title)
        if exit_on_esc:
            self.bind('<Escape>', lambda _: self.destroy())
        self.body = ttk.Frame(self)
        self.body.pack(fill=BOTH, expand=True)


class LoadingDialog(BaseDiablog):
    def __init__(self, master, transient=True):
        BaseDiablog.__init__(self, master, "Loading...", transient=transient)
        self.protocol('WM_DELETE_WINDOW', lambda *args: None)
        self.label = ttk.Label(self.body, text="Loading...", font=20)
        self.pb = ttk.Progressbar(self.body, mode="indeterminate", length=200, orient=HORIZONTAL)
        options = dict(padx=7, pady=7)
        self.label.pack(**options)
        self.pb.pack(**options)
        self.pb.start()


@six.add_metaclass(TkVarDescriptorOwner)
class PreferencesDialog(BaseDiablog):
    startup_check = TkVarDescriptor(tk.BooleanVar)

    def __init__(self, master):
        BaseDiablog.__init__(self, master, "Preferences", exit_on_esc=True)
        self.startup_check = Config.config["startup_check"]
        self.general_label = ttk.Label(self.body,
                                       text="General")
        font = Font(self.general_label, self.general_label.cget("font"))
        font.configure(underline=True)
        self.general_label.configure(font=font)
        self.config_frame = ttk.Frame(self)
        self.startup_check_checkbtn = ttk.Checkbutton(self.config_frame,
                                                      text="Check for update at launch",
                                                      variable=PreferencesDialog.startup_check.raw_klass(self),
                                                      command=self._startup_check_clicked)
        self.buttons_frame = ttk.Frame(self)
        self.close_button = ttk.Button(self.buttons_frame,
                                       text="Close",
                                       command=self.destroy)
        options = dict(padx=5, pady=5)
        self.general_label.pack(side=LEFT, **options)
        self.config_frame.pack(fill=BOTH, expand=True, **options)
        self.startup_check_checkbtn.pack(side=LEFT, **options)
        self.buttons_frame.pack(side=BOTTOM, fill=BOTH, expand=True, **options)
        self.close_button.pack(side=RIGHT, expand=False)

    def _startup_check_clicked(self):
        Config.config["startup_check"] = self.startup_check
        Config.commit()


@six.add_metaclass(TkVarDescriptorOwner)
class DownloadDialog(BaseDiablog):
    percent = TkVarDescriptor(tk.StringVar)
    cancel = TkVarDescriptor(tk.BooleanVar)

    def __init__(self, master):
        BaseDiablog.__init__(self, master, "Downloading...")
        self.protocol('WM_DELETE_WINDOW', lambda *args: None)
        self._curbytes = 0
        self._maxbytes = 0
        self.start = monotonic()
        self.update_percent()
        self.cancel = False

        self.label = ttk.Label(self.body,
                               text="The new version is currently downloading, please wait...",
                               font=20)
        self.progressframe = ttk.Frame(self.body)
        self.pb = ttk.Progressbar(self.progressframe,
                                  mode="determinate",
                                  length=250,
                                  orient=HORIZONTAL)
        self.pblabel = ttk.Label(self.progressframe,
                                 textvariable=DownloadDialog.percent.raw_klass(self))
        self.cancel_button = ttk.Button(self.body,
                                        text="Cancel",
                                        command=lambda: DownloadDialog.cancel.__set__(self, True))

        options = dict(padx=3, pady=4)
        self.label.pack(side=TOP, fill=X, expand=False, **options)
        self.cancel_button.pack(side=BOTTOM, expand=False, **options)
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


class NewVersionDialog(object):
    def __init__(self, download_url, master, *args, **kwargs):
        self.download_url = download_url
        self.master = master
        if askyesno("New version!", "A new version is available!\nDo you wish to download it?"):
            self.download()

    def download(self):
        filename = asksaveasfilename(initialfile="CelestiaSunrise.exe")
        if filename:
            downloadbox = DownloadDialog(self.master)
            progress_queue = Queue()
            cancel_queue = Queue()
            thread = ThreadedVersionDownload(progress_queue, self.download_url,
                                             filename, cancel_queue)
            thread.start()

            def process_callback(res):
                if downloadbox.cancel:
                    cancel_queue.put(True)
                downloadbox.total = res["total"]
                downloadbox.current = res["current"]

            def success_callback(res):
                showinfo("Success", "The latest version has been successfully downloaded")

            self.master.after(100, process_queue,
                              self.master, progress_queue, downloadbox,
                              success_callback, None,
                              process_callback)
