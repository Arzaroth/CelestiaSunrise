#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: ponyshell.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import base64
import sys
from cmd import Cmd
from pprint import pprint
from src import SaveManager, SaveError
from src import decompress_data, compress_data
from src import XmlHandler
from src.docopt_utils import docopt_cmd
from src.utility import Pony

def show_currencies(xml_handle, args):
    print('Main currencies:')
    for cur, val in xml_handle.currencies['Main'].items():
        print('  {}: {}'.format(cur, val))
    print('\nShards:')
    for cur, val in xml_handle.currencies['Shards'].items():
        print('  {} shards: {}'.format(cur, val))
    print('\nZecora ingredients:')
    for cur, val in xml_handle.currencies['Ingredients'].items():
        print('  {}: {}'.format(cur, val))

def show_currency(xml_handle, args):
    for currency_id in args['<currency_id>']:
        for typ in xml_handle.currencies.values():
            for val in typ.values():
                if currency_id == val.name:
                    print(val)
                    return

def show_ponies(xml_handle, args):
    print('Ponies:')
    for pony in xml_handle.ponies.values():
        print('  {}'.format(pony))
    if args['-i']:
        print('\nInventory ponies:')
        for pony in xml_handle.inventory_ponies.values():
            print('  {}'.format(pony))

def show_pony(xml_handle, args):
    for pony_id in args['<pony_id>']:
        if pony_id in xml_handle.ponies:
            print(xml_handle.ponies[pony_id])
        if pony_id in xml_handle.inventory_ponies:
            print(xml_handle.inventory_ponies[pony_id])

def show_zones(xml_handle, args):
    print('Zones:')
    for zone in xml_handle.zones.values():
        print('  {}'.format(zone))

def show_zone(xml_handle, args):
    for zone_id in args['<zone_id>']:
        if zone_id in xml_handle.zones:
            print(xml_handle.zones[zone_id])

def set_currency(xml_handle, args):
    for typ in xml_handle.currencies.values():
        for val in typ.values():
            if args['<currency_id>'] == val.name:
                try:
                    val.value = args['<value>']
                except ValueError as e:
                    print(str(e))
                return

def process_set_pony(xml_handle, pony, args):
    if args['level']:
        if args['up']:
            pony.level_up()
        elif args['down']:
            pony.level_down()
        else:
            pony.level = args['<value>']
    elif args['shards']:
        if args['up']:
            pony.shard_up()
        elif args['down']:
            pony.shard_down()
        else:
            pony.shards = args['<value>']
    elif args['next_game']:
        try:
            pony.next_game = Pony.GameTypes.map[args['<value>']]
        except KeyError:
            raise ValueError("Invalid game type")
    elif args['reset_game_timer']:
        pony.reset_game_timer()

def set_ponies(xml_handle, args):
    try:
        for pony in xml_handle.ponies.values():
            process_set_pony(xml_handle, pony, args)
    except Exception as e:
        print(str(e))

def set_pony(xml_handle, args):
    try:
        for pony_id in args['<pony_id>']:
            if pony_id in xml_handle.ponies:
                process_set_pony(xml_handle, xml_handle.ponies[pony_id], args)
    except Exception as e:
        print(str(e))

def process_set_zone(xml_handle, zone, args):
    if args['clearables']:
        zone.clear_clearable_items()
    elif args['foes']:
        zone.clear_foes()
    else:
        zone.clear_all()

def set_zones(xml_handle, args):
    for zone in xml_handle.zones.values():
        process_set_zone(xml_handle, zone, args)

def set_zone(xml_handle, args):
    for zone_id in args['<zone_id>']:
        if zone_id in xml_handle.zones:
            process_set_zone(xml_handle, xml_handle.zones[zone_id], args)

class PonyShell(Cmd):

    prompt = 'ponyshell> '

    def __init__(self, savefile, gluid):
        Cmd.__init__(self)
        self._save_manager = SaveManager(savefile, base64.b64decode(gluid))
        self._xml_handle = XmlHandler(decompress_data(self._save_manager.load())
                                      .decode('utf-8'))
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
  show ponies [-i]
  show pony <pony_id>...
  show zones
  show zone <zone_id>...

Options:
  -i            Displays ponies in inventory.
  -h --help     Show this help."""
        for i in self._show_functions:
            if args[i]:
                self._show_functions[i](self._xml_handle, args)
                break

    @docopt_cmd
    def do_set(self, args):
        """Set what you requested.

Usage:
  set currency <value> <currency_id>
  set ponies (level|shards) (up|down)
  set ponies (level|shards) <value>
  set pony (level|shards) (up|down) <pony_id>...
  set pony (level|shards|next_game) <value> <pony_id>...
  set pony reset_game_timer <pony_id>...
  set zones clear [clearables|foes]
  set zone clear [clearables|foes] <zone_id>...

Options:
  -h --help     Show this help."""
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
                    f.write(str(self._xml_handle))
            except Exception as e:
                print("Was unable to write file, reason: {}".format(str(e)))
        else:
            print(self._xml_handle)

    @docopt_cmd
    def do_write_save(self, args):
        """Write the current state of the save into a file

Usage:
  write_save <file> [<gluid>]

Arguments:
  file          Path to the new save file.
  gluid         GLUID used to encrypt the new save file. Must be base64 encoded.

Options:
  -h --help     Show this help."""
        if args['<gluid>'] is not None:
            args['<gluid>'] = base64.b64decode(args['<gluid>'].encode('utf-8'))
            print(args['<gluid>'])
        try:
            self._save_manager.save(compress_data(repr(self._xml_handle)
                                                  .encode('utf-8')),
                                    args['<file>'],
                                    args['<gluid>'])
        except Exception as e:
            print("Was unable to write file, reason: {}".format(str(e)))

    def do_bye(self, args):
        """Quit the program"""
        print("Exit")
        return True
    do_exit = do_bye
    do_quit = do_bye
    do_EOF = do_bye

    def emptyline(self):
        pass

    def default(self, line):
        print("{}: command not found".format(line), file=sys.stderr)
