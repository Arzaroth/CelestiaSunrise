#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import os
import sys
import traceback
from src import (SaveManager,
                 decompress_data, compress_data,
                 XmlHandler, PonyShell)
from docopt import docopt

PRGM = os.path.basename(__file__)
VERSION = "0.4.1b"

__doc__ = """
{prgm} {ver}
Edit your MLP saves with the power of the true goddess.
Type help or ? to list commands.

Usage:
  {prgm} <save_file> <encrypt_key>

Arguments:
  save_file             Path to save file. Must be readable.
  encrypt_key           Key used to decrypt the save file. Must be base64 encoded.

Options:
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
        PonyShell(opts['<save_file>'], opts['<encrypt_key>']).cmdloop(intro=__doc__)
    except Exception as e:
        print('Something went wrong, traceback:\n',
              file=sys.stderr)
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
    print('Exiting...')
    sys.exit(0)
