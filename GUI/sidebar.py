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
        self.button1 = Button(self.frame, text="CPU", command=self.on_option1_click)
        self.button1.pack(pady=5)

        self.button2 = Button(self.frame, text="Memory", command=self.on_option2_click)
        self.button2.pack(pady=5)

        self.button3 = Button(self.frame, text="Disk", command=self.on_option1_click)
        self.button3.pack(pady=5)

        self.button4 = Button(self.frame, text="GPU", command=self.on_option1_click)
        self.button4.pack(pady=5)

    def on_option1_click(self):
        print("Option 1 clicked!")

    def on_option2_click(self):
        print("Option 2 clicked!")


if __name__ == "__main__":
    root = Tk()
    root.title("Sidebar Example")
    root.geometry("400x300")
    root.configure(bg="#1d1a1a")

    sidebar = Sidebar(root)

    root.mainloop()