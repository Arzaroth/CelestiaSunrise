#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: CelestiaSunrise.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import sys
import binascii
import traceback
from docopt import docopt
from setup import VERSION
from celestia import PonyShell, Gui
from celestia.save import SaveData

PRGM = "CelestiaSunrise"

INTRO = """
{prgm} {ver}
Edit your MLP saves with the power of the true goddess.
""".format(prgm=PRGM, ver='.'.join(VERSION))

AUTHOR = """
Original program by Arzaroth <lekva@arzaroth.com>, inspired by Wilfried Pasquazzo ("Evenprime") work."""

__doc__ = """
{intro}

Usage:
  {prgm} [-d]
  {prgm} [-d] [-g|-s] -l <save_file>
  {prgm} [-d] [-g|-s] <save_file> (<encrypt_key> | --dbfile=<gameloft_sharing>)
  {prgm} -h
  {prgm} --version

Arguments:
  save_file                             Path to save file. Must be readable.
  encrypt_key                           Key used to decrypt the save file. Must be base64 encoded.
  gameloft_sharing                      Path to the gameloft_sharing database file. Must be readable.

Options:
  -l, --legacy                          Read a legacy save file (1.8.x version).
  -d, --debug                           Debug mode.
  -g, --gui                             Enable graphical mode (default).
  -s, --shell                           Enable shell-like mode.
  -f, --dbfile=<gameloft_sharing>       Retrieves the GLUID from the gameloft_sharing file.
  -v, --version                         Show version number.
  -h, --help                            Show this help and exit.

Notes:
  - This tool might have compatibility issues with recent versions of save files. It was tested with save files generated from the 2.9.x version of the game.
  - The code of this tool is currently open source. If you experiment issues, feel free to report or improve it.

Author:
  {author}
""".format(intro=INTRO, author=AUTHOR, prgm=PRGM)

if __name__ == '__main__':
    opts = docopt(__doc__, version='.'.join(VERSION))
    try:
        savedata = SaveData(savefile=opts['<save_file>'],
                            gluid=opts['<encrypt_key>'],
                            dbfile=opts['--dbfile'],
                            usedb=opts['--dbfile'] is not None,
                            legacy=opts['--legacy'])
        if opts['--shell']:
            PonyShell(savedata).cmdloop(intro=INTRO)
        else:
            Gui(savedata)
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
