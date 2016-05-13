#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: xmlhandler.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import rapidxml

from collections import OrderedDict, defaultdict
from six import add_metaclass
from celestia.utility import PONY_LIST
from celestia.utility.defaultordereddict import DefaultOrderedDict
from celestia.utility.utility import (Pony, Inventory, MissingPonies,
                                      Currency, PlayerData, Clearables,
                                      Foes, Zone, Shops, Quest)

class XmlDescriptor(object):
    def __init__(self):
        self.name = None

    def __get__(self, instance, objtyp=None):
        if not instance.__dict__.get('_' + self.name, None):
            instance.__dict__['_' + self.name] = getattr(instance, '_get_' + self.name)()
        return instance.__dict__['_' + self.name]


class XmlMeta(type):
    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if isinstance(value, XmlDescriptor):
                value.name = key
        return super(XmlMeta, cls).__new__(cls, name, bases, attrs)


@add_metaclass(XmlMeta)
class XmlHandler(object):
    ponies = XmlDescriptor()
    inventory = XmlDescriptor()
    missing_ponies = XmlDescriptor()
    currencies = XmlDescriptor()
    player_infos = XmlDescriptor()
    actions = XmlDescriptor()
    zones = XmlDescriptor()
    quests = XmlDescriptor()
    _mapzones = XmlDescriptor()

    def __init__(self, xml_data):
        print('Parsing XML tree...')
        self.xmlobj = rapidxml.RapidXml(bytearray(xml_data))

    def _get__mapzones(self):
        if type(self.xmlobj['MLP_Save']['MapZone']) != list:
            return [self.xmlobj['MLP_Save']['MapZone']]
        return self.xmlobj['MLP_Save']['MapZone']

    def _filtered_actions(self, ID):
        res = defaultdict(dict)
        for typ, actions in self.actions['Ponies'].items():
            for action, tags in actions.items():
                items = tags[0]['Item']
                if type(items) != list:
                    items = [items]
                tag = [i for i in items if i['@Category'].value == ID]
                if not tag:
                    tag = self.xmlobj.allocate_node('Item')
                    tag.append_attribute(self.xmlobj.allocate_attribute('Category', ID))
                    tag.append_attribute(self.xmlobj.allocate_attribute('Value', '0'))
                    tags[0].append_node(tag)
                    tag = [tag]
                res[typ][action] = tag
        return {'Pony': res, 'Global': self.actions['Global']}

    def _get_ponies(self):
        res = OrderedDict()
        for mapzone in self._mapzones:
            try:
                ponyobjects = mapzone['GameObjects']['Pony_Objects']
            except KeyError:
                pass
            else:
                for ponytag in ponyobjects:
                    ID = ponytag["@ID"].value
                    res[ID] = Pony(ponytag, self._filtered_actions(ID),
                                   None if ID not in PONY_LIST else
                                   PONY_LIST[ID])
        return res

    def _get_inventory(self):
        try:
            storage = self.xmlobj['MLP_Save']['PlayerData']['Storage']
        except KeyError:
            storage = self.xmlobj.allocate_node('Storage')
            self.xmlobj['MLP_Save']['PlayerData'].append_node(storage)
        return Inventory(storage, self.xmlobj)

    def _get_missing_ponies(self):
        return MissingPonies(self.ponies, self.inventory.ponies, PONY_LIST)

    def _get_currencies(self):
        playerdata = self.xmlobj['MLP_Save']['PlayerData']
        res = DefaultOrderedDict(OrderedDict)
        main = res['Main currencies']
        main['Bits'] = Currency('@Coins', 'Bits', playerdata)
        main['Gems'] = Currency('@Hearts', 'Gems', playerdata)
        main['Hearts'] = Currency('@Social', 'Hearts', playerdata)
        shards = playerdata['Shards']
        for i in ('Loyalty', 'Honesty', 'Kindness', 'Generosity', 'Laughter', 'Magic'):
            res['Shards'][i + ' shards'] = Currency('@' + i, i + ' shards', shards, 999)
        try:
            # Minecart Update (1.8)
            main['Wheels'] = Currency('@Wheels', 'Wheels', playerdata['Minecart'], 5)
        except:
            pass
        try:
            # Dragon Update (2.3)
            main['Sapphires'] = Currency('@BossEventCurrency', 'Sapphires', playerdata)
        except:
            pass
        try:
            # Everfree Update (2.1)
            ingredients = playerdata['Ingredients']
            zecora = res['Zecora ingredients']
            zecora['Black Iris'] = Currency('@BlackIris', 'Black Iris', ingredients, 5)
            zecora['Garlic'] = Currency('@Garlic', 'Garlic', ingredients, 5)
            zecora['Sticky Sap'] = Currency('@GlueTree', 'Sticky Sap', ingredients, 5)
            zecora['Joke Plant'] = Currency('@PoisonJokePlant', 'Joke Plant', ingredients, 5)
            zecora['Purple Mushrooms'] = Currency('@PurpleGlowingMushrooms', 'Purple Mushrooms',
                                                  ingredients, 5)
            zecora['Red Orchid'] = Currency('@RedOrchid', 'Red Orchid', ingredients, 5)
        except:
            pass
        try:
            # Boutique Update (2.6)
            popcurrency = playerdata['PopCurrency']
            boutique = res['Boutique ingredients']
            boutique['Flower'] = Currency('@PopCurrency1', 'Flower', popcurrency, 999)
            boutique['Button'] = Currency('@PopCurrency2', 'Button', popcurrency, 999)
            boutique['Thread'] = Currency('@PopCurrency3', 'Thread', popcurrency, 999)
            boutique['Fabric'] = Currency('@PopCurrency4', 'Fabric', popcurrency, 999)
            boutique['Ribbon'] = Currency('@PopCurrency5', 'Ribbon', popcurrency, 999)
        except:
            pass
        try:
            # Party Update (2.8)
            main['Party Points'] = Currency('@SpecialCurrency', 'Party Points', playerdata)
        except:
            pass
        return res

    def _get_player_infos(self):
        playerdata = self.xmlobj['MLP_Save']['PlayerData']
        res = OrderedDict()
        res['Level'] = PlayerData('@Level', 'Level', playerdata, 125)
        res['XP'] = PlayerData('@XP', 'XP', playerdata)
        try:
            # VIP Update (2.7)
            res['VIP Points'] = PlayerData('@vip_points', 'VIP Points', playerdata['vip'])
        except:
            pass
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
                zone_spec = mapzones_spec[mapzone["@ID"].value]
            except KeyError:
                continue
            clearables = Clearables('Clearable_Objects',
                                    gameobjects)
            foes = Foes(zone_spec["foes"]["ID"],
                        zone_spec["foes"]["name"],
                        gameobjects)
            shops = Shops(gameobjects['Pony_House_Objects'])
            zones[mapzone["@ID"].value] = Zone(mapzone["@ID"].value,
                                               zone_spec["name"],
                                               clearables,
                                               foes, shops)
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
                    if (tag[key].value == ('PlayAction%s_%s%s' % (typ, action, suffix))
                        and (not inner or inner in tag)):
                        dikt[typ][action].append(tag)
            for typ in ('Complete', 'Started'):
                if tag[key].value == ('ClearSkies_%s%s' % (typ, suffix)):
                    dikt['ClearSkies'][typ].append(tag)
            if tag[key].value == ('PlayActionComplete%s' % suffix):
                dikt['Complete']['All'].append(tag)

        for tag in objectcategories:
            populate_dict(actions, inner='Item')
        for tag in globalcategories:
            for suffix in (' [TOTAL]', ' [TOTAL] Pony'):
                populate_dict(glob, key='@Category', suffix=suffix)
        return {'Global': glob, 'Ponies': actions}

    def _get_quests(self):
        activequestlist = self.xmlobj['MLP_Save']['QuestData']['ActiveQuestList']
        return [Quest(quest) for quest in activequestlist]

    def pre_load(self):
        self.player_infos
        self.currencies
        self.ponies
        self.inventory
        self.missing_ponies
        self.zones
        self.quests
        self.actions

    def to_string(self):
        return self.xmlobj.unparse(raw=True)

    def prettify(self):
        return self.xmlobj.unparse(pretty=True, raw=True)
