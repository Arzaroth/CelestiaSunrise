#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: poniesframe.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import six
try:
    # py3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import (N, S, E, W,
                                   NSEW,
                                   HORIZONTAL,
                                   NORMAL, DISABLED)
except ImportError:
    # py2
    import Tkinter as tk
    import ttk
    from Tkconstants import (N, S, E, W,
                             NSEW,
                             HORIZONTAL,
                             NORMAL, DISABLED)
from .scrolledframe import ScrolledFrame
from celestia.utility.utility import Pony
from celestia.utility.tkvardescriptor import TkVarDescriptor, TkVarDescriptorOwner

@six.add_metaclass(TkVarDescriptorOwner)
class PonyFrame(ttk.Frame, object):
    level = TkVarDescriptor(tk.IntVar)
    level_up = TkVarDescriptor(tk.BooleanVar)
    next_game = TkVarDescriptor(tk.StringVar)
    reset_next_game = TkVarDescriptor(tk.BooleanVar)

    def __init__(self, parent,
                 name, level,
                 shards, next_game,
                 offset):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self._pony_label = ttk.Label(self.parent,
                                     text=name)
        self.level = level
        self._level_frame = ttk.Frame(self.parent)
        self._level_label = ttk.Label(self._level_frame,
                                      text=self.level)
        self._level_scale = ttk.Scale(self._level_frame,
                                      from_=0, to=5,
                                      orient=HORIZONTAL,
                                      variable=PonyFrame.level.raw_klass(self))
        PonyFrame.level.raw_klass(self).trace("w", self._level_change)
        self.level_up = shards == 10 and self.level != 5
        self._shards = ttk.Checkbutton(self.parent,
                                       state=(DISABLED if self.level == 5 else NORMAL),
                                       variable=PonyFrame.level_up.raw_klass(self))
        self.next_game = next_game
        self._option_next = ttk.OptionMenu(self.parent,
                                           PonyFrame.next_game.raw_klass(self),
                                           Pony.GameTypes.rmap[Pony.GameTypes.Ball],
                                           Pony.GameTypes.rmap[Pony.GameTypes.Apple],
                                           Pony.GameTypes.rmap[Pony.GameTypes.Book])
        self.reset_next_game = False
        self._reset_checkbox = ttk.Checkbutton(self.parent,
                                               variable=PonyFrame.reset_next_game.raw_klass(self))

        options = dict(padx=16, pady=2)
        self._pony_label.grid(row=offset, column=0, sticky=W, **options)
        self._level_frame.grid(row=offset, column=1, **options)
        self._level_label.grid(row=0, column=0)
        self._level_scale.grid(row=1, column=0)
        self._shards.grid(row=offset, column=2, **options)
        self._option_next.grid(row=offset, column=3, **options)
        self._reset_checkbox.grid(row=offset, column=4, **options)

    def _level_change(self, *args):
        self._shards.configure(state=(DISABLED if self.level == 5 else NORMAL))
        self.level_up = self.level_up and self.level != 5
        self._level_label.config(text=self.level)


class EveryponyFrame(PonyFrame):
    def __init__(self, ponies, *args):
        PonyFrame.__init__(self, *args)
        self._ponies = ponies
        EveryponyFrame.level_up.raw_klass(self).trace("w", self._shards_change)
        EveryponyFrame.next_game.raw_klass(self).trace("w", self._next_game_change)
        EveryponyFrame.reset_next_game.raw_klass(self).trace("w", self._reset_change)

    def _level_change(self, *args):
        PonyFrame._level_change(self, *args)
        for pony in self._ponies.values():
            pony.level = self.level
        self._shards_change(self)

    def _shards_change(self, *args):
        for pony in self._ponies.values():
            pony.level_up = self.level_up and pony.level != 5

    def _next_game_change(self, *args):
        for pony in self._ponies.values():
            pony.next_game = self.next_game

    def _reset_change(self, *args):
        for pony in self._ponies.values():
            pony.reset_next_game = self.reset_next_game


class PoniesFrame(ScrolledFrame):
    def __init__(self, parent, xml_handle):
        ScrolledFrame.__init__(self, parent)
        self._xml_handle = xml_handle

        options = dict(padx=16, pady=2)
        ttk.Label(self.interior, text="Level").grid(row=0, column=1, **options)
        ttk.Label(self.interior, text="Trigger next level").grid(row=0, column=2, **options)
        ttk.Label(self.interior, text="Next minigame").grid(row=0, column=3, **options)
        ttk.Label(self.interior, text="Reset game timer").grid(row=0, column=4, **options)
        self._ponies = {}
        for n, pony in enumerate(self._xml_handle.ponies.values()):
            self._ponies[pony.ID] = PonyFrame(self.interior,
                                              pony.name, pony.level,
                                              pony.shards, pony.next_game,
                                              n + 2)
        self._everypony = EveryponyFrame(self._ponies, self.interior,
                                         "Everypony", 0,
                                         0, Pony.GameTypes.rmap[Pony.GameTypes.Ball],
                                         1)

    def commit(self):
        for pony in self._xml_handle.ponies.values():
            pony.level = self._ponies[pony.ID].level
            pony.shards = 10 if self._ponies[pony.ID].level_up else 0
            pony.next_game = Pony.GameTypes.map[self._ponies[pony.ID].next_game]
            if self._ponies[pony.ID].reset_next_game:
                pony.reset_game_timer()
