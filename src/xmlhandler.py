#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: xmlhandler.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function
import xmltodict
from collections import OrderedDict, defaultdict
from src.defaultordereddict import DefaultOrderedDict
from src.utility import Pony, InventoryPony, Currency, Clearables, Foes, Zone

def remove_parent(xml_data):
    return xml_data.replace('(', '_x0028_').replace(')', '_x0029_')

def add_parent(xml_data):
    return xml_data.replace('_x0028_', '(').replace('_x0029_', ')')

class XmlHandler(object):
    def __init__(self, xml_data):
        print('Parsing XML tree...')
        self.xmlobj = xmltodict.parse(remove_parent(xml_data))
        self._ponies = None
        self._inventory_ponies = None
        self._currencies = None
        self._actions = None
        self._zones = None

    def _filtered_actions(self, ID):
        res = defaultdict(dict)
        for typ, actions in self.actions['Ponies'].items():
            for action, tags in actions.items():
                items = tags[0]['Item']
                if type(items) != list:
                    items = [items]
                tag = [i for i in items if i['@Category'] == ID]
                if not tag:
                    tag = [OrderedDict([('@Category', ID), ('@Value', "0")])]
                    items.append(tag[0])
                    tags[0]['Item'] = items
                res[typ][action] = tag
        return {'Pony': res, 'Global': self.actions['Global']}

    def _get_pony_list(self):
        res = OrderedDict()
        mapzones = self.xmlobj['MLP_Save']['MapZone']
        if type(mapzones) != list:
            mapzones = [mapzones]
        for mapzone in mapzones:
            ponyobjects = mapzone['GameObjects']['Pony_Objects']
            if ponyobjects:
                for ponytag in ponyobjects['Object']:
                    res[ponytag["@ID"]] = Pony(ponytag, self._filtered_actions(ponytag["@ID"]))
        return res

    def _get_inventory_pony_list(self):
        res = OrderedDict()
        storage = self.xmlobj['MLP_Save']['PlayerData']['Storage']
        if not storage:
            return res
        items = storage['StoredItem']
        if type(items) != list:
            items = [items]
        for item in items:
            if item['@ID'].startswith('Pony_'):
                res[item['@ID']] = InventoryPony(item)
        return res

    def _get_currencies(self):
        playerdata = self.xmlobj['MLP_Save']['PlayerData']
        res = DefaultOrderedDict(OrderedDict)
        res['Main']['Coins'] = Currency('@Coins', playerdata)
        res['Main']['Gems'] = Currency('@Hearts', playerdata)
        res['Main']['Hearts'] = Currency('@Social', playerdata)
        res['Main']['Wheels'] = Currency('@Wheels', playerdata['Minecart'], 5)
        shards = playerdata['Shards']
        for i in ('Loyalty', 'Honesty', 'Kindness', 'Generosity', 'Laughter', 'Magic'):
            res['Shards'][i] = Currency('@' + i, shards)
        ingredients = playerdata['Ingredients']
        res['Ingredients']['Black Iris'] = Currency('@BlackIris', ingredients, 5)
        res['Ingredients']['Garlic'] = Currency('@Garlic', ingredients, 5)
        res['Ingredients']['Sticky Sap'] = Currency('@GlueTree', ingredients, 5)
        res['Ingredients']['Joke Plant'] = Currency('@PoisonJokePlant', ingredients, 5)
        res['Ingredients']['Purple Mushrooms'] = Currency('@PurpleGlowingMushrooms', ingredients, 5)
        res['Ingredients']['Red Orchid'] = Currency('@RedOrchid', ingredients, 5)
        return res

    def _get_zones(self):
        mapzones_spec = OrderedDict((
            ("0", {"name": "Ponyville",
                   "foes": {"ID": "Parasprite_Objects",
                            "name": "Parasprites"}}),
            ("1", {"name": "Canterlot",
                   "foes": {"ID": "Changeling_Objects",
                            "name": "Changelings"}}),
            ("2", {"name": "Sweet Apple Acres",
                   "foes": {"ID": "Parasprite_Objects",
                            "name": "Vampire Bats"}}),
            ("3", {"name": "Everfree Forest",
                   "foes": {"ID": "Plunderseed_Vine_Objects",
                            "name": "Plunderseed Vines"}}),
        ))
        zones = OrderedDict()
        mapzones = self.xmlobj['MLP_Save']['MapZone']
        if type(mapzones) != list:
            mapzones = [mapzones]
        for mapzone in mapzones:
            gameobjects = mapzone['GameObjects']
            try:
                zone_spec = mapzones_spec[mapzone["@ID"]]
            except:
                continue
            clearables = Clearables('Clearable_Objects',
                                    gameobjects['Clearable_Objects'])
            foes = Foes(zone_spec["foes"]["ID"],
                        zone_spec["foes"]["name"],
                        gameobjects[zone_spec["foes"]["ID"]])
            zones[mapzone["@ID"]] = Zone(mapzone["@ID"],
                                         zone_spec["name"],
                                         clearables,
                                         foes)
        return zones

    def _get_actions(self):
        datatable = self.xmlobj['MLP_Save']['QuestData']['GlobalDataTable']['DataTable']
        objectcategories = datatable['ObjectCategoryList']['ObjectCategory']
        globalcategories = datatable['GlobalCategoryList']['GlobalCategory']
        actions = defaultdict(lambda: defaultdict(list))
        glob = defaultdict(lambda: defaultdict(list))
        def populate_dict(dikt, key='@ID', suffix='', inner=None):
            for typ in ('Complete', 'Started', 'ItemSelected'):
                for action in Pony.GameTypes.map:
                    if (tag[key] == ('PlayAction%s_%s%s' % (typ, action, suffix))
                        and (not inner or inner in tag)):
                        dikt[typ][action].append(tag)
            for typ in ('Complete', 'Started'):
                if tag[key] == ('ClearSkies_%s%s' % (typ, suffix)):
                    dikt['ClearSkies'][typ].append(tag)
            if tag[key] == ('PlayActionComplete%s' % suffix):
                dikt['Complete']['All'].append(tag)

        for tag in objectcategories:
            populate_dict(actions, inner='Item')
        for tag in globalcategories:
            for suffix in (' [TOTAL]', ' [TOTAL] Pony'):
                populate_dict(glob, key='@Category', suffix=suffix)
        return {'Global': glob, 'Ponies': actions}

    @property
    def ponies(self):
        if self._ponies is None:
            self._ponies = self._get_pony_list()
        return self._ponies

    @property
    def inventory_ponies(self):
        if self._inventory_ponies is None:
            self._inventory_ponies = self._get_inventory_pony_list()
        return self._inventory_ponies

    @property
    def currencies(self):
        if self._currencies is None:
            self._currencies = self._get_currencies()
        return self._currencies

    @property
    def zones(self):
        if self._zones is None:
            self._zones = self._get_zones()
        return self._zones

    @property
    def actions(self):
        if self._actions is None:
            self._actions = self._get_actions()
        return self._actions

    def pre_load(self):
        self.currencies
        self.ponies
        self.inventory_ponies
        self.zones
        self.actions

    def __repr__(self):
        return xmltodict.unparse(self.xmlobj, full_document=False)

    def __str__(self):
        return xmltodict.unparse(self.xmlobj, full_document=False, pretty=True, indent='  ')
