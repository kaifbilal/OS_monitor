from tkinter import *
from tkinter import ttk
from GUI.sidebar import Sidebar
from GUI.page_cpu import CPUPage
from GUI.page_disk import DiskPage
from GUI.page_memory import MemoryPage
from GUI.page_gpu import GPUPage
from GUI.page_wifi import WiFiPage



class MainWindow(Tk):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title("OS Monitor")
        self.geometry("1024x640")
        self.configure(bg="#191919")
        self.sidebar = Sidebar(self)
        self.cpu_page = CPUPage(self)
        self.disk_page = DiskPage(self)
        self.memory_page = MemoryPage(self)
        self.gpu_page = GPUPage(self)
        self.wifi_page = WiFiPage(self)

        self.pages = {
            "CPU": (self.cpu_page, False),
            "Memory": (self.memory_page, False),
            "Disk": (self.disk_page, False),
            "GPU": (self.gpu_page, False),
            "WiFi": (self.wifi_page, False),
        }
        self.update_flag = {
            "CPU": False,
            "Memory": False,
            "Disk": False,
            "GPU": False,
            "WiFi": False
        }
        # self.show_page("CPU")

    def _hide_all(self):
        for page in self.pages.values():
            page[0].pack_forget()

    def show_page(self, page_name):
        self._hide_all()
        if page_name in self.pages:
            page, flag = self.pages[page_name]
            page.pack(fill=BOTH, expand=True)
        try:
            if not flag:
                page.setup_static()
                self.pages[page_name] = (page, True)
        except Exception as e:
            print(f"Error setting up static content for {page_name}: {e}")

    def update(self):
        pass

if __name__ == "__main__":

    root = MainWindow(None)
    root.mainloop()