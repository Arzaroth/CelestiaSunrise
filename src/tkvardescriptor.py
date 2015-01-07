#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: tkvardescriptor.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

class TkVarDescriptor(object):
    def __init__(self, klass):
        self.label = None
        self.klass = klass

    def __get__(self, instance, objtype=None):
        if instance is None:
            return self
        return instance.__dict__[self.label].get()

    def __set__(self, instance, value):
        if self.label not in instance.__dict__:
            instance.__dict__[self.label] = self.klass(instance)
        instance.__dict__[self.label].set(value)

    def raw_klass(self, instance):
        return instance.__dict__[self.label]


class TkVarDescriptorOwner(type):
    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if isinstance(value, TkVarDescriptor):
                value.label = key
        return super(TkVarDescriptorOwner, cls).__new__(cls, name, bases, attrs)
