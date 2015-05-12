#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: threaded.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

import threading
try:
    # py3
    import queue as Queue
except ImportError:
    # py2
    import Queue
from celestia.save import SaveManager, SaveError
from celestia.save import decompress_data, compress_data
from celestia.xml.xmlhandler import XmlHandler

class ThreadedLoad(threading.Thread):
    def __init__(self, queue, savedata, xml=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.savedata = savedata
        self.xml = xml

    def run(self):
        res = {
            "error": None,
        }
        if not self.xml:
            save_manager = SaveManager(self.savedata.savefile,
                                       self.savedata.gluid)
            try:
                data, save_number = save_manager.load(self.savedata.legacy)
                if not self.savedata.legacy:
                    data = decompress_data(data)
            except Exception as e:
                res["error"] = e
            else:
                res["save_manager"] = save_manager
                res["save_number"] = save_number
        else:
            try:
                with open(self.xml, 'rb') as f:
                    data = f.read()
            except Exception as e:
                res["error"] = e
        if not res["error"]:
            xml_handle = XmlHandler(data)
            xml_handle.pre_load()
            res["xml_handle"] = xml_handle
        self.queue.put(res)

def process_loadqueue(instance, loadingbox, queue,
                      success_callback, error_callback=None):
    try:
        res = queue.get_nowait()
    except Queue.Empty:
        instance.after(100, process_loadqueue,
                       instance, loadingbox, queue,
                       success_callback, error_callback)
    else:
        loadingbox.destroy()
        if res["error"]:
            showerror("Error",
                      "Was unable to load from file, reason: {}".format(str(error)))
            if error_callback:
                error_callback()
        else:
            success_callback(res)
