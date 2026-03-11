from tkinter import *
from tkinter import ttk


class Chart:
    def __init__(self, parent):
        self.parent = parent

        self.title = "Chart"
        self.geometry = "400x300"
        self.container = Frame(self.parent)
        self.container.pack(fill=BOTH, expand=True)
        self.frm0 = Frame(self.container)
        self.frm0.pack(side=TOP, fill=X)
        self.top_left = Label(self.frm0, text="% Utilization")
        self.top_right = Label(self.frm0, text="100%")
        self.top_left.pack(side=LEFT)
        self.top_right.pack(side=TOP, anchor=E)

        self.frm1 = Frame(self.container)
        self.frm1.pack(fill=BOTH, expand=True)
        self.chart = Canvas(self.frm1, width=400, height=300, bg="grey") # To be replaced by the actual chart
        self.chart.pack(fill=BOTH, expand=True)

        self.frm2 = Frame(self.container)
        self.frm2.pack(side=BOTTOM, fill=X)
        self.bottom_left = Label(self.frm2, text="60 seconds")
        self.bottom_right = Label(self.frm2, text="0")
        self.bottom_left.pack(side=LEFT)
        self.bottom_right.pack(side=TOP, anchor=E)



if __name__ == "__main__":
    root = Tk()
    app = Chart(root)
    root.mainloop()