#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: xmlhandler.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
import sys
from collections import OrderedDict, defaultdict
from src.defaultordereddict import DefaultOrderedDict
from src.utility import (Pony, Inventory,
                         Currency, Clearables,
                         Foes, Zone)

def remove_parent(xml_data):
    return xml_data.replace('(', '_x0028_').replace(')', '_x0029_')

def add_parent(xml_data):
    return xml_data.replace('_x0028_', '(').replace('_x0029_', ')')

class XmlHandler(object):
    def __init__(self, xml_data):
        import xmltodict
        print('Parsing XML tree...')
        self.xmlobj = xmltodict.parse(remove_parent(xml_data))
        self._ponies = None
        self._inventory = None
        self._currencies = None
        self._actions = None
        self._zones = None
        self.__mapzones = None

    def _get_mapzones(self):
        if type(self.xmlobj['MLP_Save']['MapZone']) != list:
            self.xmlobj['MLP_Save']['MapZone'] = [self.xmlobj['MLP_Save']['MapZone']]
        return self.xmlobj['MLP_Save']['MapZone']

    def _filtered_actions(self, ID):
        res = defaultdict(dict)
        for typ, actions in self.actions['Ponies'].items():
            for action, tags in actions.items():
                if type(tags[0]['Item']) != list:
                    tags[0]['Item'] = [tags[0]['Item']]
                items = tags[0]['Item']
                tag = [i for i in items if i['@Category'] == ID]
                if not tag:
                    tag = [OrderedDict([('@Category', ID), ('@Value', "0")])]
                    items.append(tag[0])
                    tags[0]['Item'] = items
                res[typ][action] = tag
        return {'Pony': res, 'Global': self.actions['Global']}

    def _get_pony_list(self):
        res = OrderedDict()
        for mapzone in self._mapzones:
            ponyobjects = mapzone['GameObjects']['Pony_Objects']
            if ponyobjects:
                if type(ponyobjects['Object']) != list:
                    ponyobjects['Object'] = [ponyobjects['Object']]
                for ponytag in ponyobjects['Object']:
                    res[ponytag["@ID"]] = Pony(ponytag, self._filtered_actions(ponytag["@ID"]))
        return res

    def _get_inventory(self):
        res = OrderedDict()
        storage = self.xmlobj['MLP_Save']['PlayerData']['Storage']
        if not storage:
            return res
        if type(storage['StoredItem']) != list:
            storage['StoredItem'] = [storage['StoredItem']]
        items = storage['StoredItem']
        return Inventory(items)

    def _get_currencies(self):
        playerdata = self.xmlobj['MLP_Save']['PlayerData']
        res = DefaultOrderedDict(OrderedDict)
        main = res['Main currencies']
        main['Coins'] = Currency('@Coins', playerdata)
        main['Gems'] = Currency('@Hearts', playerdata)
        main['Hearts'] = Currency('@Social', playerdata)
        main['Wheels'] = Currency('@Wheels', playerdata['Minecart'], 5)
        shards = playerdata['Shards']
        for i in ('Loyalty', 'Honesty', 'Kindness', 'Generosity', 'Laughter', 'Magic'):
            res['Shards'][i + ' shards'] = Currency('@' + i, shards)
        ingredients = playerdata['Ingredients']
        zecora = res['Zecora ingredients']
        zecora['Black Iris'] = Currency('@BlackIris', ingredients, 5)
        zecora['Garlic'] = Currency('@Garlic', ingredients, 5)
        zecora['Sticky Sap'] = Currency('@GlueTree', ingredients, 5)
        zecora['Joke Plant'] = Currency('@PoisonJokePlant', ingredients, 5)
        zecora['Purple Mushrooms'] = Currency('@PurpleGlowingMushrooms', ingredients, 5)
        zecora['Red Orchid'] = Currency('@RedOrchid', ingredients, 5)
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
        for mapzone in self._mapzones:
            gameobjects = mapzone['GameObjects']
            try:
                zone_spec = mapzones_spec[mapzone["@ID"]]
            except:
                continue
            clearables = Clearables('Clearable_Objects',
                                    gameobjects)
            foes = Foes(zone_spec["foes"]["ID"],
                        zone_spec["foes"]["name"],
                        gameobjects)
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
    def _mapzones(self):
        if self.__mapzones is None:
            self.__mapzones = self._get_mapzones()
        return self.__mapzones

    @property
    def ponies(self):
        if self._ponies is None:
            self._ponies = self._get_pony_list()
        return self._ponies

    @property
    def inventory(self):
        if self._inventory is None:
            self._inventory = self._get_inventory()
        return self._inventory

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
        self.inventory
        self.zones
        self.actions

    def to_string(self):
        import xmltodict
        return add_parent(xmltodict.unparse(self.xmlobj,
                                            full_document=False))

    def prettify(self):
        import xmltodict
        return add_parent(xmltodict.unparse(self.xmlobj,
                                            full_document=False,
                                            pretty=True,
                                            indent='  '))
