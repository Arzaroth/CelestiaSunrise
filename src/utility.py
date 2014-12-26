#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: utility.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from src.enum import enum
from collections import defaultdict

class InventoryPony(object):
    def __init__(self, tag):
        self.name = tag["@ID"][5:].replace('_', ' ')
        self.ID = tag["@ID"]
        self._tag = tag
        self.stored = True

    @property
    def _level(self):
        return min(max(int(self._tag["@PonyLevel"]), 0), 5)

    @property
    def _exp(self):
        return int(self._tag["@PonyCurrentEXP"])

    @property
    def _shards(self):
        return min(max(int(self._tag["@PonyShards"]), 0), 10)

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


class Pony(InventoryPony):

    GameTypes = enum(Ball=0, Apple=1, Book=2)

    def __init__(self, tag, actions):
        super(Pony, self).__init__(tag)
        self._leveltag = tag["Game"]["Level"]
        self._minigametag = tag["Game"]["MiniGame"]
        self._pony_actions = actions
        self.stored = False

    @InventoryPony._level.getter
    def _level(self):
        return min(max(int(self._leveltag["@Level"]), 0), 5)

    @InventoryPony._exp.getter
    def _exp(self):
        return int(self._leveltag["@CurrentEXP"])

    @InventoryPony._shards.getter
    def _shards(self):
        return min(max(int(self._leveltag["@Shards"]), 0), 10)

    @InventoryPony.level.setter
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
                    old_vals['ClearSkies'][k] = int(v[0]['@Value'])
                mod = new_val - old_vals['ClearSkies'][k]
                for i in v:
                    i['@Value'] = str((int(i['@Value']) + mod) if diff else new_val)
            for action in ('Complete', 'ItemSelected', 'Started'):
                for k, v in actions[action].items():
                    if not diff:
                        old_vals[action][k] = int(v[0]['@Value'])
                    mod = (new_val * 2) - old_vals[action][k]
                    for i in v:
                        i['@Value'] = str((int(i['@Value']) + mod) if diff else (new_val * 2))
            if not diff:
                old_vals['Complete']['All'] = int(actions['Complete']['All'][0]['@Value'])
            mod = (new_val * 2 * (len(Pony.GameTypes.map) + 1)) - old_vals['Complete']['All']
            for i in actions['Complete']['All']:
                i['@Value'] = str((int(i['@Value']) + mod) if diff else (new_val * 2 *
                                                                         (len(Pony.GameTypes.map) + 1)))
            return old_vals

        old_vals = update_action_values(self._pony_actions['Pony'], new_val)
        update_action_values(self._pony_actions['Global'], new_val, old_vals)
        self.shards = 0
        self._leveltag["@Level"] = str(new_val)

    @InventoryPony.shards.setter
    def shards(self, new_val):
        new_val = int(new_val)
        if new_val < 0 or new_val > 10:
            raise ValueError("Shards must be beetween 0 and 10")
        if self.level == 5 and new_val > 0:
            raise ValueError("Can't have shards at maximum level")
        self._leveltag["@Shards"] = str(new_val)

    @InventoryPony.next_game.getter
    def next_game(self):
        try:
            gametype = int(self._minigametag["@NextPlayAction"])
            name = Pony.GameTypes.rmap[gametype]
        except:
            name = 'Unknown'
        return name

    @next_game.setter
    def next_game(self, gametype):
        if gametype not in Pony.GameTypes.rmap:
            raise ValueError("Invalid game type")
        self._minigametag["@NextPlayAction"] = str(gametype)

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
        self._minigametag["@NextPlayTime"] = "0.000000"


class Currency(object):
    def __init__(self, name, tag, limit=-1):
        self.name = name
        self.limit = int(limit)
        self._tag = tag

    @property
    def value(self):
        return int(self._tag[self.name])

    @value.setter
    def value(self, new_val):
        new_val = int(new_val)
        if new_val < 0:
            raise ValueError("Can't set a negative currency value")
        if self.limit > 0 and new_val > self.limit:
            raise ValueError("Value above the limit")
        self._tag[self.name] = str(new_val)

    def __repr__(self):
        return ('%s(ID: %s, Value: %s)'
                % (self.__class__.__name__,
                   self.name,
                   self.value))


class Clearables(object):
    def __init__(self, ID, tag):
        self.ID = ID
        self.name = 'Clearable Objects'
        self._objects = [] if tag is None else tag['Object']
        if type(self._objects) != list:
            self._objects = [self._objects]

    def cleared(self):
        return not self._objects

    def clear(self):
        del self._objects[:]

    def __len__(self):
        return len(self._objects)

    def __repr__(self):
        return ('%s(ID: %s, Name: %s, Cleared: %s)'
                % (self.__class__.__name__,
                   self.ID,
                   self.name,
                   self.cleared()))


class Foes(Clearables):
    def __init__(self, ID, name, tag):
        super(Foes, self).__init__(ID, tag)
        self.name = name


class Zone(object):
    def __init__(self, ID, name, clearables, foes):
        self.ID = ID
        self.name = name
        self.clearable_items = clearables
        self.foes = foes

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
