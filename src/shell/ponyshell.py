#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponyshell.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
import binascii
import sys
from cmd import Cmd
from src.savemanager import (SaveManager, SaveError,
                             decompress_data, compress_data)
from src.xml.xmlhandler import XmlHandler
from src.utility.utility import Pony
from src.utility.gluid import retrieve_gluid
from .docopt_utils import docopt_cmd, docopt_cmd_completion
from .show import (show_currencies, show_currency,
                   show_ponies, show_pony,
                   show_zones, show_zone)
from .set import (set_currency,
                  set_ponies, set_pony,
                  set_zones, set_zone,
                  set_inventory)
import six

class PonyMeta(type):
    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        for key, value in attrs.items():
            if key.startswith('do_') and value.__doc__:
                new_attrs['complete_' + key[3:]] = docopt_cmd_completion(value)
            new_attrs[key] = value
        return super(PonyMeta, cls).__new__(cls, name, bases, new_attrs)


@six.add_metaclass(PonyMeta)
class PonyShell(Cmd, object):
    prompt = 'ponyshell> '

    def __init__(self, savefile, gluid, dbfile, legacy):
        Cmd.__init__(self)
        gluid = retrieve_gluid(dbfile) if dbfile is not None else gluid
        gluid = binascii.a2b_base64(gluid) if gluid is not None else b''
        self._save_manager = SaveManager(savefile, gluid)
        data, self.save_number = self._save_manager.load(legacy)
        if not legacy:
            data = decompress_data(data)
        self._xml_handle = XmlHandler(data)
        self._xml_handle.pre_load()
        self.legacy = legacy
        self._show_functions = {
            'currencies': show_currencies,
            'currency': show_currency,
            'ponies': show_ponies,
            'pony': show_pony,
            'zones': show_zones,
            'zone': show_zone,
        }
        self._set_functions = {
            'currency': set_currency,
            'ponies': set_ponies,
            'pony': set_pony,
            'zones': set_zones,
            'zone': set_zone,
            'inventory': set_inventory,
        }

    def cmdloop(self, intro=None):
        if intro is None:
            print(self.intro)
        try:
            Cmd.cmdloop(self, intro="")
            self.postloop()
        except KeyboardInterrupt:
            print("^C")
            self.cmdloop(intro)

    @docopt_cmd
    def do_show(self, args):
        """Show what you requested.

Usage:
  show currencies
  show currency <currency_id>...
  show ponies [-i|-o]
  show pony <pony_id>...
  show zones
  show zone <zone_id>...

Arguments:
  currency_id   Id of a currency. Can be retrieved with "show currencies".
  pony_id       Id of a pony. Can be retrieved with "show ponies".
  zone_id       Id of a zone. Can be retrieved with "show zones".

Options:
  -i            Displays ponies in inventory.
  -o            Displays not owned ponies.
  -h --help     Show this help."""
        for i in self._show_functions:
            if args[i]:
                self._show_functions[i](self._xml_handle, args)
                break

    @docopt_cmd
    def do_set(self, args):
        """Set what you requested.

Usage:
  set currency <value> <currency_id>...
  set ponies (level|shards) (up|down)
  set ponies (level|shards) <value>
  set ponies reset_game_timer
  set pony (level|shards) (up|down) <pony_id>...
  set pony (level|shards|next_game) <value> <pony_id>...
  set pony reset_game_timer <pony_id>...
  set zones clear [clearables|foes]
  set zones reset_shops_timer
  set zone clear [clearables|foes] <zone_id>...
  set zone reset_shops_timer <zone_id>...
  set inventory add <not_owned_pony_id>...

Arguments:
  currency_id           Id of a currency. Can be retrieved with "show currencies".
  pony_id               Id of a pony. Can be retrieved with "show ponies".
  zone_id               Id of a zone. Can be retrieved with "show zones".
  not_owned_pony_id     Id of a not owned pony. Can be retrieved with "show ponies -o".
  level value           An integer between 0 and 5.
  shards value          An integer between 0 and 10.
  next_game             One of Ball, Apple or Book.

Options:
  -h --help             Show this help."""
        for i in self._set_functions:
            if args[i]:
                self._set_functions[i](self._xml_handle, args)
                break

    @docopt_cmd
    def do_dump_xml(self, args):
        """Dump the actual XML tree.

Usage:
  dump_xml [<file>]

Arguments:
  file          If present, write to file instead of standard output.

Options:
  -h --help     Show this help."""
        if args['<file>']:
            try:
                with open(args['<file>'], 'w') as f:
                    f.write(self._xml_handle.prettify())
            except Exception as e:
                print("Was unable to write to file, reason: {}".format(str(e)))
        else:
            print(self._xml_handle.prettify())

    @docopt_cmd
    def do_import_xml(self, args):
        """Import an XML tree. Use with caution.

Usage:
  import_xml <file>

Arguments:
  file          Path to a file containing an XML tree.

Options:
  -h --help     Show this help."""
        try:
            with open(args['<file>'], 'rb') as f:
                xml_data = f.read()
            new_xml_handle = XmlHandler(xml_data)
            new_xml_handle.pre_load()
        except Exception as e:
            print("Was unable to load from file, reason: {}".format(str(e)))
        else:
            self._xml_handle = new_xml_handle

    @docopt_cmd
    def do_write_save(self, args):
        """Write the current state of the save into a file

Usage:
  write_save <file> [<gluid>]
  write_save -l <file>

Arguments:
  file          Path to the new save file.
  gluid         GLUID used to encrypt the new save file. Must be base64 encoded.

Options:
  -l --legacy   Write a legacy save file (1.8.x version).
  -h --help     Show this help."""
        if args['<gluid>'] is not None:
            try:
                args['<gluid>'] = binascii.a2b_base64(args['<gluid>'].encode('utf-8'))
            except binascii.Error:
                print("Invalid encryption key")
                return
        try:
            try:
                data = self._xml_handle.to_string().encode('utf-8')
            except UnicodeDecodeError:
                data = self._xml_handle.to_string()
            self._save_manager.save(compress_data(data),
                                    args['<file>'],
                                    self.save_number,
                                    args['<gluid>'],
                                    (self.legacy or args['--legacy'])
                                    and args['<gluid>'] is None)
        except Exception as e:
            print("Was unable to write to file, reason: {}".format(str(e)))

    def do_bye(self, args):
        print("Exit")
        return True
    do_exit = do_bye
    do_quit = do_bye
    do_EOF = do_bye

    def emptyline(self):
        pass

    def default(self, line):
        print("{}: command not found".format(line))
