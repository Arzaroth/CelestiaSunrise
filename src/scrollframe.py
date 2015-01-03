#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: scrollframe.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
try:
    # py3
    from tkinter import Frame, Canvas, Scrollbar
    from tkinter.constants import NW, VERTICAL, Y, LEFT, RIGHT, ALL
except ImportError:
    # py2
    from Tkinter import Frame, Canvas, Scrollbar
    from Tkconstants import NW, VERTICAL, Y, LEFT, RIGHT, ALL

class ScrollFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self._canvas = Canvas(self)
        self._data_frame = Frame(self._canvas)

        self._scrollb = Scrollbar(self, orient=VERTICAL, command=self._canvas.yview)
        self._scrollb.pack(side=RIGHT, fill=Y)

        self._canvas.configure(yscrollcommand=self._scrollb.set)
        self._canvas.pack(side=LEFT)
        self._canvas.create_window((0, 0), window=self._data_frame,
                                   anchor=NW, tags="self._data_frame")

        self._data_frame.bind('<Configure>', self._scroll_func)

    def _scroll_func(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox(ALL),
                               height=500,
                               width=780)
