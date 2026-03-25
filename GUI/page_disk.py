from GUI.footer import Footer
from GUI.header import Header
from GUI.chart import Chart
from tkinter import *

class DiskPage(Frame):
        def __init__(self, parent):
                super().__init__(parent)
                self.configure(bg="#191919")
                self.header = Header(self)
                self.chart = Chart(self)
                self.footer = Footer(self)

        def get_stats(self):
                self._stats_dictionary = {"header": ("Disk", "Samsung SSD 970 EVO Plus 1TB"),
                "footer": {
                        "Active time": ("%", "row1"),
                        "Average response time": ("ms", "row1"),
                        "Read speed": ("KB/s", "row2"),
                        "Write speed": ("KB/s", "row2"),
                        },
                "footer_static":{
                         "Capacity:": ( "512", " GB"),
                        "Formatted:": ( "512", " GB"),
                        "System disk:": ( f"yes", ""),
                        "Page file:": ( f"yes", ""),
                        "Type:": ( f"SSD(NVMe)", "")
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
        root.title("Disk Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        disk_page = DiskPage(root)
        disk_page.setup_static()
        disk_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()