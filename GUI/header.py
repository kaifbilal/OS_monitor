from tkinter import *

BG = "#191919"
FG = "#ffffff"

class Header():
    def __init__(self, parent):
        self.parent = parent

        self.frm = Frame(self.parent, bg=BG)
        self.frm.pack(fill=X, padx=10, pady=6)
        self.screen_name = ""
        self.screen_name_label = Label(self.frm, text=self.screen_name, bg=BG, fg=FG, font=("Segoe UI", 18, "bold"))

        self.screen_info = ""
        self.screen_info_label = Label(self.frm, text=self.screen_info, bg=BG, fg="#aaaaaa", font=("Segoe UI", 10))

        self.screen_name_label.pack(side=LEFT)
        self.screen_info_label.pack(side=RIGHT, padx=(10, 0))
    
    def update_info(self, name, info):
        self.screen_name = name
        self.screen_info = info
        self.screen_name_label.config(text=self.screen_name)
        self.screen_info_label.config(text=self.screen_info)



if __name__ == "__main__":
    root = Tk()
    root.configure(bg=BG)
    header = Header(root)
    root.mainloop()