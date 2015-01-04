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
from src.docopt_utils import docopt_cmd, docopt_cmd_completion
from src.savemanager import (SaveManager, SaveError,
                             decompress_data, compress_data)
from src.xmlhandler import XmlHandler
from src.utility import Pony
from src.gluid import retrieve_gluid
from src.show import (show_currencies, show_currency,
                      show_ponies, show_pony,
                      show_zones, show_zone)
from src.set import (set_currency,
                     set_ponies, set_pony,
                     set_zones, set_zone,
                     set_inventory)
import src.docstrings as docstrings

if sys.version_info.major < 3:
    import codecs
    open = codecs.open

class PonyShell(Cmd):

    prompt = 'ponyshell> '

    def __init__(self, savefile, gluid, dbfile, legacy):
        Cmd.__init__(self)
        gluid = retrieve_gluid(dbfile) if dbfile is not None else gluid
        gluid = binascii.a2b_base64(gluid) if gluid is not None else b''
        self._save_manager = SaveManager(savefile, gluid)
        data, self.save_number = self._save_manager.load(legacy)
        if not legacy:
            data = decompress_data(data)
        self._xml_handle = XmlHandler(data.decode('utf-8', 'ignore'))
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

    @docopt_cmd(docstrings.SHOW)
    def do_show(self, args):
        for i in self._show_functions:
            if args[i]:
                self._show_functions[i](self._xml_handle, args)
                break

    @docopt_cmd_completion(docstrings.SHOW)
    def complete_show(self):
        pass

    @docopt_cmd(docstrings.SET)
    def do_set(self, args):
        for i in self._set_functions:
            if args[i]:
                self._set_functions[i](self._xml_handle, args)
                break

    @docopt_cmd_completion(docstrings.SET)
    def complete_set(self):
        pass

    @docopt_cmd(docstrings.DUMP_XML)
    def do_dump_xml(self, args):
        if args['<file>']:
            try:
                with open(args['<file>'], 'w', encoding='utf-8') as f:
                    f.write(self._xml_handle.prettify())
            except Exception as e:
                print("Was unable to write to file, reason: {}".format(str(e)))
        else:
            print(self._xml_handle.prettify())

    @docopt_cmd_completion(docstrings.DUMP_XML)
    def complete_dump_xml(self):
        pass

    @docopt_cmd(docstrings.IMPORT_XML)
    def do_import_xml(self, args):
        try:
            with open(args['<file>'], 'r', encoding='utf-8') as f:
                xml_data = f.read()
            new_xml_handle = XmlHandler(xml_data)
            new_xml_handle.pre_load()
        except Exception as e:
            print("Was unable to load from file, reason: {}".format(str(e)))
        else:
            self._xml_handle = new_xml_handle

    @docopt_cmd_completion(docstrings.IMPORT_XML)
    def complete_import_xml(self):
        pass

    @docopt_cmd(docstrings.WRITE_SAVE)
    def do_write_save(self, args):
        if args['<gluid>'] is not None:
            try:
                args['<gluid>'] = binascii.a2b_base64(args['<gluid>'].encode('utf-8'))
            except binascii.Error:
                print("Invalid encryption key")
                return
        try:
            self._save_manager.save(compress_data(self._xml_handle
                                                  .to_string()
                                                  .encode('utf-8')),
                                    args['<file>'],
                                    self.save_number,
                                    args['<gluid>'],
                                    (self.legacy or args['--legacy'])
                                    and args['<gluid>'] is None)
        except Exception as e:
            print("Was unable to write to file, reason: {}".format(str(e)))

    @docopt_cmd_completion(docstrings.WRITE_SAVE)
    def complete_write_save(self):
        pass

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
        print("{}: command not found".format(line))
