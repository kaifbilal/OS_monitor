from GUI.footer import Footer
from GUI.header import Header
from GUI.chart import Chart
from tkinter import *

class WiFiPage(Frame):
        def __init__(self, parent):
                super().__init__(parent)
                self.configure(bg="#191919")
                self.header = Header(self)
                self.chart = Chart(self)
                self.footer = Footer(self)
                self.chart.update_head("WiFi Signal Strength", "0%")
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
                        "Signal quality": (f"{footer['signal_strength']}", "row1"),
                        "Send speed": (f"{footer['send']}", "row1"),
                        "Recieve speed": (f"{footer['receive']}", "row2"),
                        "Throughput": (f"{footer['throughput']}", "row2"),
                        },
                "footer_static":{
                        "SSID:": (f"{footer_static['ssid']}", ""),
                        # "Security type:": (f"{footer_static['security_type']}", ""),
                        "Connection type:": (f"{footer_static['connection_type']}", ""),
                        "IPv4 address:": (f"{footer_static['ipv4_address']}", ""),
                        "IPv6 address:": (f"{footer_static['ipv6_address']}", ""),
                        "Current speed": (f"{footer_static['current_internet_speed']}", " Mbps"),
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
                        "Signal quality": self._fmt_value(footer.get("signal_strength")),
                        "Send speed": self._fmt_value(footer.get("send")),
                        "Recieve speed": self._fmt_value(footer.get("receive")),
                        "Throughput": self._fmt_value(footer.get("throughput")),
                }
                self.footer.dynamic_value_setter(dynamic)
                self.chart.plot_value(footer.get("throughput"))

if __name__ == "__main__":
        root = Tk()
        root.title("WiFi Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        wifi_page = WiFiPage(root)
        wifi_page.setup_static()
        wifi_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()