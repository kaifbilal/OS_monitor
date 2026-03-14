from tkinter import *
from tkinter import ttk
import random


BG = "#191919"
FG = "#ffffff"
FG_DIM = "#aaaaaa"

class Footer:
    def __init__(self, parent):
        self.parent = parent
        self.geometry = "400x200"
        self.create_footer()
    
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


        # frame
        self.frm1 = Frame(self.container, bg=BG)
        self.frm1.pack(side=LEFT, fill=BOTH, expand=True)

    def setup_cpu(self):
        self.reset() # Clear previous stats
        # create columns inside row1
        self._create_stat_label(self.row1, "Utilization", "%")
        self._create_stat_label(self.row1, "Speed", " GHz")
        # row 2 in frm0
        self._create_stat_label(self.row2, "Processes")
        self._create_stat_label(self.row2, "Threads")
        self._create_stat_label(self.row2, "Handles")
        #row 3 in frm0
        # row 3 in frm0
        self.row3 = Frame(self.frm0, bg=BG)
        self.row3.pack(side=TOP, pady=10, fill=X)
        self._create_stat_label(self.row3, "Up Time", "0:00:00:00")
        

        # Create rows for each stat
        self._create_stat_row(self.frm1, "Base Speed:", f"{random.randint(0, 100)} GHz", "BS")
        self._create_stat_row(self.frm1, "Sockets:", f"{random.randint(0, 4)}", "sockets")
        self._create_stat_row(self.frm1, "Cores:", f"{random.randint(0, 16)}", "cores")
        self._create_stat_row(self.frm1, "Logical Processors:", f"{random.randint(0, 32)}", "logical_processors")
        self._create_stat_row(self.frm1, "Virtualization:", f"{random.choice(['Enabled', 'Disabled'])}", "Virtualization")
        self._create_stat_row(self.frm1, "L1 Cache:", f"{random.randint(0, 256)} KB", "l1_cache")
        self._create_stat_row(self.frm1, "L2 Cache:", f"{random.randint(0, 2048)} KB", "l2_cache")
        self._create_stat_row(self.frm1, "L3 Cache:", f"{random.randint(0, 32768)} KB", "l3_cache")

    def setup_memory(self):
        self.reset()
        # stat_labels
        self._create_stat_label(self.row1, "In use (Compressed)", [" GB (", " MB)"])
        self._create_stat_label(self.row1, "Available", " GB")
        self._create_stat_label(self.row2, "Committed", ["/", " GB"])
        self._create_stat_label(self.row2, "Cached", " GB")
        
        # row 3 in frm0
        self.row3 = Frame(self.frm0, bg=BG)
        self.row3.pack(side=TOP, pady=10, fill=X)
        self._create_stat_label(self.row3, "Paged pool", " MB")
        self._create_stat_label(self.row3, "Non-paged pool", " MB")

        # stat rows
        self._create_stat_row(self.frm1, "Speed:", f"{random.randint(1000, 4000)}"," MT/s") # speed: 3200 MT/s
        self._create_stat_row(self.frm1, "Slots used:", f"{random.randint(1,3)} of 2")# slots used:  2 0f 2
        self._create_stat_row(self.frm1, "Form factor:", "Row of chips")# form factor: row of chips
        self._create_stat_row(self.frm1, "Hardware reserved:", f"{random.randint(200, 300)}", " MB")# Hardware reserved: 261 MB

    def setup_disk(self):
        self.reset()
        #label
        # active time. %
        #average response time ms
        # read speeed KB/s
        # write speed KB/s
        self._create_stat_label(self.row1, "Active time: ", " %")
        self._create_stat_label(self.row1, "Average response time: ", " ms")
        self._create_stat_label(self.row2, "Read speed: ", " KB/s")
        self._create_stat_label(self.row2, "Write speed: ", " KB/s")
        # 
        # row
        # capacity: GB
        # formatted: GB
        # System disk: Yes/No
        # Page file: Yes/no
        # Type: SSD(NVMe)#
        self._create_stat_row(self.frm1, "Capacity:", f"{random.randint(128, 2048)}", " GB")
        self._create_stat_row(self.frm1, "Formatted:", f"{random.randint(128, 2048)}", " GB")
        self._create_stat_row(self.frm1, "System disk:", random.choice(["Yes", "No"]))
        self._create_stat_row(self.frm1, "Page file:", random.choice(["Yes", "No"]))
        self._create_stat_row(self.frm1, "Type:", random.choice(["SSD", "HDD"]))
    
    def setup_gpu(self):
        self.reset() # Clear previous stats
        # label
        # 
        # Utilization %
        # Shared GPU memory 0.2/3.9 GB
        # GPU Memory 0.2/3.9 GB 
        self._create_stat_label(self.row1, "Utilization: ", " %")
        self._create_stat_label(self.row1, "Shared GPU memory: ", " GB")
        self._create_stat_label(self.row2, "GPU Memory: ", " GB")
        # 
        # row
        # Driver version: 31.0.101.2125
        # Driver date: 24-05-2023
        # DirectX version: 12 (FL 12.1)
        # Physical location: PCI bus 0, device 2, function 0#
        self._create_stat_row(self.frm1, "Driver version:", f"{random.randint(20, 40)}.{random.randint(0, 9)}.{random.randint(0, 999)}.{random.randint(1000, 9999)}")
        self._create_stat_row(self.frm1, "Driver date:", f"{random.randint(1, 31)}-{random.randint(1, 12)}-{random.randint(2020, 2024)}")
        self._create_stat_row(self.frm1, "DirectX version:", f"{random.randint(9, 12)} (FL {random.randint(9, 12)}.{random.randint(0, 2)})")
        self._create_stat_row(self.frm1, "Physical location:", f"PCI bus {random.randint(0, 3)}, device {random.randint(0, 15)}, function {random.randint(0, 7)}")

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

        self.random_number = random.randint(0, 100) # To be replaced by actual data
        hlabel = Label(col, text=htext, bg=BG, fg=FG_DIM, font=("Segoe UI", 9))
        hlabel.pack(anchor=W, padx=12, pady=(0, 2))
        if type(ltext) == str:
            ltext = [ltext]
        row = Frame(col, bg=BG)
        row.pack(anchor=W, padx=12, pady=(0, 2))
        for text in ltext:
            self.random_number = random.randint(0, 100) # To be replaced by actual data
            vlabel = Label(row, text=f"{self.random_number}{text}", bg=BG, fg=FG, font=("Segoe UI", 10, "bold"), padx=0, pady=0, bd=0, highlightthickness=0)
            vlabel.pack(side=LEFT, padx=0)

        # return references in case caller wants them
        return hlabel, vlabel

    def reset(self):
        # Clear all stat labels and rows
        
        # for widget in self.frm0.winfo_children():
        #     widget.destroy()
        # for widget in self.frm1.winfo_children():
        #     widget.destroy()
        self.container.destroy()
        self.create_footer() # Recreate the footer structure after clearing


if __name__ == "__main__":
    root = Tk()
    root.configure(bg=BG)
    footer = Footer(root)
    # footer.setup_cpu()
    # footer.setup_memory()
    # footer.setup_disk()
    footer.setup_gpu()
    root.mainloop()