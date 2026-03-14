from tkinter import *
from tkinter import ttk

BG = "#191919"
FG = "#ffffff"
FG_DIM = "#aaaaaa"

class Chart:
    def __init__(self, parent):
        self.parent = parent

        self.title = "Chart"
        self.geometry = "400x300"
        self.container = Frame(self.parent, bg=BG)
        self.container.pack(fill=BOTH, expand=True)
        self.frm0 = Frame(self.container, bg=BG)
        self.frm0.pack(side=TOP, fill=X, padx=8, pady=(4, 0))
        self.top_left = Label(self.frm0, text="% Utilization", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.top_right = Label(self.frm0, text="100%", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.top_left.pack(side=LEFT)
        self.top_right.pack(side=TOP, anchor=E)

        self.frm1 = Frame(self.container, bg=BG)
        self.frm1.pack(fill=BOTH, expand=True)
        self.chart = Canvas(self.frm1, width=400, height=300, bg="#0b0b0b", highlightthickness=0) # To be replaced by the actual chart
        self.chart.pack(fill=BOTH, expand=True)

        self.frm2 = Frame(self.container, bg=BG)
        self.frm2.pack(side=BOTTOM, fill=X, padx=8, pady=(0, 4))
        self.bottom_left = Label(self.frm2, text="60 seconds", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.bottom_right = Label(self.frm2, text="0", bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        self.bottom_left.pack(side=LEFT)
        self.bottom_right.pack(side=RIGHT)



if __name__ == "__main__":
    root = Tk()
    app = Chart(root)
    root.mainloop()