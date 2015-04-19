#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: utility.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
from collections import defaultdict, OrderedDict
from .enum import enum
from .defaultordereddict import DefaultOrderedDict

ZERO = "0.000000"

class MissingPonies(object):
    def __init__(self, owned_ponies, inventory_ponies, all_ponies):
        owned_ponies_id = set(owned_ponies.keys()) | set(inventory_ponies.keys())
        all_ponies_id = set(all_ponies.keys())
        not_owned = all_ponies_id - owned_ponies_id
        self._ponies = OrderedDict([(ID, name)
                                    for ID, name in all_ponies.items()
                                    if ID in not_owned])

    def items(self):
        return self._ponies.items()

    def values(self):
        return self._ponies.values()

    def keys(self):
        return self._ponies.keys()

    def __contains__(self, item):
        return item in self._ponies

    def __isub__(self, pony_id):
        self._ponies.pop(pony_id, None)
        return self

    def remove(self, pony_id):
        self -= pony_id


class Inventory(object):
    def __init__(self, tag, xmlobj):
        self._tag = tag
        self._xmlobj = xmlobj
        self._ponies = None
        self._decorations = None

    def _populate(self, prefix):
        res = DefaultOrderedDict(list)
        try:
            items = self._tag['StoredItem']
        except KeyError:
            items = []
        if type(items) != list:
            items = [items]
        for item in items:
            if item['@ID'].value.startswith(prefix):
                res[item['@ID'].value].append(StoredItem(item))
        return res

    @property
    def ponies(self):
        if self._ponies is None:
            self._ponies = self._populate('Pony_')
        return self._ponies

    @property
    def decorations(self):
        if self._decorations is None:
            self._decorations = self._populate('Decoration_')
        return self._decorations

    def __iadd__(self, ID):
        new_item = self._xmlobj.allocate_node('StoredItem')
        new_item.append_attribute(self._xmlobj.allocate_attribute('ID', ID))
        new_item.append_attribute(self._xmlobj.allocate_attribute('Cost', '0'))
        new_item.append_attribute(self._xmlobj.allocate_attribute('CostType', '0'))
        new_item.append_attribute(self._xmlobj.allocate_attribute('PonyLevel', '0'))
        new_item.append_attribute(self._xmlobj.allocate_attribute('PonyShards', '0'))
        new_item.append_attribute(self._xmlobj.allocate_attribute('PonyCurrentEXP', '0'))
        new_item.append_attribute(self._xmlobj.allocate_attribute('Constructed', '0'))
        new_item.append_attribute(self._xmlobj.allocate_attribute('PonyArriveBonus', '0'))
        self._tag.append_node(new_item)
        self._ponies = self._populate('Pony_')
        self._decorations = self._populate('Decoration_')
        return self

    def append(self, ID):
        self += ID


class StoredItem(object):
    def __init__(self, tag):
        self.name = tag["@ID"].value[5:].replace('_', ' ')
        self.ID = tag["@ID"].value
        self._tag = tag
        self.stored = True

    @property
    def _level(self):
        return min(max(int(self._tag["@PonyLevel"].value), 0), 5)

    @property
    def _exp(self):
        return int(self._tag["@PonyCurrentEXP"].value)

    @property
    def _shards(self):
        return min(max(int(self._tag["@PonyShards"].value), 0), 10)

    @property
    def level(self):
        return self._level

    @property
    def exp(self):
        return self._exp

    @property
    def shards(self):
        return self._shards

    @property
    def next_game(self):
        return 'None'

    def __repr__(self):
        return ('%s(ID: %s, Name: %s, Level: %s, Shards: %s, Next Game: %s)'
                % (self.__class__.__name__,
                   self.ID,
                   self.name,
                   self.level,
                   self.shards,
                   self.next_game))


