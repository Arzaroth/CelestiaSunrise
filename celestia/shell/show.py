#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: show.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

def show_player(xml_handle, args):
    for typ in xml_handle.player_infos.values():
        if not args['<player_data>'] or args['<player_data>'] == typ.name:
            print(typ)

def show_currencies(xml_handle, args):
    for name, typ in xml_handle.currencies.items():
        print('{}:'.format(name))
        for cur, val in typ.items():
            print('  {}: {}'.format(cur, val))

def show_currency(xml_handle, args):
    for currency_id in args['<currency_id>']:
        for typ in xml_handle.currencies.values():
            for val in typ.values():
                if currency_id == val.name:
                    print(val)

def show_ponies(xml_handle, args):
    if args['-o']:
        print('Not owned ponies:')
        for ID, name in xml_handle.missing_ponies.items():
            print('Pony(ID: {}, Name: {})'.format(ID, name))
    else:
        print('Ponies:')
        for pony in xml_handle.ponies.values():
            print('  {}'.format(pony))
        if args['-i']:
            print('\nInventory ponies:')
            for pony in xml_handle.inventory.ponies.values():
                print('  {}'.format(pony[0]))

def show_pony(xml_handle, args):
    for pony_id in args['<pony_id>']:
        if pony_id in xml_handle.ponies:
            print(xml_handle.ponies[pony_id])
        if pony_id in xml_handle.inventory.ponies:
            print(xml_handle.inventory.ponies[pony_id][0])

def show_zones(xml_handle, args):
    print('Zones:')
    for zone in xml_handle.zones.values():
        print('  {}'.format(zone))

def show_zone(xml_handle, args):
    for zone_id in args['<zone_id>']:
        if zone_id in xml_handle.zones:
            print(xml_handle.zones[zone_id])
