#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: show.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

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
