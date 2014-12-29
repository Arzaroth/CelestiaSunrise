#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: currenciesframe.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
from collections import defaultdict
try:
    # py3
    from tkinter import Label, Entry, Frame, StringVar
    from tkinter.constants import N, S, E, W, NSEW
except ImportError:
    # py2
    from Tkinter import Label, Entry, Frame, StringVar
    from Tkconstants import N, S, E, W, NSEW

class CurrencyFrame(object):

    def __init__(self, parent, text, value, offset):
        self.parent = parent

        self._value = StringVar(self.parent, value)

        self._label = Label(self.parent, text=text)
        self._entry = Entry(self.parent, textvariable=self._value)

        options = dict(padx=10, pady=4)
        self._label.grid(row=offset, column=0, sticky=W, **options)
        self._entry.grid(row=offset, column=1, sticky=E, **options)

    @property
    def value(self):
        return self._value.get()


class CurrenciesFrame(Frame):

    def __init__(self, parent, xml_handle):
        Frame.__init__(self, parent)

        self._xml_handle = xml_handle
        self._currencies = defaultdict(dict)
        n = 0
        for name, typ in xml_handle.currencies.items():
            for cur, val in typ.items():
                self._currencies[name][cur] = CurrencyFrame(self, cur, val.value, n)
                n += 1

    def commit(self):
        for name, typ in self._xml_handle.currencies.items():
            for cur, val in typ.items():
                val.value = self._currencies[name][cur].value
