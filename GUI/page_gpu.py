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

        def get_stats(self):
                self._stats_dictionary = {"header": ("GPU", "NVIDIA GeForce RTX 2060"),
                "footer": {
                        "Utilization": ("%", "row1"),
                        "Shared GPU memory": ("GB", "row1"),
                        "GPU Memory": ("GB", "row2"),
                        },
                "footer_static":{
                        "Driver version:": (f"31.0.101.2125", ""),
                        "Driver date:": (f"24-05-2023", ""),
                        "DirectX version:": (f"12 (FL 12.1)", ""),
                        "Physical location:": (f"PCI bus 0 , device 1 , function 1 ", "")
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
        root.title("GPU Page")
        root.geometry("1024x600")
        root.configure(bg="#191919")
        
        gpu_page = GPUPage(root)
        gpu_page.setup_static()
        gpu_page.pack(fill=BOTH, expand=True)
        
        root.mainloop()