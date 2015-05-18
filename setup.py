#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: setup.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import

import os
from setuptools import setup, find_packages

VERSION = ("v1", "2", "1")

if __name__ == '__main__':
    setup(
        name='CelestiaSunrise',
        version='.'.join(VERSION),
        license='BSD',

        url='https://arzaroth.github.io/CelestiaSunrise',
        download_url='https://github.com/Arzaroth/CelestiaSunrise/archive/%s.zip' % ('.'.join(VERSION)),

        author='Marc-Etienne Barrut',
        author_email='lekva@arzaroth.com',

        description='A savegame editor for the mobile game "My Little Pony"',
        long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
        keywords='pony cheat hack save editor',

        packages=find_packages('.'),
        scripts=['CelestiaSunrise.py'],

        install_requires=open('requirements.txt').read().split('\n'),
    )
