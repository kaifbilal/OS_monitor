from tkinter import *
from tkinter import ttk



BG = "#191919"
FG = "#ffffff"
FG_DIM = "#aaaaaa"

class Footer:
    def __init__(self, parent):
        self.parent = parent
        self.geometry = "400x200"
        self.create_footer()
        self._element_dictionary = {} # Store references to label widgets for dynamic updates
        self.flag = {
            "CPU": False,
            "Memory": False,
            "Disk": False,
            "GPU": False,
            "WiFi": False
        }

    def create_footer(self):
        # Main container frame using pack
        self.container = Frame(self.parent, bg=BG)
        self.container.pack(fill=X)


        # Left section (frm0) - stats in columns
        self.frm0 = Frame(self.container, bg=BG)
        self.frm0.pack(side=LEFT, fill=X)

        # row 1 in frm0 (stacked vertically)
        self.row1 = Frame(self.frm0, bg=BG)
        self.row1.pack(side=TOP, fill=X)

        self.row2 = Frame(self.frm0, bg=BG)
        self.row2.pack(side=TOP, pady=10, fill=X)


        # row 3 in frm0
        self.row3 = Frame(self.frm0, bg=BG)
        self.row3.pack(side=TOP, pady=10, fill=X)

        # frame
        self.frm1 = Frame(self.container, bg=BG)
        self.frm1.pack(side=LEFT, fill=BOTH, expand=True)
        
    def setup_footer(self, dictionary):
        # dictionary = {
        #     "label": ("Unit", position)"
        #     "Base Speed": ("GHz", "row1"),
        # }
        for key, (unit, position) in dictionary.items():
            if position == "row1":
                self._element_dictionary[key] = self._create_stat_label(self.row1, key, unit)
            elif position == "row2":
                self._element_dictionary[key] = self._create_stat_label(self.row2, key, unit)
            elif position == "row3":
                self._element_dictionary[key] = self._create_stat_label(self.row3, key, unit)
        return self._element_dictionary

    def update_footer(self, dictionary):
        # dictionary = {
        #     "label": ("value", position)"
        #     "Base Speed": ("1.19", "row1"),
        # }
        for key, (unit, position) in dictionary.items():
            label_attr = f"{position}_label"
            number_label_attr = f"{position}_number_label"
            if hasattr(self, label_attr) and hasattr(self, number_label_attr):
                label_widget = getattr(self, label_attr)
                number_label_widget = getattr(self, number_label_attr)
                label_widget.config(text=key)
                number_label_widget.config(text=f"") # Replace with actual data retrieval logic

    def _create_stat_row(self, parent, label_text, value_text, attr_prefix=""):
        """Helper to create a row with label and value"""
        row = Frame(parent, bg=BG)
        row.pack(fill=X, pady=1)

        label = Label(row, text=label_text, bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        label.pack(side=LEFT)

        value = Label(row, text=value_text, bg=BG, fg=FG, font=("Segoe UI", 9))
        value.pack(side=LEFT, padx=(5, 0))

        # Store references
        setattr(self, f"{attr_prefix}_label", label)
        setattr(self, f"{attr_prefix}_number_label", value)

    def _create_stat_label(self, parent, htext="", ltext=""):
        """Create a stat column inside the provided row parent.
        Packs a small column frame side-by-side with others in the same row."""
        col = Frame(parent, bg=BG)
        col.pack(side=LEFT, padx=10)
        hlabel = Label(col, text=htext, bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        hlabel.pack(anchor=W, padx=12, pady=(0, 2))
        if type(ltext) == str:
            ltext = [ltext]
        row = Frame(col, bg=BG)
        row.pack(anchor=W, padx=12, pady=(0, 2))
        for text in ltext:
            vlabel = Label(row, text=f"{text}", bg=BG, fg=FG, font=("Segoe UI", 10, "bold"), padx=0, pady=0, bd=0, highlightthickness=0)
            vlabel.pack(side=LEFT, padx=0)

        return hlabel, vlabel

    def static_value_setter(self, dictionary):
        """Takes input in the form of: dictionary, and create static rows"""        
        for key, value in dictionary.items():
            self._create_stat_row(self.frm1, f"{key}:", f"{value}")
    
    def dynamic_value_setter(self, dictionary):
        """Takes input in the form of: dictionary, and create dynamic rows"""
        for key, value in dictionary.items():
            if key not in self._element_dictionary:
                continue
            self._element_dictionary[key][1].config(text=f"{value}")



if __name__ == "__main__":
    root = Tk()
    root.configure(bg=BG)
    footer = Footer(root)
    root.mainloop()