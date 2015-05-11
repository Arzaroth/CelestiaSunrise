#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: xmlhandler.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import sys
import rapidxml

from collections import OrderedDict, defaultdict
from six import unichr, add_metaclass
from celestia.utility.defaultordereddict import DefaultOrderedDict
from celestia.utility.utility import (Pony, Inventory, MissingPonies,
                                      Currency, Clearables,
                                      Foes, Zone, Shops)

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
    PONY_LIST = OrderedDict([
        ('Pony_Ace', 'Ace'),
        ('Pony_AKYearling', 'AKYearling'),
        ('Pony_Aloe', 'Aloe'),
        ('Pony_Apple_Bloom', 'Apple Bloom'),
        ('Pony_Apple_Bottoms', 'Apple Bottoms'),
        ('Pony_Apple_Bumpkin', 'Apple Bumpkin'),
        ('Pony_Apple_Cider', 'Apple Cider'),
        ('Pony_Apple_Cinnamon', 'Apple Cinnamon'),
        ('Pony_Apple_Cobbler', 'Apple Cobbler'),
        ('Pony_Apple_Dumpling', 'Apple Dumpling'),
        ('Pony_Apple_Honey', 'Apple Honey'),
        ('Pony_Apple_Leaves', 'Apple Leaves'),
        ('Pony_Apple_Pie', 'Apple Pie'),
        ('Pony_Apple_Rose', 'Apple Rose'),
        ('Pony_Apple_Stars', 'Apple Stars'),
        ('Pony_Apple_Strudel', 'Apple Strudel'),
        ('Pony_Applefritter', 'Apple Fritter'),
        ('Pony_Applejack', 'Applejack'),
        ('Pony_Aunt_Applesauce', 'Aunt Applesauce'),
        ('Pony_Aunt_Orange', 'Aunt Orange'),
        ('Pony_Babs_Seed', 'Babs Seed'),
        ('Pony_Banana_Bliss', 'Banana Bliss'),
        ('Pony_Beauty_Brass', 'Beauty Brass'),
        ('Pony_Berry_Punch', 'Berry Punch'),
        ('Pony_Big_Mac', 'Big Macintosh'),
        ('Pony_Blue_moon', 'Blue Moon'),
        ('Pony_Bon_Bon', 'Bon Bon'),
        ('Pony_Braeburn', 'Braeburn'),
        ('Pony_Candy_Apples', 'Candy Apples'),
        ('Pony_Caramel', 'Caramel'),
        ('Pony_Caramel_Apple', 'Caramel Apple'),
        ('Pony_Cheerilee', 'Cheerilee'),
        ('Pony_Cheese_Sandwich', 'Cheese Sandwich'),
        ('Pony_CherryBerry', 'Cherry Berry'),
        ('Pony_Cherry_Fizzy', 'Cherry Fizzy'),
        ('Pony_Cherry_Jubilee', 'Cherry Jubilee'),
        ('Pony_Coco_Pommel', 'Coco Pommel'),
        ('Pony_Comet_Tail', 'Comet Tail'),
        ('Pony_Compass_Star', 'Compass Star'),
        ('Pony_Conductor', 'Conductor'),
        ('Pony_Crescent_Moon', 'Crescent Moon'),
        ('Pony_Daisy', 'Daisy'),
        ('Pony_Daring', 'Daring Do'),
        ('Pony_Diamond_Tiara', 'Diamond Tiara'),
        ('Pony_Dj_Pon3', 'Dj Pon3 (Ponyville)'),
        ('Pony_Dj_Pon3_Canterlot', 'Dj Pon3 (Canterlot)'),
        ('Pony_DrWhooves', 'Dr. Hooves'),
        ('Pony_Eclaire_Creme', 'Eclaire Creme'),
        ('Pony_Elite_Male', 'Elite Pony'),
        ('Pony_Emerald_Gem', 'Emerald Gem'),
        ('Pony_Emerald_Green', 'Emerald Green'),
        ('Pony_Fancypants', 'Fancypants'),
        ('Pony_Featherweight', 'Featherweight'),
        ('Pony_Filthy_Rich', 'Filthy Rich'),
        ('Pony_Fine_Line', 'Fine Line'),
        ('Pony_FireChief', 'Dinky Doo (Fire Chief)'),
        ('Pony_Flam', 'Flam'),
        ('Pony_Flash_Sentry', 'Flash Sentry'),
        ('Pony_Flashy_Pony', 'Flashy Pony'),
        ('Pony_Fleetfoot', 'Fleetfoot'),
        ('Pony_Fleur_Dis_Lee', 'Fleur Dis Lee'),
        ('Pony_Flim', 'Flim'),
        ('Pony_Fluttershy', 'Fluttershy'),
        ('Pony_Forsythia', 'Forsythia'),
        ('Pony_Four_Step', 'Four Step'),
        ('Pony_Frederic', 'Frederic'),
        ('Pony_Gala_Appleby', 'Gala Appleby'),
        ('Pony_Golden_Delicious', 'Golden Delicious'),
        ('Pony_Golden_Harvest', 'Golden Harvest'),
        ('Pony_Goldie_Delicious', 'Goldie Delicious'),
        ('Pony_Granny_Smith', 'Granny Smith'),
        ('Pony_Half_Baked_Apple', 'Half Baked Apple'),
        ('Pony_Hayseed_Turnip_Truck', 'Hayseed Turnip Truck'),
        ('Pony_Hoity_Toity', 'Hoity Toity'),
        ('Pony_Jeff_Letrotski', 'Jeff Letrotski'),
        ('Pony_Jesus_Pezuna', 'Jesus Pezuna'),
        ('Pony_Jet_Set', 'Jet Set'),
        ('Pony_Joe', 'Joe'),
        ('Pony_Junebug', 'Junebug'),
        ('Pony_King_Sombra', 'King Sombra'),
        ('Pony_Lemony_Gem', 'Lemony Gem'),
        ('Pony_Lightning_Dust', 'Lightning Dust'),
        ('Pony_Lily_Valley', 'Lily Valley'),
        ('Pony_Limestone_Pie', 'Limestone Pie'),
        ('Pony_Lotus_Blossom', 'Lotus Blossom'),
        ('Pony_Lovestruck', 'Lovestruck'),
        ('Pony_Lucky_Clover', 'Lucky Clover'),
        ('Pony_Luna_Guard', 'Luna Guard'),
        ('Pony_Lyra', 'Lyra'),
        ('Pony_Lyrica', 'Lyrica'),
        ('Pony_Magnum', 'Hondo Flanks (Magnum)'),
        ('Pony_Mane_iac', 'Mane-iac'),
        ('Pony_Marble_Pie', 'Marble Pie'),
        ('Pony_Maud_Pie', 'Maud Pie'),
        ('Pony_Mayor', 'Mayor'),
        ('Pony_Minuette', 'Minuette'),
        ('Pony_Mr_Breezy', 'Mr. Breezy'),
        ('Pony_Mr_Cake', 'Mr. Cake'),
        ('Pony_Mrs_Cake', 'Mrs. Cake'),
        ('Pony_MsHarshwhinny', 'Ms. Harshwhinny'),
        ('Pony_Neon_Lights', 'Neon Lights'),
        ('Pony_Nerdpony', 'Nerdpony'),
        ('Pony_Noteworthy', 'Noteworthy'),
        ('Pony_Nurse_Redheart', 'Nurse Redheart'),
        ('Pony_Octavia', 'Octavia'),
        ('Pony_Parish', 'Parish'),
        ('Pony_Peachy_Pie', 'Peachy Pie'),
        ('Pony_Peachy_Sweet', 'Peachy Sweet'),
        ('Pony_Pearl', 'Cookie Crumbles (Betty Bouffant)'),
        ('Pony_Perfect_Pace', 'Perfect Pace'),
        ('Pony_Photofinish', 'Photo Finish'),
        ('Pony_Pinkie_Pie', 'Pinkie Pie'),
        ('Pony_Pinkiepies_Dad', 'Igneous Rock'),
        ('Pony_Pinkiepies_Mom', 'Cloudy Quartz'),
        ('Pony_Pipsqueak', 'Pipsqueak'),
        ('Pony_Prim_Hemline', 'Prim Hemline'),
        ('Pony_Prince_Blueblood', 'Prince Blueblood'),
        ('Pony_Princess_Cadence', 'Princess Cadence'),
        ('Pony_Princess_Celestia', 'Princess Celestia'),
        ('Pony_Princess_Luna', 'Princess Luna'),
        ('Pony_Professor', 'Bill Neigh (Professor)'),
        ('Pony_Purple_Wave', 'Purple Wave'),
        ('Pony_Quake', 'Quake'),
        ('Pony_Rainbow_Dash', 'Rainbow Dash'),
        ('Pony_Randolph', 'Randolph the Butler'),
        ('Pony_Rarity', 'Rarity'),
        ('Pony_Red_Delicious', 'Red Delicious'),
        ('Pony_Red_Gala', 'Red Gala'),
        ('Pony_Renfairpony', 'Richard (the) Hoovenheart'),
        ('Pony_Royal_Guard', 'Royal Guard'),
        ('Pony_Royal_Pin', 'Royal Pin'),
        ('Pony_Royal_Ribbon', 'Royal Ribbon'),
        ('Pony_Rumble', 'Rumble'),
        ('Pony_Sapphire_Shores', 'Sapphire Shores'),
        ('Pony_Savoir_Fare', 'Savoir Fare'),
        ('Pony_Scootaloo', 'Scootaloo'),
        ('Pony_Shadow_Surprise', 'The Shadowbolts'),
        ('Pony_Shining_Armour', 'Shining Armour'),
        ('Pony_Shooting_Star', 'Shooting Star'),
        ('Pony_Silver_Shill', 'Silver Shill'),
        ('Pony_Silver_Spoon', 'Silver Spoon'),
        ('Pony_Snails', 'Snails'),
        ('Pony_Snips', 'Snips'),
        ('Pony_Soarin', 'Soarin'),
        ('Pony_Spitfire', 'Spitfire'),
        ('Pony_Sunny_Daze', 'Sunny Daze'),
        ('Pony_Sunsetshimmer', 'Sunset Shimmer'),
        ('Pony_Suri_Polomare', 'Suri Polomare'),
        ('Pony_Swan_Song', 'Swan Song'),
        ('Pony_Sweetiebelle', 'Sweetie Belle'),
        ('Pony_Thunderlane', 'Thunderlane'),
        ('Pony_Toe_Tapper', 'Toe Tapper'),
        ('Pony_Torch_Song', 'Torch Song'),
        ('Pony_Trenderhoof', 'Trenderhoof'),
        ('Pony_Trixie', 'Trixie'),
        ('Pony_Truffle', "Teacher's Pet"),
        ('Pony_Twilight_Sparkle', 'Twilight Sparkle'),
        ('Pony_Twilight_Velvet', 'Twilight Velvet'),
        ('Pony_Twilights_Dad', "Night Light (Twilight's Dad)"),
        ('Pony_Twinkleshine', 'Twinkleshine'),
        ('Pony_Twist', 'Twist'),
        ('Pony_Uncle_Orange', 'Uncle Orange'),
        ('Pony_Unicorn_Guard', 'Unicorn Guard'),
        ('Pony_Uppercrust', 'Upper Crust'),
        ('Pony_Walter', 'Walter (Bowling Pony)'),
        ('Pony_Wensley', 'Wensley'),
        ('Pony_Wild_Fire', 'Wild Fire'),
        ('Pony_Zecora', 'Zecora'),
        ('Pony_Zipporwhill', 'Zipporwhill'),
    ])

    ponies = XmlDescriptor()
    inventory = XmlDescriptor()
    missing_ponies = XmlDescriptor()
    currencies = XmlDescriptor()
    actions = XmlDescriptor()
    zones = XmlDescriptor()
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
                                   None if ID not in XmlHandler.PONY_LIST else
                                   XmlHandler.PONY_LIST[ID])
        return res

    def _get_inventory(self):
        try:
            storage = self.xmlobj['MLP_Save']['PlayerData']['Storage']
        except KeyError:
            storage = self.xmlobj.allocate_node('Storage')
            self.xmlobj['MLP_Save']['PlayerData'].append_node(storage)
        return Inventory(storage, self.xmlobj)

    def _get_missing_ponies(self):
        return MissingPonies(self.ponies, self.inventory.ponies,
                             XmlHandler.PONY_LIST)

    def _get_currencies(self):
        playerdata = self.xmlobj['MLP_Save']['PlayerData']
        res = DefaultOrderedDict(OrderedDict)
        main = res['Main currencies']
        main['Bits'] = Currency('@Coins', playerdata)
        main['Gems'] = Currency('@Hearts', playerdata)
        main['Hearts'] = Currency('@Social', playerdata)
        try:
            main['Sapphires'] = Currency('@BossEventCurrency', playerdata)
        except:
            pass
        main['Wheels'] = Currency('@Wheels', playerdata['Minecart'], 5)
        shards = playerdata['Shards']
        for i in ('Loyalty', 'Honesty', 'Kindness', 'Generosity', 'Laughter', 'Magic'):
            res['Shards'][i + ' shards'] = Currency('@' + i, shards, 999)
        try:
            ingredients = playerdata['Ingredients']
            zecora = res['Zecora ingredients']
            zecora['Black Iris'] = Currency('@BlackIris', ingredients, 5)
            zecora['Garlic'] = Currency('@Garlic', ingredients, 5)
            zecora['Sticky Sap'] = Currency('@GlueTree', ingredients, 5)
            zecora['Joke Plant'] = Currency('@PoisonJokePlant', ingredients, 5)
            zecora['Purple Mushrooms'] = Currency('@PurpleGlowingMushrooms', ingredients, 5)
            zecora['Red Orchid'] = Currency('@RedOrchid', ingredients, 5)
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

    def pre_load(self):
        self.currencies
        self.ponies
        self.inventory
        self.missing_ponies
        self.zones
        self.actions

    def to_string(self):
        return self.xmlobj.unparse()

    def prettify(self):
        return self.xmlobj.unparse(pretty=True)
