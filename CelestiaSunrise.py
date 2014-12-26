#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import os
import sys
import base64
import binascii
from src import PonyShell, Gui
from docopt import docopt

PRGM = os.path.basename(__file__)
VERSION = "0.5.0a"

__doc__ = """
{prgm} {ver}
Edit your MLP saves with the power of the true goddess.
Type help or ? to list commands.

Usage:
  {prgm} <save_file> <encrypt_key>
  {prgm} -l <save_file>
  {prgm} [-l] -g [<save_file>] [<encrypt_key>]

Arguments:
  save_file             Path to save file. Must be readable.
  encrypt_key           Key used to decrypt the save file. Must be base64 encoded.

Options:
  -l --legacy           Read a legacy save file (1.8.x version).
  -g --gui              Enable graphical mode.
  -h --help             Show this help and exit.

Notes:
  - This tool might have compatibility issues with recent versions of save files. It was tested with save files generated from the 2.1.x version of the game.
  - The code of this tool is currently open source. If you experiment issues, feel free to report or improve it.

Author:
  Original program by Arzaroth <lekva@arzaroth.com>, inspired by Wilfried Pasquazzo ("Evenprime") work.
""".format(prgm=PRGM, ver=VERSION)

if __name__ == '__main__':
    opts = docopt(__doc__, version=VERSION)
    try:
        if opts['--gui']:
            Gui(savefile=opts['<save_file>'],
                gluid=opts['<encrypt_key>'],
                legacy=opts['--legacy']).start()
        else:
            if opts['<encrypt_key>'] is not None:
                gluid = base64.b64decode(opts['<encrypt_key>'])
            else:
                gluid = ''
            PonyShell(savefile=opts['<save_file>'],
                      gluid=gluid,
                      legacy=opts['--legacy']).cmdloop(intro=__doc__)
    except binascii.Error:
        print("Invalid decryption key",
              file=sys.stderr)
    except Exception as e:
        print('Something went wrong, error message:',
              file=sys.stderr)
        print(str(e),
              file=sys.stderr)
        raise
    print('Exiting...')
    sys.exit(0)
