#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: xxtea.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#
# Deeply inspired by Yue Du <ifduyue@gmail.com>
# https://github.com/ifduyue/xxtea

from __future__ import division
import sys
from struct import pack, unpack

try:
    xrange
except NameError:
    xrange = range

def str2longs(s):
    length = ((len(s) + 3) // 4) * 4
    s = s.ljust(length, b'\0')
    return [unpack('<I', s[i:i + 4])[0] for i in xrange(0, length, 4)]

def longs2str(s):
    return b''.join(pack('<I', c) for c in s).rstrip(b'\0')

DELTA = 0x9e3779b9
uint32 = lambda x: x & 0xffffffff

def btea(v, n, k):
    if (not isinstance(v, list) or
        not isinstance(n, int) or
        not isinstance(k, (list, tuple))):
        return False

    MX = lambda: ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ (sum ^ y) + (k[(p & 3) ^ e] ^ z)

    y = v[0]
    sum = 0
    if n > 1:
        z = v[n - 1]
        for _ in range(6 + 52 // n, 0, -1):
            sum = uint32(sum + DELTA)
            e = uint32(sum >> 2) & 3
            p = 0
            while p < n - 1:
                y = v[p + 1]
                z = v[p] = uint32(v[p] + MX())
                p += 1
            y = v[0]
            z = v[n - 1] = uint32(v[n - 1] + MX())
        return True
    elif n < -1:
        n = -n
        q = 6 + 52 // n
        for sum in range(q * DELTA, 0, -DELTA):
            e = uint32(sum >> 2) & 3
            p = n - 1
            while p > 0:
                z = v[p - 1]
                y = v[p] = uint32(v[p] - MX())
                p -= 1
            z = v[n - 1]
            y = v[0] = uint32(v[0] - MX())
        return True
    return False

def encrypt(str, key):
    key = key.ljust(16, b'\0')
    v = str2longs(str)
    k = str2longs(key)
    n = len(v)
    btea(v, n, k)
    result = longs2str(v)
    return result

def decrypt(s, key):
    key = key.ljust(16, b'\0')
    v = str2longs(s)
    k = str2longs(key)
    n = len(v)
    btea(v, -n, k)
    return longs2str(v)
