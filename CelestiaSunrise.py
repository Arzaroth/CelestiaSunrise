#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: CelestiaSunrise.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
import os
import sys
import base64
import binascii
import traceback
from src import PonyShell, Gui

try:
    PRGM = os.path.basename(__file__)
except NameError:
    PRGM = os.path.basename(sys.argv[0])
VERSION = "0.7.1a"

__doc__ = """
{prgm} {ver}
Edit your MLP saves with the power of the true goddess.
Type help or ? to list commands.

Usage:
  {prgm} [-d]
  {prgm} [-d] [-g|-s] -l <save_file>
  {prgm} [-d] [-g|-s] <save_file> <encrypt_key>

Arguments:
  save_file             Path to save file. Must be readable.
  encrypt_key           Key used to decrypt the save file. Must be base64 encoded.

Options:
  -l --legacy           Read a legacy save file (1.8.x version).
  -d --debug            Debug mode.
  -g --gui              Enable graphical mode (default).
  -s --shell            Enable shell-like mode.
  -v --version          Show version number.
  -h --help             Show this help and exit.

Notes:
  - This tool might have compatibility issues with recent versions of save files. It was tested with save files generated from the 2.1.x version of the game.
  - The code of this tool is currently open source. If you experiment issues, feel free to report or improve it.

Author:
  Original program by Arzaroth <lekva@arzaroth.com>, inspired by Wilfried Pasquazzo ("Evenprime") work.
""".format(prgm=PRGM, ver=VERSION)

if __name__ == '__main__':
    from docopt import docopt
    opts = docopt(__doc__, version=VERSION)
    try:
        if opts['--shell']:
            if opts['<encrypt_key>'] is not None:
                gluid = base64.b64decode(opts['<encrypt_key>'])
            else:
                gluid = b''
            PonyShell(savefile=opts['<save_file>'],
                      gluid=gluid,
                      legacy=opts['--legacy']).cmdloop(intro=__doc__)
        else:
            Gui(savefile=opts['<save_file>'],
                gluid=opts['<encrypt_key>'],
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
