#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: config.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import sys
import json
from clint import resources

CONFIG_FILE = "config.json"
BASE_CONFIG = {
    "startup_check": False
}

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Config(object):
    _config = None

    @ClassProperty
    @classmethod
    def config(cls):
        if cls._config is None:
            config = resources.user.read(CONFIG_FILE)
            if config is None:
                config = BASE_CONFIG
                cls.commit()
            else:
                config = json.loads(config)
            cls._config = config
        return cls._config

    @classmethod
    def commit(cls):
        resources.user.write(CONFIG_FILE, json.dumps(cls.config))


resources.init('Arzaroth', 'CelesiaSunrise')
