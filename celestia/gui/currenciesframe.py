#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: currenciesframe.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import six
from collections import defaultdict
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
from celestia.utility.tkvardescriptor import TkVarDescriptor, TkVarDescriptorOwner

@six.add_metaclass(TkVarDescriptorOwner)
class CurrencyFrame(ttk.Frame, object):
    value = TkVarDescriptor(tk.StringVar)

    def __init__(self, parent, text, value, limit, offset):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.value = value

        self._label = ttk.Label(self.parent, text=text)
        self._entry = ttk.Entry(self.parent, textvariable=CurrencyFrame.value.raw_klass(self))
        self._limit = ttk.Label(self.parent, text="(Limit: {})".format(limit))

        options = dict(padx=10, pady=4)
        self._label.grid(row=offset, column=0, sticky=W, **options)
        self._entry.grid(row=offset, column=1, sticky=NSEW, **options)
        self._limit.grid(row=offset, column=2, sticky=NSEW, **options)


class CurrenciesFrame(ttk.Frame):
    def __init__(self, parent, xml_handle):
        ttk.Frame.__init__(self, parent)

        self._xml_handle = xml_handle
        self._currencies = defaultdict(dict)
        n = 0
        for name, typ in xml_handle.currencies.items():
            for cur, val in typ.items():
                self._currencies[name][cur] = CurrencyFrame(self,
                                                            cur,
                                                            val.value,
                                                            val.limit, n)
                n += 1

    def commit(self):
        for name, typ in self._xml_handle.currencies.items():
            for cur, val in typ.items():
                val.value = self._currencies[name][cur].value
