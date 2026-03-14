from tkinter import *
from tkinter import ttk

class Sidebar:
    def __init__(self, parent):
        self.parent = parent
        self.frame = Frame(self.parent, bg="#2c2c2c", width=200)
        self.frame.pack(side=LEFT, fill=Y)

        self.label = Label(self.frame, text="Sidebar", bg="#2c2c2c", fg="white")
        self.label.pack(pady=10)
        # CPU, Memroy, Disk, GPU
        btn_cfg = {"bg": "#3a3a3a", "fg": "#ffffff", "font": ("Segoe UI", 10),
                   "relief": FLAT, "activebackground": "#4a4a4a", "activeforeground": "#ffffff",
                   "width": 14, "cursor": "hand2"}
        self.button1 = Button(self.frame, text="CPU", command=self.on_option_cpu, **btn_cfg)
        self.button1.pack(pady=5)

        self.button2 = Button(self.frame, text="Memory", command=self.on_option_memory, **btn_cfg)
        self.button2.pack(pady=5)

        self.button3 = Button(self.frame, text="Disk", command=self.on_option_disk, **btn_cfg)
        self.button3.pack(pady=5)

        self.button4 = Button(self.frame, text="GPU", command=self.on_option_gpu, **btn_cfg)
        self.button4.pack(pady=5)

    def on_option_cpu(self):
        self.parent.show_cpu()  # Call the method in MainWindow to update header, footer, and chart

    def on_option_memory(self):
        self.parent.show_memory()

    def on_option_disk(self):
        self.parent.show_disk()

    def on_option_gpu(self):
        self.parent.show_gpu()

if __name__ == "__main__":
    root = Tk()
    root.title("Sidebar Example")
    root.geometry("400x300")
    root.configure(bg="#1d1a1a")

    sidebar = Sidebar(root)

    root.mainloop()