class Pony(StoredItem):
    GameTypes = enum(Ball=0, Apple=1, Book=2)

    def __init__(self, tag, actions, name=None):
        StoredItem.__init__(self, tag)
        if name is not None:
            self.name = name
        self._leveltag = tag["Game"]["Level"]
        self._minigametag = tag["Game"]["MiniGame"]
        self._pony_actions = actions
        self.stored = False

    @StoredItem._level.getter
    def _level(self):
        return min(max(int(self._leveltag["@Level"].value), 0), 5)

    @StoredItem._exp.getter
    def _exp(self):
        return int(self._leveltag["@CurrentEXP"].value)

    @StoredItem._shards.getter
    def _shards(self):
        return min(max(int(self._leveltag["@Shards"].value), 0), 10)

    @StoredItem.level.setter
    def level(self, new_val):
        new_val = int(new_val)
        if new_val < 0 or new_val > 5:
            raise ValueError("Level must be beetween 0 and 5")

        def update_action_values(actions, new_val, old_vals=None):
            diff = bool(old_vals)
            if not old_vals:
                old_vals = defaultdict(dict)
            for k, v in actions['ClearSkies'].items():
                if not diff:
                    old_vals['ClearSkies'][k] = int(v[0]['@Value'].value)
                mod = new_val - old_vals['ClearSkies'][k]
                for i in v:
                    i['@Value'].value = str((int(i['@Value']) + mod) if diff else new_val)
            for action in ('Complete', 'ItemSelected', 'Started'):
                for k, v in actions[action].items():
                    if not diff:
                        old_vals[action][k] = int(v[0]['@Value'].value)
                    mod = (new_val * 2) - old_vals[action][k]
                    for i in v:
                        i['@Value'].value = str((int(i['@Value'].value) + mod)
                                                if diff else (new_val * 2))
            if not diff:
                old_vals['Complete']['All'] = int(actions['Complete']['All'][0]['@Value'].value)
            mod = (new_val * 2 * (len(Pony.GameTypes.map) + 1)) - old_vals['Complete']['All']
            for i in actions['Complete']['All']:
                i['@Value'].value = str((int(i['@Value'].value) + mod)
                                        if diff else (new_val * 2 *
                                                      (len(Pony.GameTypes.map) + 1)))
            return old_vals

        old_vals = update_action_values(self._pony_actions['Pony'], new_val)
        update_action_values(self._pony_actions['Global'], new_val, old_vals)
        self.shards = 0
        self._leveltag["@Level"].value = str(new_val)

    @StoredItem.shards.setter
    def shards(self, new_val):
        new_val = int(new_val)
        if new_val < 0 or new_val > 10:
            raise ValueError("Shards must be beetween 0 and 10")
        if self.level == 5 and new_val > 0:
            raise ValueError("Can't have shards at maximum level")
        self._leveltag["@Shards"].value = str(new_val)

    @StoredItem.next_game.getter
    def next_game(self):
        try:
            gametype = int(self._minigametag["@NextPlayAction"].value)
            name = Pony.GameTypes.rmap[gametype]
        except:
            name = 'Unknown'
        return name

    @next_game.setter
    def next_game(self, gametype):
        if gametype not in Pony.GameTypes.rmap:
            raise ValueError("Invalid game type")
        self._minigametag["@NextPlayAction"].value = str(gametype)

    def level_up(self, nb=1):
        self.level = min(max(self.level + nb, 0), 5)
        self.shards = 0

    def level_down(self, nb=1):
        self.level_up(-nb)

    def shard_up(self):
        if self.level != 5:
            self.shards = 10

    def shard_down(self):
        if self.level != 5:
            self.shards = 0

    def reset_game_timer(self):
        self._minigametag["@NextPlayTime"].value = ZERO


class Currency(object):
    def __init__(self, name, tag, limit=None):
        self.name = name
        self.limit = limit
        self._tag = tag[name]

    @property
    def value(self):
        return int(self._tag.value)

    @value.setter
    def value(self, new_val):
        new_val = int(new_val)
        if new_val < 0:
            raise ValueError("Can't set a negative currency value for %s" % self.name)
        if self.limit is not None and new_val > int(self.limit):
            raise ValueError("Value above the limit for %s" % self.name)
        self._tag.value = str(new_val)

    def __repr__(self):
        return ('%s(ID: %s, Value: %s, Limit: %s)'
                % (self.__class__.__name__,
                   self.name,
                   self.value,
                   self.limit))


class Clearables(object):
    def __init__(self, ID, tag):
        self.ID = ID
        self.name = 'Clearable Objects'
        self._tag = tag[ID]

    def cleared(self):
        return not self._tag.first_node()

    def clear(self):
        self._tag.remove_all_nodes()

    def __len__(self):
        return len(list(self._tag.children))

    def __repr__(self):
        return ('%s(ID: %s, Name: %s, Cleared: %s)'
                % (self.__class__.__name__,
                   self.ID,
                   self.name,
                   self.cleared()))


class Foes(Clearables):
    def __init__(self, ID, name, tag):
        Clearables.__init__(self, ID, tag)
        self.name = name


class Shops(object):
    def __init__(self, tag):
        self._shops = [shop for shop in tag if 'ShopProduction' in shop]

    def reset_shops_timer(self):
        for shop in self._shops:
            shop['ShopProduction']['@TimeA'].value = ZERO
            shop['ShopProduction']['@TimeB'].value = ZERO

    def __len__(self):
        return len(self._shops)


class Zone(object):
    def __init__(self, ID, name, clearables, foes, shops):
        self.ID = ID
        self.name = name
        self.clearable_items = clearables
        self.foes = foes
        self.shops = shops

    def cleared(self):
        return self.clearable_items.cleared() and self.foes.cleared()

    def clear(self):
        self.clearable_items.clear()
        self.foes.clear()

    def __repr__(self):
        return ('%s(ID: %s, Name: %s, Cleared: %s)'
                % (self.__class__.__name__,
                   self.ID,
                   self.name,
                   self.cleared()))
