from GUI.footer import Footer
from GUI.header import Header
from GUI.chart import Chart
from tkinter import *

class MemoryPage(Frame):
        def __init__(self, parent):
                super().__init__(parent)
                self.configure(bg="#191919")
                self.header = Header(self)
                self.chart = Chart(self)
                self.footer = Footer(self)

        def get_stats(self):
                self._stats_dictionary = {"header": ("Memory", "16 GB"),
                "footer": {
                        "In use (Compressed)": ("GB (MB)", "row1"),
                        "In use": ("GB", "row1"),
                        "Compressed": ("MB", "row1"),
                        "Available": ("GB", "row1"),
                        "Committed": ("/ GB", "row2"),
                        "Cached": ("GB", "row2"),
                        "Paged pool": ("MB", "row3"),
                        "Non-paged pool": ("MB", "row3"),
                        "memory composition": ("", "row3"),
                                        },
                "footer_static":{ 
                        "Speed:": (f"3200", " MT/s"),
                        "Slots used:": (f"2 of 2", ""),                                        "Form factor:": ("Row of chips", ""),
                        "Hardware reserved:": (f"261", " MB"),
                        },
                }
                return self._stats_dictionary
        
        def setup_static(self):
                dictionary = self.get_stats()
                name, info = dictionary["header"]
                self.header.update_info(name, info)
                self.footer.setup_footer(dictionary["footer"])
                for label, (value, unit) in dictionary["footer_static"].items():
                        self.footer._create_stat_row(self.footer.frm1, label, f"{value} {unit}")

if __name__ == "__main__":
        root = Tk()
        root.title("Memory Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        memory_page = MemoryPage(root)
        memory_page.setup_static()
        memory_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()