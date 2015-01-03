#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: missingponiesframe.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
try:
    # py3
    from tkinter import Label, Checkbutton, BooleanVar
    from tkinter.constants import N, S, E, W, NSEW
except ImportError:
    # py2
    from Tkinter import Label, Checkbutton, BooleanVar
    from Tkconstants import N, S, E, W, NSEW
from src.scrollframe import ScrollFrame

class MissingPony(object):

    def __init__(self, parent, name, offset):
        self.parent = parent

        self._checked = BooleanVar(self.parent, False)
        self._chkbox = Checkbutton(self.parent,
                                   text="Add {} to inventory".format(name),
                                   variable=self._checked)

        self._chkbox.grid(row=offset, column=0, sticky=W, padx=3, pady=2)

    def grid_remove(self):
        self._chkbox.grid_remove()

    @property
    def checked(self):
        return self._checked.get()

    @checked.setter
    def checked(self, new_val):
        self._checked.set(new_val)


class MissingEverypony(MissingPony):

    def __init__(self, missing_ponies, *args):
        MissingPony.__init__(self, *args)
        self._missing_ponies = missing_ponies
        self._checked.trace("w", self._checked_change)

    def _checked_change(self, *args):
        for pony in self._missing_ponies.values():
            pony.checked = self.checked


class MissingPoniesFrame(ScrollFrame):

    def __init__(self, parent, xml_handle):
        ScrollFrame.__init__(self, parent)
        self._xml_handle = xml_handle
        self._missing_ponies = {}

        Label(self._data_frame).grid(row=1, column=0)
        for n, (ID, name) in enumerate(self._xml_handle.missing_ponies.items()):
            self._missing_ponies[ID] = MissingPony(self._data_frame,
                                                   name, n + 2)
        self._missing_everypony = MissingEverypony(self._missing_ponies, self._data_frame,
                                                   "Everypony", 0)

    def commit(self):
        for ID, pony in self._missing_ponies.items():
            if pony.checked:
                pony.grid_remove()
                self._xml_handle.inventory.append(ID)
                self._xml_handle.missing_ponies.remove(ID)