#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: zonesframe.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
try:
    # py3
    from tkinter import Frame, Checkbutton, Label, BooleanVar, StringVar
    from tkinter.constants import N, S, E, W, NSEW
except ImportError:
    # py2
    from Tkinter import Frame, Checkbutton, Label, BooleanVar, StringVar
    from Tkconstants import N, S, E, W, NSEW
from src.utility.tkvardescriptor import TkVarDescriptor, TkVarDescriptorOwner
import six

@six.add_metaclass(TkVarDescriptorOwner)
class ZoneFrame(Frame, object):
    clearables_checked = TkVarDescriptor(BooleanVar)
    foes_checked = TkVarDescriptor(BooleanVar)
    reset_checked = TkVarDescriptor(BooleanVar)
    clearables_text = TkVarDescriptor(StringVar)
    foes_text = TkVarDescriptor(StringVar)
    reset_text = TkVarDescriptor(StringVar)

    def __init__(self, parent, zone, offset, reset_offset):
        Frame.__init__(self, parent)
        self.parent = parent
        self.zone = zone

        self.clearables_checked = False
        self.foes_checked = False
        self.reset_checked = False
        self.update()
        self._clearables_box = Checkbutton(self.parent,
                                           textvariable=ZoneFrame.clearables_text.raw_klass(self),
                                           variable=ZoneFrame.clearables_checked.raw_klass(self))
        self._foes_box = Checkbutton(self.parent,
                                     textvariable=ZoneFrame.foes_text.raw_klass(self),
                                     variable=ZoneFrame.foes_checked.raw_klass(self))
        self._reset_box = Checkbutton(self.parent,
                                      textvariable=ZoneFrame.reset_text.raw_klass(self),
                                      variable=ZoneFrame.reset_checked.raw_klass(self))

        options = dict(sticky=W, padx=3, pady=2)
        self._clearables_box.grid(row=(offset * 2), column=0, **options)
        self._foes_box.grid(row=(offset * 2) + 1, column=0, **options)
        self._reset_box.grid(row=reset_offset + offset, column=0, **options)

    def update(self):
        self.clearables_text = ("Remove Clearables Objects from {} ({} remaining)"
                                .format(self.zone.name,
                                        len(self.zone.clearable_items)))
        self.foes_text = ("Remove {} from {} ({} remaining)"
                          .format(self.zone.foes.name,
                                  self.zone.name,
                                  len(self.zone.foes)))
        self.reset_text = ("Reset shops timer for {} ({} shop{})"
                           .format(self.zone.name,
                                   len(self.zone.shops),
                                   "s" if len(self.zone.shops) > 1 else ""))


class ZonesFrame(Frame):
    def __init__(self, parent, xml_handle):
        Frame.__init__(self, parent)

        self._xml_handle = xml_handle
        self._zones = {}
        reset_offset = len(self._xml_handle.zones) * 2
        Label(self).grid(row=reset_offset, column=0)
        for n, (ID, zone) in enumerate(self._xml_handle.zones.items()):
            self._zones[ID] = ZoneFrame(self, zone, n, reset_offset + 1)

    def commit(self):
        for ID, zone in self._xml_handle.zones.items():
            if self._zones[ID].clearables_checked:
                zone.clearable_items.clear()
            if self._zones[ID].foes_checked:
                zone.foes.clear()
            if self._zones[ID].reset_checked:
                zone.shops.reset_shops_timer()
            self._zones[ID].update()
