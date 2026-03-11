from tkinter import *

class Header():
    def __init__(self, parent):
        self.parent = parent

        self.frm = Frame(self.parent)
        self.frm.pack(fill=X)
        self.screen_name = "CPU"
        self.screen_name_label = Label(self.frm, text=self.screen_name)

        self.screen_info = "Intel(R) Core(TM) i3-100"
        self.screen_info_label = Label(self.frm, text=self.screen_info)

        self.screen_name_label.pack(side=LEFT)
        self.screen_info_label.pack(side=TOP, anchor=E)
