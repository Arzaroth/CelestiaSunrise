#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: update.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import requests
try:
    # py2
    from urllib2 import urlopen, URLError
except ImportError:
    # py3
    from urllib.request import urlopen
    from urllib.error import URLError
from setup import VERSION
from pkg_resources import parse_version

def check_network():
    try:
        res = urlopen('http://74.125.228.100',
                      timeout=1,
                      headers={"pragma": "no-cache"})
        return True
    except URLError:
        pass
    return False

def check_version():
    if not check_network():
        return False
    r = requests.get('https://api.github.com/repos/Arzaroth/CelestiaSunrise/releases/latest')
    return parse_version(r.json()['tag_name']) > parse_version('.'.join(VERSION))

def update_version():
    if not check_version():
        return True
    return True
