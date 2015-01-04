#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: docstrings.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

SHOW = """Show what you requested.

Usage:
  show currencies
  show currency <currency_id>...
  show ponies [-i|-o]
  show pony <pony_id>...
  show zones
  show zone <zone_id>...

Arguments:
  currency_id   Id of a currency. Can be retrieved with "show currencies".
  pony_id       Id of a pony. Can be retrieved with "show ponies".
  zone_id       Id of a zone. Can be retrieved with "show zones".

Options:
  -i            Displays ponies in inventory.
  -o            Displays not owned ponies.
  -h --help     Show this help."""

SET = """Set what you requested.

Usage:
  set currency <value> <currency_id>...
  set ponies (level|shards) (up|down)
  set ponies (level|shards) <value>
  set ponies reset_game_timer
  set pony (level|shards) (up|down) <pony_id>...
  set pony (level|shards|next_game) <value> <pony_id>...
  set pony reset_game_timer <pony_id>...
  set zones clear [clearables|foes]
  set zones reset_shops_timer
  set zone clear [clearables|foes] <zone_id>...
  set zone reset_shops_timer <zone_id>...
  set inventory add <not_owned_pony_id>...

Arguments:
  currency_id           Id of a currency. Can be retrieved with "show currencies".
  pony_id               Id of a pony. Can be retrieved with "show ponies".
  zone_id               Id of a zone. Can be retrieved with "show zones".
  not_owned_pony_id     Id of a not owned pony. Can be retrieved with "show ponies -o".
  level value           An integer between 0 and 5.
  shards value          An integer between 0 and 10.
  next_game             One of Ball, Apple or Book.

Options:
  -h --help             Show this help."""

DUMP_XML = """Dump the actual XML tree.

Usage:
  dump_xml [<file>]

Arguments:
  file          If present, write to file instead of standard output.

Options:
  -h --help     Show this help."""

IMPORT_XML = """Import an XML tree. Use with caution.

Usage:
  import_xml <file>

Arguments:
  file          Path to a file containing an XML tree.

Options:
  -h --help     Show this help."""

WRITE_SAVE = """Write the current state of the save into a file

Usage:
  write_save <file> [<gluid>]
  write_save -l <file>

Arguments:
  file          Path to the new save file.
  gluid         GLUID used to encrypt the new save file. Must be base64 encoded.

Options:
  -l --legacy   Write a legacy save file (1.8.x version).
  -h --help     Show this help."""
