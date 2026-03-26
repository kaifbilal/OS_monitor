from GUI.footer import Footer
from GUI.header import Header
from GUI.chart import Chart
from tkinter import *

class GPUPage(Frame):
        def __init__(self, parent):
                super().__init__(parent)
                self.configure(bg="#191919")
                self.header = Header(self)
                self.chart = Chart(self)
                self.footer = Footer(self)
                self.chart.update_head("GPU Utilization", "100%")
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
                        "Utilization": (f"{footer['gpu_utilization']}", "row1"),
                        "Shared GPU memory": (f"{footer['shared_gpu_memory']}", "row1"),
                        "GPU Memory": (f"{footer['total_gpu_memory']}", "row2"),
                        },
                "footer_static":{
                        "Driver version:": (f"{footer_static['driver_version']}", ""),
                        "Driver date:": (f"{footer_static['driver_date']}", ""),
                        "DirectX version:": (f"{footer_static['directx_version']}", ""),
                        "Physical location:": (f"{footer_static['physical_location']}", "")
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
                        "Utilization": self._fmt_value(footer.get("gpu_utilization")),
                        "Shared GPU memory": self._fmt_value(footer.get("shared_gpu_memory")),
                        "GPU Memory": self._fmt_value(footer.get("total_gpu_memory")),
                }
                self.footer.dynamic_value_setter(dynamic)
                self.chart.plot_value(footer.get("gpu_utilization"))


if __name__ == "__main__":
        root = Tk()
        root.title("GPU Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        gpu_page = GPUPage(root)
        gpu_page.setup_static()
        gpu_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()