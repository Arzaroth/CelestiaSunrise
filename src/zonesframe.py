#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: zonesframe.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from tkinter import Frame, Checkbutton, BooleanVar, StringVar
from tkinter.constants import N, S, E, W, NSEW

class ZoneFrame(object):

    def __init__(self, parent, zone, offset):
        self.parent = parent
        self.zone = zone

        self._clearables_checked = BooleanVar(self.parent, False)
        self._foes_checked = BooleanVar(self.parent, False)
        self._clearables_text = StringVar(self.parent)
        self._foes_text = StringVar(self.parent)
        self.update()
        self._clearables_box = Checkbutton(self.parent,
                                           textvariable=self._clearables_text,
                                           variable=self._clearables_checked)
        self._foes_box = Checkbutton(self.parent,
                                     textvariable=self._foes_text,
                                     variable=self._foes_checked)

        options = dict(sticky=W, padx=3, pady=2)
        self._clearables_box.grid(row=(offset * 2), column=0, **options)
        self._foes_box.grid(row=(offset * 2) + 1, column=0, **options)


    def update(self):
        self._clearables_text.set("Remove Clearables Objects from {} ({} remaining)"
                                  .format(self.zone.name,
                                          len(self.zone.clearable_items)))
        self._foes_text.set("Remove {} from {} ({} remaining)"
                            .format(self.zone.foes.name,
                                    self.zone.name,
                                    len(self.zone.foes)))

    @property
    def clearables_checked(self):
        return self._clearables_checked.get()

    @property
    def foes_checked(self):
        return self._foes_checked.get()


class ZonesFrame(Frame):

    def __init__(self, parent, xml_handle):
        super(ZonesFrame, self).__init__(parent)

        self._xml_handle = xml_handle
        self._zones = {}
        for n, (ID, zone) in enumerate(self._xml_handle.zones.items()):
            self._zones[ID] = ZoneFrame(self, zone, n)

    def commit(self):
        for ID, zone in self._xml_handle.zones.items():
            if self._zones[ID].clearables_checked:
                zone.clearable_items.clear()
            if self._zones[ID].foes_checked:
                zone.foes.clear()
            self._zones[ID].update()
