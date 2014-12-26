#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: window.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from tkinter import Tk, Label, Button, Entry, StringVar, Frame
from tkinter.filedialog import askopenfilename
from tkinter.constants import N, S, E, W, NSEW

class Window(Tk):

    def __init__(self):
        super(Window, self).__init__()
        # self.geometry("450x250+300+300")
        self.grid()
        self.wm_title("Celestia Sunrise")
        self.resizable(False, False)
        self.bind('<Escape>', lambda _: self.destroy())

        self._create_variables()
        self._create_frames()
        self._create_widgets()
        self._grid_frames()
        self._grid_widgets()

    def _create_variables(self):
        self._filename = StringVar(self, "")
        self._gluid = StringVar(self, "")

    def _create_frames(self):
        self._disclaimer_frame = Frame(self)
        self._file_frame = Frame(self)
        self._key_frame = Frame(self)

    def _create_widgets(self):
        self._disclaimer_label1 = Label(self._disclaimer_frame,
                                        text='Your savegame is most likely called "mlp_save_prime.dat".')
        self._disclaimer_label2 = Label(self._disclaimer_frame,
                                        text="Make backups before using this tool.")

        self._file_label = Label(self._file_frame,
                                 text="Savegame file: ")
        self._file_entry = Entry(self._file_frame,
                                 textvariable=self._filename)
        self._file_button = Button(self._file_frame,
                                   text="Browse",
                                   command=lambda: self._filename.set(askopenfilename()))

        self._key_label = Label(self._key_frame,
                                text="Decryption key (GLUID): ")
        self._key_entry = Entry(self._key_frame,
                                textvariable=self._gluid)

        self._ok_button = Button(self,
                                 text="Go !",
                                 command=self._next)

    def _grid_frames(self):
        self._disclaimer_frame.grid(row=0, column=0, sticky=NSEW)
        self._file_frame.grid(row=1, column=0, pady=10, sticky=NSEW)
        self._key_frame.grid(row=2, column=0, pady=5, sticky=NSEW)

    def _grid_widgets(self):
        options = dict(sticky=W, padx=0, pady=2)
        self._disclaimer_label1.grid(row=0, column=0,
                                     **options)
        self._disclaimer_label2.grid(row=1, column=0,
                                     **options)

        options = dict(sticky=NSEW, padx=3, pady=4)
        self._file_label.grid(row=0, column=0, **options)
        self._file_entry.grid(row=0, column=1, **options)
        self._file_button.grid(row=0, column=2, **options)

        self._key_label.grid(row=0, column=0, **options)
        self._key_entry.grid(row=0, column=1, **options)

        self._ok_button.grid(row=3, column=0, **options)

    def _next(self):
        print(self._filename.get())
        print(self._gluid.get())
        self.destroy()
