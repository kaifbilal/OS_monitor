from GUI.footer import Footer
from GUI.header import Header
from GUI.chart import Chart
from tkinter import *

class CPUPage(Frame):
        def __init__(self, parent):
                super().__init__(parent)
                self.configure(bg="#191919")
                self.header = Header(self)
                self.chart = Chart(self)
                self.footer = Footer(self)

                self._stats_dictionary = {}

        
        def set_stats(self, dictionary):
                header = dictionary["header"]
                footer = dictionary["footer"]
                footer_static = dictionary["footer_static"]
                self._stats_dictionary = {"header": header,
                        "footer": {
                                "Utilization": (f"{footer['Utilization']} %", "row1"),
                                "Speed": (f"{footer['Speed']} GHz", "row1"),
                                "Processes": (f"{footer['Processes']}", "row2"),
                                "Threads": (f"{footer['Threads']}", "row2"),
                                "Handles": (f"{footer['Handles']}", "row2"),
                                "Up Time": (f"{footer['UptimeSeconds']} Seconds", "row3"),
                                },
                        "footer_static":{
                                "Base Speed": (f"{footer_static['Base Speed']}", "GHz"),
                                "Sockets": (f"{footer_static['Sockets']}", ""),
                                "Cores": (f"{footer_static['Cores']}", ""),
                                "Logical Processors": (f"{footer_static['Logical Processors']}", ""),
                                "L1 Cache": (f"{footer_static['L1 Cache']}", "KB"),
                                "L2 Cache": (f"{footer_static['L2 Cache']}", "MB"),
                                "L3 Cache": (f"{footer_static['L3 Cache']}", "MB"),
                                },
                        }
        def get_stats(self):
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
        root.title("CPU Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        cpu_page = CPUPage(root)
        cpu_page.setup_static()
        cpu_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()