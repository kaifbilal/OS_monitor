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
                self.chart.update_head("Memory Usage", "0%")
                self._stats_dictionary = {}

        def _fmt_value(self, value):
                if value is None:
                        return "N/A"
                text = str(value).strip()
                return text if text else "N/A"

        def set_stats(self, dictionary):
                header = dictionary["header"]
                footer = dictionary["footer"]
                footer_static = dictionary["footer_static"]
                self._stats_dictionary = {
                "header": header,
                "footer": {
                        "In use (Compressed)": (f"{footer['In use (Compressed)']}", "row1"),
                        "In use": (f"{footer['In use']}", "row1"),
                        "Compressed": (f"{footer['Compressed']}", "row1"),
                        "Available": (f"{footer['Available']}", "row1"),
                        "Committed": (f"{footer['Committed']}", "row2"),
                        "Cached": (f"{footer['Cached']}", "row2"),
                        "Paged pool": (f"{footer['Paged pool']}", "row3"),
                        "Non-paged pool": (f"{footer['Non-paged pool']}", "row3"),
                        # "memory composition": (f"{footer['memory_composition']}", "row3"),
                                        },
                "footer_static":{ 
                        "Speed:": (f"{footer_static['speed']}", " MT/s"),
                        "Slots used:": (f"{footer_static['slots_used']}", ""),                                        "Form factor:": ("Row of chips", ""),
                        "Hardware reserved:": (f"{footer_static['hardware_reserved']}", " MB"),
                        },
                }
        def get_stats(self):
                return self._stats_dictionary
        
        def setup_static(self):
                dictionary = self.get_stats()
                print("to be build", dictionary)
                name, info = dictionary["header"]
                self.header.update_info(name, info)
                self.footer.setup_footer(dictionary["footer"])
                for label, (value, unit) in dictionary["footer_static"].items():
                        self.footer._create_stat_row(self.footer.frm1, label, f"{value} {unit}")

        def update_stats(self, dictionary):
                footer = dictionary or {}
                dynamic = {
                        "In use (Compressed)": self._fmt_value(footer.get("In use (Compressed)")),
                        "In use": self._fmt_value(footer.get("In use")),
                        "Compressed": self._fmt_value(footer.get("Compressed")),
                        "Available": self._fmt_value(footer.get("Available")),
                        "Committed": self._fmt_value(footer.get("Committed")),
                        "Cached": self._fmt_value(footer.get("Cached")),
                        "Paged pool": self._fmt_value(footer.get("Paged pool")),
                        "Non-paged pool": self._fmt_value(footer.get("Non-paged pool")),
                }
                self.footer.dynamic_value_setter(dynamic)
                self.chart.plot_value(footer.get("In use"))

if __name__ == "__main__":
        root = Tk()
        root.title("Memory Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        memory_page = MemoryPage(root)
        memory_page.setup_static()
        memory_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()