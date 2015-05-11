#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: update.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import requests
import sys
from setup import VERSION
from pkg_resources import parse_version

def check_network():
    try:
        res = requests.get('http://74.125.224.72/',
                           timeout=1,
                           headers={"pragma": "no-cache"})
    except requests.exceptions.Timeout:
        return False
    return True

def check_version():
    if not check_network():
        return False
    r = requests.get('https://api.github.com/repos/Arzaroth/CelestiaSunrise/releases/latest')
    return parse_version(r.json()['tag_name']) > parse_version('.'.join(VERSION))

def check_frozen():
    return getattr(sys, 'frozen', False)

def update_version():
    if not check_version():
        return True
    return True
