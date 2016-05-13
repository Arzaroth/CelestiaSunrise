#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: playerframe.py
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
from celestia.gui.currenciesframe import CurrencyFrame
from celestia.utility.tkvardescriptor import TkVarDescriptor, TkVarDescriptorOwner

@six.add_metaclass(TkVarDescriptorOwner)
class PlayerFrame(ttk.Frame, object):
    complete_quests = TkVarDescriptor(tk.BooleanVar)

    def __init__(self, parent, xml_handle):
        ttk.Frame.__init__(self, parent, height=400)
        self.grid_propagate(0)

        self._xml_handle = xml_handle
        self._player_infos = {}
        for n, (name, typ) in enumerate(xml_handle.player_infos.items()):
            self._player_infos[name] = CurrencyFrame(self, name, typ.value,
                                                     typ.limit, n)
        self.complete_quests = False
        self._quests_box = ttk.Checkbutton(self,
                                           text="Complete current quests",
                                           variable=PlayerFrame.complete_quests.raw_klass(self))
        self._quests_box.grid(row=(n + 1), column=0, sticky=W, padx=3, pady=2)

    def commit(self):
        for name, typ in self._xml_handle.player_infos.items():
            typ.value = self._player_infos[name].value
        if self.complete_quests:
            for quest in self._xml_handle.quests:
                quest.complete()
