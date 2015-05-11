#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: CelestiaSunrise.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import inspect
import os
import sys
import binascii
import traceback
from setup import VERSION
from celestia import PonyShell, Gui
from celestia.utils.update import check_frozen
from docopt import docopt

def get_script_name(follow_links=True):
    if check_frozen():
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_name)
    if follow_links:
        path = os.path.realpath(path)
    return path

PRGM = os.path.basename(get_script_name())

__doc__ = """
{prgm} {ver}
Edit your MLP saves with the power of the true goddess.
Type help or ? to list commands.

Usage:
  {prgm} [-d]
  {prgm} [-d] [-g|-s] -l <save_file>
  {prgm} [-d] [-g|-s] <save_file> (<encrypt_key> | -f <gameloft_sharing>)
  {prgm} -h
  {prgm} --version

Arguments:
  save_file             Path to save file. Must be readable.
  encrypt_key           Key used to decrypt the save file. Must be base64 encoded.
  gameloft_sharing      Path to the gameloft_sharing database file. Must be readable.

Options:
  -l --legacy           Read a legacy save file (1.8.x version).
  -d --debug            Debug mode.
  -g --gui              Enable graphical mode (default).
  -s --shell            Enable shell-like mode.
  -f --dbfile           Retrieves the GLUID from the gameloft_sharing file.
  -v --version          Show version number.
  -h --help             Show this help and exit.

Notes:
  - This tool might have compatibility issues with recent versions of save files. It was tested with save files generated from the 2.3.x version of the game.
  - The code of this tool is currently open source. If you experiment issues, feel free to report or improve it.

Author:
  Original program by Arzaroth <lekva@arzaroth.com>, inspired by Wilfried Pasquazzo ("Evenprime") work.
""".format(prgm=PRGM, ver='.'.join(VERSION))

if __name__ == '__main__':
    opts = docopt(__doc__, version='.'.join(VERSION))
    try:
        if opts['--shell']:
            PonyShell(savefile=opts['<save_file>'],
                      gluid=opts['<encrypt_key>'],
                      dbfile=opts['<gameloft_sharing>'],
                      legacy=opts['--legacy']).cmdloop(intro=__doc__)
        else:
            Gui(savefile=opts['<save_file>'],
                gluid=opts['<encrypt_key>'],
                dbfile=opts['<gameloft_sharing>'],
                legacy=opts['--legacy']).start()
    except binascii.Error:
        print("Invalid decryption key",
              file=sys.stderr)
    except Exception as e:
        print('Something went wrong, error message:',
              file=sys.stderr)
        print(str(e),
              file=sys.stderr)
        if opts['--debug']:
            print()
            tb = traceback.format_exc()
            print(tb)
    print('Exiting...')
    sys.exit(0)
