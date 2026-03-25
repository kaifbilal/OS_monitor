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

        def get_stats(self):
                self._stats_dictionary = {"header": ("Wi-Fi", "Intel(R) Wi-Fi 6 AX201 160MHz"),
                "footer": {
                        "Signal quality": ("%", "row1"),
                        "Link speed": ("Mbps", "row1"),
                        "Network band": ("GHz", "row2"),
                        "Channel": ("", "row2"),
                        "Physical type": ("", "row3"),
                        },
                "footer_static":{
                        "SSID:": (f"Kaif's Wi-Fi", ""),
                        "Security type:": (f"WPA2-Personal", ""),
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
        root.title("WiFi Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        wifi_page = WiFiPage(root)
        wifi_page.setup_static()
        wifi_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()