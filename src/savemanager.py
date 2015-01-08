#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: savemanager.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals
import zlib
import struct
import src.utility.xxtea as xxtea

class SaveError(Exception):
    pass


def read_or_raise(file, size):
    data = file.read(size)
    if len(data) != size:
        raise SaveError("Unable to read, truncated or corrupted file")
    return data

class SaveManager(object):
    SECTIONS = 2

    def __init__(self, filename, gluid=b''):
        self.filename = filename
        self.gluid = gluid

    def _save_buffer(self, data, file, gluid=None):
        crc_res = zlib.crc32(data) & 0xffffffff
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
            raise SaveError("Unable to decompress data, truncated or corrupted file, or bad decryption key")
        if len(res) != uncompress_size:
            raise SaveError("Invalid inflated data")
        crc_res = zlib.crc32(res) & 0xffffffff
        if crc_res != crc_value:
            raise SaveError("crc mismatch")
        return res

    def load(self, legacy=False):
        try:
            with open(self.filename, 'rb') as file:
                print('Loading save.', end='')
                if legacy:
                    results = [decompress_data(file.read())]
                    print('.', end='')
                else:
                    file.seek(-4, 2)
                    if struct.unpack('I', read_or_raise(file, 4))[0] != SaveManager.SECTIONS:
                        raise SaveError("Invalid sections number, truncated or corrupted file")
                    print('.', end='')
                    file.seek(0, 0)
                    results = [self._load_buffer(file) for _ in range(SaveManager.SECTIONS)]
                print('.\nDone !')
        except Exception as e:
            raise SaveError(str(e))
        save_number = struct.unpack('I', results[0])[0] if len(results) > 1 else 10
        return results[-1], save_number

    def save(self, data, filename, save_number=10,
             gluid=None, legacy=False):
        try:
            with open(filename, 'wb') as file:
                print('Writing save.', end='')
                if legacy:
                    file.write(data)
                    print('.', end='')
                else:
                    self._save_buffer(struct.pack('I', save_number), file, gluid)
                    print('.', end='')
                    self._save_buffer(data, file, gluid)
                    print('.', end='')
                    file.write(struct.pack('I', SaveManager.SECTIONS))
                print('.\nDone !')
        except Exception as e:
            raise SaveError(str(e))


def decompress_data(data):
    res = zlib.decompress(data[16:])
    uncompress_size, compress_size = struct.unpack('2I', data[:8])
    if len(res) != uncompress_size or len(data[16:]) != compress_size:
        raise SaveError("Invalid inflated data")
    return res

def compress_data(data):
    compressed_data = zlib.compress(data)
    res = struct.pack('4I', len(data), len(compressed_data), 0, 0)
    res += compressed_data
    return res
