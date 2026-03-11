from tkinter import *
from tkinter import ttk
import random


class Footer:
    def __init__(self, parent):
        self.parent = parent
        self.geometry = "400x200"
        # Main container frame using pack
        self.container = Frame(self.parent, bg="lightgray")
        self.container.pack(fill=X)
        
        # Left section (frm0) - stats in columns
        self.frm0 = Frame(self.container, bg="lightgray")
        self.frm0.pack(side=LEFT)
        
        # Column 1 in frm0
        self.col1 = Frame(self.frm0, bg="lightgray")
        self.col1.pack(side=LEFT)
        
        self.utilzation_number = random.randint(0, 100)
        self.utilization_label = Label(self.col1, text="Utilization", bg="lightgray")
        self.utilization_label.pack(anchor=W)
        self.utilization_number_label = Label(self.col1, text=f"{self.utilzation_number}%", bg="lightgray")
        self.utilization_number_label.pack(anchor=W)
        
        self.processes_number = random.randint(0, 1000)
        self.processes_label = Label(self.col1, text="Processes", bg="lightgray")
        self.processes_label.pack(anchor=W, pady=(5, 0))
        self.processes_number_label = Label(self.col1, text=f"{self.processes_number}", bg="lightgray")
        self.processes_number_label.pack(anchor=W)
        
        self.upTime_number = "0:00:00:00"
        self.upTime_label = Label(self.col1, text="Up Time", bg="lightgray")
        self.upTime_label.pack(anchor=W, pady=(5, 0))
        self.upTime_number_label = Label(self.col1, text=f"{self.upTime_number}", bg="lightgray")
        self.upTime_number_label.pack(anchor=W)
        
        # Column 2 in frm0
        self.col2 = Frame(self.frm0, bg="lightgray")
        self.col2.pack(side=LEFT, padx=10)
        
        self.speed_label = Label(self.col2, text="Speed", bg="lightgray")
        self.speed_label.pack(anchor=W)
        self.speed_number_label = Label(self.col2, text=f"{random.randint(0, 100)} GHz", bg="lightgray")
        self.speed_number_label.pack(anchor=W)
        
        self.thread_label = Label(self.col2, text="Threads", bg="lightgray")
        self.thread_label.pack(anchor=W, pady=(5, 0))
        self.thread_number_label = Label(self.col2, text=f"{random.randint(0, 3000)}", bg="lightgray")
        self.thread_number_label.pack(anchor=W)
        
        # Column 3 in frm0
        self.col3 = Frame(self.frm0, bg="lightgray")
        self.col3.pack(side=LEFT, padx=10)
        
        self.Handles_label = Label(self.col3, text="Handles", bg="lightgray")
        self.Handles_label.pack(anchor=W, pady=(5, 0))
        self.Handles_number_label = Label(self.col3, text=f"{random.randint(0, 200000)}", bg="lightgray")
        self.Handles_number_label.pack(anchor=W)
        
        # Right section (frm1) - system details in rows
        self.frm1 = Frame(self.container, bg="lightgray")
        self.frm1.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Create rows for each stat
        self._create_stat_row(self.frm1, "Base Speed:", f"{random.randint(0, 100)} GHz", "BS")
        self._create_stat_row(self.frm1, "Sockets:", f"{random.randint(0, 4)}", "sockets")
        self._create_stat_row(self.frm1, "Cores:", f"{random.randint(0, 16)}", "cores")
        self._create_stat_row(self.frm1, "Logical Processors:", f"{random.randint(0, 32)}", "logical_processors")
        self._create_stat_row(self.frm1, "Virtualization:", f"{random.choice(['Enabled', 'Disabled'])}", "Virtualization")
        self._create_stat_row(self.frm1, "L1 Cache:", f"{random.randint(0, 256)} KB", "l1_cache")
        self._create_stat_row(self.frm1, "L2 Cache:", f"{random.randint(0, 2048)} KB", "l2_cache")
        self._create_stat_row(self.frm1, "L3 Cache:", f"{random.randint(0, 32768)} KB", "l3_cache")
    
    def _create_stat_row(self, parent, label_text, value_text, attr_prefix):
        """Helper to create a row with label and value"""
        row = Frame(parent, bg="lightgray")
        row.pack(fill=X, pady=1)
        
        label = Label(row, text=label_text, bg="lightgray")
        label.pack(side=LEFT)
        
        value = Label(row, text=value_text, bg="lightgray")
        value.pack(side=LEFT, padx=(5, 0))
        
        # Store references
        setattr(self, f"{attr_prefix}_label", label)
        setattr(self, f"{attr_prefix}_number_label", value)


if __name__ == "__main__":
    root = Tk()
    root.geometry("400x200")
    footer = Footer(root)
    root.mainloop()