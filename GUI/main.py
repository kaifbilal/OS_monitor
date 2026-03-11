from tkinter import *
from tkinter import ttk
from sidebar import Sidebar
from header import Header
from chart import Chart
from footer import Footer

class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("OS Monitor")
        self.configure(bg="#191919")
        self.sidebar = Sidebar(self)
        self.header = Header(self)
        self.chart = Chart(self)
        self.footer = Footer(self)


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()