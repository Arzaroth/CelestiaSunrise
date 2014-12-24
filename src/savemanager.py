#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: savemanager.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function
import zlib
import struct
import src.xxtea as xxtea

def read_or_raise(file, size):
    data = file.read(size)
    if len(data) != size:
        raise SaveError("Unable to read, truncated or corrupted file")
    return data

class SaveError(Exception):
    pass


class SaveManager(object):
    def __init__(self, filename, gluid):
        self.filename = filename
        self._sections = 0
        self.results = []
        self.gluid = gluid

    def _save_buffer(self, data, file, gluid=None):
        crc_res = zlib.crc32(data)
        uncompress_size = len(data)
        decrypt_data = zlib.compress(data)
        crc_offset = len(decrypt_data) + 4
        decrypt_data += struct.pack('I', crc_res)
        raw_data = xxtea.encrypt(decrypt_data,
                                 self.gluid if gluid is None else gluid)
        data_size = len(raw_data)
        file.write(struct.pack('3I', uncompress_size, crc_offset, data_size))
        file.write(raw_data)

    def _load_buffer(self, file):
        metadata = read_or_raise(file, 12)
        uncompress_size, crc_offset, data_size = struct.unpack('3I', metadata)
        if crc_offset > data_size:
            raise SaveError("Bad size or crc_offset")
        raw_data = read_or_raise(file, data_size)
        decrypt_data = xxtea.decrypt(raw_data,
                                     self.gluid)
        crc_value = struct.unpack('I', decrypt_data[crc_offset - 4:crc_offset])[0]
        try:
            res = zlib.decompress(decrypt_data)
        except zlib.error as e:
            raise SaveError(str(e))
        else:
            self.results.append(res)
        if len(res) != uncompress_size:
            raise SaveError("Invalid inflated data")
        crc_res = zlib.crc32(res)
        if crc_res != crc_value:
            raise SaveError("crc mismatch")

    def load(self):
        try:
            with open(self.filename, 'rb') as file:
                print('Loading save.', end='')
                file.seek(-4, 2)
                self._sections = struct.unpack('I', read_or_raise(file, 4))[0]
                print('.', end='')
                file.seek(0, 0)
                self.results = []
                for i in range(self._sections):
                    self._load_buffer(file)
                    print('.', end='')
                print('\nDone !')
        except Exception as e:
            raise SaveError(str(e))
        return self.results[-1]

    def save(self, data, filename, gluid=None):
        if not self._sections:
            raise SaveError("Load before save in order to get a correct chunk data")
        try:
            with open(filename, 'wb') as file:
                print('Writing save.', end='')
                for i in range(self._sections - 1):
                    self._save_buffer(self.results[i], file, gluid)
                    print('.', end='')
                self._save_buffer(data, file, gluid)
                print('.', end='')
                file.write(struct.pack('I', self._sections))
                print('.\nDone !')
        except Exception as e:
            raise SaveError(str(e))


def decompress_data(data):
    try:
        res = zlib.decompress(data[16:])
    except zlib.error as e:
        raise SaveError(str(e))
    uncompress_size, compress_size = struct.unpack('2I', data[:8])
    if len(res) != uncompress_size or len(data[16:]) != compress_size:
        raise SaveError("Invalid inflated data")
    return res

def compress_data(data):
    compressed_data = zlib.compress(data)
    res = struct.pack('4I', len(data), len(compressed_data), 0, 0)
    res += compressed_data
    return res
