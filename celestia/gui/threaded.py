#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: threaded.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

import threading
import requests
import shutil
import os
try:
    # py3
    import queue as Queue
    from tkinter.messagebox import showerror
except ImportError:
    # py2
    import Queue
    from tkMessageBox import showerror
from celestia.save import SaveManager, SaveError
from celestia.save import decompress_data, compress_data
from celestia.xml.xmlhandler import XmlHandler
from celestia.utility.version import get_script_name, check_version

class ThreadedBase(threading.Thread):
    def __init__(self, queue, savedata=None, pre_func=None):
        threading.Thread.__init__(self,
                                  target=self.worker, args=(queue,))
        self.pre_func = pre_func
        self.savedata = savedata

    def worker(self, queue):
        if self.pre_func:
            self.pre_func()


class ThreadedLoad(ThreadedBase):
    def __init__(self, queue, savedata, xml=None, pre_func=None):
        ThreadedBase.__init__(self, queue, savedata, pre_func)
        self.xml = xml

    def worker(self, queue):
        ThreadedBase.worker(self, queue)
        res = {
            "error": None,
        }
        try:
            if not self.xml:
                save_manager = SaveManager(self.savedata.savefile,
                                           self.savedata.gluid)
                data, save_number = save_manager.load(self.savedata.legacy)
                if not self.savedata.legacy:
                    data = decompress_data(data)
                res["save_manager"] = save_manager
                res["save_number"] = save_number
            else:
                with open(self.xml, 'rb') as f:
                    data = f.read()
        except Exception as e:
            res["error"] = e
        if not res["error"]:
            xml_handle = XmlHandler(data)
            xml_handle.pre_load()
            res["xml_handle"] = xml_handle
        res["done"] = True
        queue.put(res)


class ThreadedSave(ThreadedBase):
    def __init__(self, queue, savedata,
                 xml_handle, save_manager, save_number,
                 xml=None, pre_func=None):
        ThreadedBase.__init__(self, queue, savedata, pre_func)
        self.savedata = savedata
        self.xml_handle = xml_handle
        self.save_manager = save_manager
        self.save_number = save_number
        self.xml = xml

    def worker(self, queue):
        ThreadedBase.worker(self, queue)
        res = {
            "error": None,
        }
        try:
            if not self.xml:
                self.save_manager.save(compress_data(self.xml_handle.to_string()),
                                       self.savedata.savefile,
                                       self.save_number,
                                       self.savedata.gluid,
                                       self.savedata.legacy)
            else:
                with open(self.xml, 'wb') as f:
                    f.write(self.xml_handle.prettify())
        except Exception as e:
            res["error"] = e
        res["done"] = True
        queue.put(res)


class ThreadedVersionCheck(ThreadedBase):
    def worker(self, queue):
        ThreadedBase.worker(self, queue)
        res = check_version()
        res["done"] = True
        queue.put(res)


class ThreadedVersionDownload(ThreadedBase):
    def __init__(self, progress_queue, download_url, filename, cancel_queue):
        ThreadedBase.__init__(self, progress_queue)
        self.download_url = download_url
        self.filename = filename
        self.cancel_queue = cancel_queue

    def worker(self, queue):
        ThreadedBase.worker(self, queue)
        res = {
            "error": None,
            "total": 0,
            "current": 0,
            "done": False
        }
        partfile = "{}.part".format(self.filename)
        try:
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            res["total"] = int(response.headers.get('content-length') or 0)
            queue.put(res)
            with open(partfile, 'wb') as tmp:
                if not res["total"]:
                    tmp.write(response.content)
                else:
                    for chunk in response.iter_content(1024):
                        try:
                            cancel = self.cancel_queue.get_nowait()
                            raise RuntimeError("The download was canceled.")
                        except Queue.Empty:
                            pass
                        res["current"] += len(chunk)
                        tmp.write(chunk)
                        queue.put(res)
            shutil.copy(partfile, self.filename)
        except Exception as e:
            res["error"] = e
        finally:
            os.unlink(partfile)
        res["done"] = True
        queue.put(res)


def process_queue(instance, queue, loadingbox=None,
                  success_callback=None, error_callback=None,
                  process_callback=None, show_error=True):
    empty = False
    try:
        res = queue.get_nowait()
    except Queue.Empty:
        res = {"done": False}
        empty = True
    if not res["done"]:
        if process_callback and not empty:
            process_callback(res)
        instance.after(100, process_queue,
                       instance, queue, loadingbox,
                       success_callback, error_callback,
                       process_callback, show_error)
    else:
        if loadingbox is not None:
            loadingbox.destroy()
        if res["error"]:
            if show_error:
                showerror("Error", str(res["error"]))
            if error_callback:
                error_callback()
        elif success_callback:
            success_callback(res)
