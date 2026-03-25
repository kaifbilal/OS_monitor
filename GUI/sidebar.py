from tkinter import *
from tkinter import ttk

class Sidebar:
    def __init__(self, parent):
        self.parent = parent
        self.frame = Frame(self.parent, bg="#2c2c2c", width=200)
        self.frame.pack(side=LEFT, fill=Y)

        self.label = Label(self.frame, text="Sidebar", bg="#2c2c2c", fg="white")
        self.label.pack(pady=10)
        # CPU, Memroy, Disk, GPU, WiFi
        btn_cfg = {"bg": "#3a3a3a", "fg": "#ffffff", "font": ("Segoe UI", 10),
                   "relief": FLAT, "activebackground": "#4a4a4a", "activeforeground": "#ffffff",
                   "width": 14, "cursor": "hand2"}
        self.button1 = Button(self.frame, text="CPU", command=lambda: self.parent.show_page("CPU"), **btn_cfg)
        self.button1.pack(pady=5)

        self.button2 = Button(self.frame, text="Memory", command=lambda: self.parent.show_page("Memory"), **btn_cfg)
        self.button2.pack(pady=5)

        self.button3 = Button(self.frame, text="Disk", command=lambda: self.parent.show_page("Disk"), **btn_cfg)
        self.button3.pack(pady=5)

        self.button4 = Button(self.frame, text="GPU", command=lambda: self.parent.show_page("GPU"), **btn_cfg)
        self.button4.pack(pady=5)

        self.button5 = Button(self.frame, text="WiFi", command=lambda: self.parent.show_page("WiFi"), **btn_cfg)
        self.button5.pack(pady=5)


if __name__ == "__main__":
    root = Tk()
    root.title("Sidebar")
    root.geometry("400x300")
    root.configure(bg="#1d1a1a")

    sidebar = Sidebar(root)

    root.mainloop()