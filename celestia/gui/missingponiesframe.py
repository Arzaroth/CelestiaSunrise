#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: missingponiesframe.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import six
try:
    # py3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import N, S, E, W, NSEW
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import N, S, E, W, NSEW
from .scrolledframe import ScrolledFrame
from celestia.utility.tkvardescriptor import TkVarDescriptor, TkVarDescriptorOwner

@six.add_metaclass(TkVarDescriptorOwner)
class MissingPony(ttk.Frame, object):
    checked = TkVarDescriptor(tk.BooleanVar)

    def __init__(self, parent, name, offset):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.checked = False
        self._chkbox = ttk.Checkbutton(self.parent,
                                       text="Add {} to inventory".format(name),
                                       variable=MissingPony.checked.raw_klass(self))

        self._chkbox.grid(row=offset, column=0, sticky=W, padx=3, pady=2)

    def grid_remove(self):
        self._chkbox.grid_remove()


class MissingEverypony(MissingPony):
    def __init__(self, missing_ponies, *args):
        MissingPony.__init__(self, *args)
        self._missing_ponies = missing_ponies
        MissingPony.checked.raw_klass(self).trace("w", self._checked_change)

    def _checked_change(self, *args):
        for pony in self._missing_ponies.values():
            pony.checked = self.checked


class MissingPoniesFrame(ScrolledFrame):
    def __init__(self, parent, xml_handle):
        ScrolledFrame.__init__(self, parent)
        self._xml_handle = xml_handle
        self._missing_ponies = {}

        ttk.Label(self.interior).grid(row=1, column=0)
        for n, (ID, name) in enumerate(self._xml_handle.missing_ponies.items()):
            self._missing_ponies[ID] = MissingPony(self.interior,
                                                   name, n + 2)
        self._missing_everypony = MissingEverypony(self._missing_ponies, self.interior,
                                                   "Everypony", 0)

    def commit(self):
        for ID, pony in self._missing_ponies.items():
            if pony.checked:
                pony.grid_remove()
                self._xml_handle.inventory.append(ID)
                self._xml_handle.missing_ponies.remove(ID)
