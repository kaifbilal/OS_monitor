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
                self.chart.update_head("Disk Transfer Rate", "0 MB/s")
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

                self._stats_dictionary = {"header": header,
                "footer": {
                        "Active time": (f"{footer['active_time']}", "row1"),
                        "Average response time": (f"{footer['average_response_time']}", "row1"),
                        "Read speed": (f"{footer['read_speed']}", "row2"),
                        "Write speed": (f"{footer['write_speed']}", "row2"),
                        "disk_transfer_rate": (f"{footer['disk_transfer_rate']}", "row3")
                        },
                "footer_static":{
                         "Capacity:": ( f"{footer_static['capacity']}", " GB"),
                        "Formatted:": ( f"{footer_static['formatted']}", " GB"),
                        "System disk:": ( f"{footer_static['system_disk']}", ""),
                        "Type:": ( f"{footer_static['type']}", "")
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

        def update_stats(self, dictionary):
                footer = dictionary or {}
                dynamic = {
                        "Active time": self._fmt_value(footer.get("active_time")),
                        "Average response time": self._fmt_value(footer.get("average_response_time")),
                        "Read speed": self._fmt_value(footer.get("read_speed")),
                        "Write speed": self._fmt_value(footer.get("write_speed")),
                        "disk_transfer_rate": self._fmt_value(footer.get("disk_transfer_rate")),
                }
                self.footer.dynamic_value_setter(dynamic)
                self.chart.plot_value(footer.get("active_time"))

if __name__ == "__main__":
        root = Tk()
        root.title("Disk Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        disk_page = DiskPage(root)
        disk_page.setup_static()
        disk_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()