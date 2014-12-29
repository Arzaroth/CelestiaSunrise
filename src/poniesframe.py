#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: poniesframe.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
try:
    # py3
    from tkinter import (Frame, Canvas,
                         Label, Scrollbar, Scale, Checkbutton, OptionMenu,
                         IntVar, BooleanVar, StringVar)
    from tkinter.constants import (N, S, E, W,
                                   NW, NSEW,
                                   VERTICAL, HORIZONTAL,
                                   Y, LEFT, RIGHT,
                                   ALL,
                                   NORMAL, DISABLED)
except ImportError:
    # py2
    from Tkinter import (Frame, Canvas,
                         Label, Scrollbar, Scale, Checkbutton, OptionMenu,
                         IntVar, BooleanVar, StringVar)
    from Tkconstants import (N, S, E, W,
                             NW, NSEW,
                             VERTICAL, HORIZONTAL,
                             Y, LEFT, RIGHT,
                             ALL,
                             NORMAL, DISABLED)
from src.utility import Pony

class PonyFrame(object):

    def __init__(self, parent,
                 name, level,
                 shards, next_game,
                 offset):
        self.parent = parent

        self._pony_label = Label(self.parent,
                                 text=name)
        self._level = Scale(self.parent,
                            from_=0, to=5,
                            orient=HORIZONTAL,
                            command=self._level_change)
        self._level.set(level)
        self._level_up = BooleanVar(self.parent,
                                    shards == 10)
        self._shards = Checkbutton(self.parent,
                                   variable=self._level_up)
        self._next_game = StringVar(self.parent,
                                    next_game)
        self._option_next = OptionMenu(self.parent,
                                       self._next_game,
                                       Pony.GameTypes.rmap[Pony.GameTypes.Ball],
                                       Pony.GameTypes.rmap[Pony.GameTypes.Apple],
                                       Pony.GameTypes.rmap[Pony.GameTypes.Book])
        self._reset = BooleanVar(self.parent,
                                 False)
        self._reset_checkbox = Checkbutton(self.parent,
                                           variable=self._reset)

        options = dict(padx=16, pady=2)
        self._pony_label.grid(row=offset, column=0, sticky=W, **options)
        self._level.grid(row=offset, column=1, sticky=NSEW, **options)
        self._shards.grid(row=offset, column=2, sticky=NSEW, **options)
        self._option_next.grid(row=offset, column=3, sticky=NSEW, **options)
        self._reset_checkbox.grid(row=offset, column=4, sticky=NSEW, **options)

    def _level_change(self, *args):
        if self.level == 5:
            self._shards.configure(state=DISABLED)
            self.level_up = False
        else:
            self._shards.configure(state=NORMAL)

    @property
    def level(self):
        return int(self._level.get())

    @level.setter
    def level(self, new_val):
        self._level.set(new_val)

    @property
    def level_up(self):
        return self._level_up.get()

    @level_up.setter
    def level_up(self, new_val):
        self._level_up.set(new_val and self.level != 5)

    @property
    def next_game(self):
        return self._next_game.get()

    @next_game.setter
    def next_game(self, new_val):
        self._next_game.set(new_val)

    @property
    def reset_next_game(self):
        return self._reset.get()

    @reset_next_game.setter
    def reset_next_game(self, new_val):
        self._reset.set(new_val)


class EveryponyFrame(PonyFrame):

    def __init__(self, ponies, *args):
        PonyFrame.__init__(self, *args)
        self._ponies = ponies
        self._level_change_first_call = False
        self._level_up.trace("w", self._shards_change)
        self._next_game.trace("w", self._next_game_change)
        self._reset.trace("w", self._reset_change)

    def _level_change(self, *args):
        PonyFrame._level_change(self, *args)
        if self._level_change_first_call:
            for pony in self._ponies.values():
                pony.level = self.level
            self._shards_change(self)
        else:
            self._level_change_first_call = True

    def _shards_change(self, *args):
        for pony in self._ponies.values():
            pony.level_up = self.level_up

    def _next_game_change(self, *args):
        for pony in self._ponies.values():
            pony.next_game = self.next_game

    def _reset_change(self, *args):
        for pony in self._ponies.values():
            pony.reset_next_game = self.reset_next_game


class PoniesFrame(Frame):

    def __init__(self, parent, xml_handle):
        Frame.__init__(self, parent)
        self._canvas = Canvas(self)
        self._ponies_frame = Frame(self._canvas)

        self._scrollb = Scrollbar(self, orient=VERTICAL, command=self._canvas.yview)
        self._scrollb.pack(side=RIGHT, fill=Y)

        self._canvas.configure(yscrollcommand=self._scrollb.set)
        self._canvas.pack(side=LEFT)
        self._canvas.create_window((0, 0), window=self._ponies_frame,
                                   anchor=NW, tags="self._ponies_frame")

        self._ponies_frame.bind('<Configure>', self._scroll_func)

        self._xml_handle = xml_handle

        options = dict(sticky=NSEW, padx=16, pady=2)
        Label(self._ponies_frame, text="Level").grid(row=0, column=1, **options)
        Label(self._ponies_frame, text="Trigger next level").grid(row=0, column=2, **options)
        Label(self._ponies_frame, text="Next minigame").grid(row=0, column=3, **options)
        Label(self._ponies_frame, text="Reset game timer").grid(row=0, column=4, **options)
        self._ponies = {}
        for n, pony in enumerate(self._xml_handle.ponies.values()):
            self._ponies[pony.ID] = PonyFrame(self._ponies_frame,
                                              pony.name, pony.level,
                                              pony.shards, pony.next_game,
                                              n + 2)
        self._everypony = EveryponyFrame(self._ponies, self._ponies_frame,
                                         "Everypony", 0,
                                         0, Pony.GameTypes.rmap[Pony.GameTypes.Ball],
                                         1)

    def _scroll_func(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox(ALL),
                               height=500,
                               width=700)

    def commit(self):
        for pony in self._xml_handle.ponies.values():
            pony.level = self._ponies[pony.ID].level
            pony.shards = 10 if self._ponies[pony.ID].level_up else 0
            pony.next_game = Pony.GameTypes.map[self._ponies[pony.ID].next_game]
            if self._ponies[pony.ID].reset_next_game:
                pony.reset_game_timer()
