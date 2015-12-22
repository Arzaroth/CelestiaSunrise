#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: version.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import unicode_literals, absolute_import

import os
import sys
import socket
import inspect
import requests
from setup import VERSION
from pkg_resources import parse_version

def get_script_name(follow_links=True):
    if check_frozen():
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_name)
    if follow_links:
        path = os.path.realpath(path)
    return path

def check_network(host="8.8.8.8", port=53):
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    except Exception:
        return False
    return True

def check_frozen():
    return getattr(sys, 'frozen', False)

def check_version(force=False):
    res = {
        "up_to_date": True,
        "error": None,
        "download_url": None,
    }
    if not check_network():
        res["error"] = "It seems you don't have access to the internet"
    elif not check_frozen() and not force:
        res["error"] = "You're not running the frozen version"
    else:
        r = requests.get('https://api.github.com/repos/Arzaroth/CelestiaSunrise/releases/latest')
        res["up_to_date"] = parse_version(r.json()['tag_name']) <= parse_version('.'.join(VERSION))
        try:
            res["download_url"] = r.json()['assets'][0]['browser_download_url']
        except:
            res["error"] = "Unable to find download url"
    return res
