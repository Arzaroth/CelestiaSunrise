#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: xxtea.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#
# Deeply inspired by Yue Du <ifduyue@gmail.com>
# https://github.com/ifduyue/xxtea

from __future__ import print_function, absolute_import, unicode_literals, division
import sys
from itertools import islice, count
from struct import pack, unpack

def xrange(start, stop=None, step=1):
    if stop is None:
        stop = start
        start = 0
    return islice(count(start, step), (stop - start + step - 1 + 2 * (step < 0)) // step)

def str2longs(s):
    length = ((len(s) + 3) // 4) * 4
    s = s.ljust(length, b'\0')
    return [unpack('<I', s[i:i + 4])[0] for i in xrange(0, length, 4)]

def longs2str(s):
    return b''.join(pack('<I', c) for c in s)

DELTA = 0x9e3779b9
uint32 = lambda x: x & 0xffffffff

def btea(v, n, k):
    if (not isinstance(v, list) or
        not isinstance(n, int) or
        not isinstance(k, (list, tuple))):
        return False

    MX = lambda: ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ (sum ^ y) + (k[(p & 3) ^ e] ^ z)

    res = v[:]
    y = res[0]
    sum = 0
    if n > 1:
        z = res[n - 1]
        for _ in xrange(6 + 52 // n, 0, -1):
            sum = uint32(sum + DELTA)
            e = uint32(sum >> 2) & 3
            for p in xrange(n):
                y = res[p + 1] if p < n - 1 else res[0]
                z = res[p] = uint32(res[p] + MX())
    elif n < -1:
        n = -n
        q = 6 + 52 // n
        for sum in xrange(q * DELTA, 0, -DELTA):
            e = uint32(sum >> 2) & 3
            for p in xrange(n - 1, -1, -1):
                z = res[p - 1] if p > 0 else res[n - 1]
                y = res[p] = uint32(res[p] - MX())
    return res

def encrypt(data, key):
    key = key.ljust(16, b'\0')
    data = str2longs(data)
    key = str2longs(key)
    return longs2str(btea(data, len(data), key))

def decrypt(data, key):
    key = key.ljust(16, b'\0')
    data = str2longs(data)
    key = str2longs(key)
    return longs2str(btea(data, -len(data), key))
