from tkinter import BOTH

from OS_info.main import MainInfo
from GUI.main import MainWindow

class MainApp:
    def __init__(self):
        self.root = MainWindow(self)
        self.root_info = MainInfo()
        self._updates_started = False
        self.setup()
        self.update()


    def run(self):
        self.root.mainloop()
# -------------------SETUP-------------------
    def setup(self):
        self.setup_cpu()
        self.setup_disk()
        self.setup_gpu()
        self.setup_memory()
        self.setup_wifi()

    def setup_cpu(self):
        dictionary = self.root_info.get_stats_static_cpu()
        self.root.cpu_page.set_stats(dictionary)

    def setup_disk(self):
        dictionary = self.root_info.get_stats_static_disk()
        self.root.disk_page.set_stats(dictionary)

    def setup_gpu(self):
        dictionary = self.root_info.get_stats_static_gpu()
        self.root.gpu_page.set_stats(dictionary)

    def setup_memory(self):
        dictionary = self.root_info.get_stats_static_memory()
        self.root.memory_page.set_stats(dictionary)


    def setup_wifi(self):
        dictionary = self.root_info.get_stats_static_wifi()
        self.root.wifi_page.set_stats(dictionary)

#-------------------UPDATER-------------------
    def update(self):
        if self._updates_started:
            return
        self._updates_started = True

        self.update_cpu()
        self.update_disk()
        self.update_gpu()
        self.update_memory()
        self.update_wifi()

    def update_cpu(self):
        if self.root.pages["CPU"][1]:
            dictionary = self.root_info.get_stats_dynamic_cpu()
            self.root.cpu_page.update_stats(dictionary)
        self.root.after(1000, self.update_cpu)

    def update_disk(self):
        if self.root.pages["Disk"][1]:
            dictionary = self.root_info.get_stats_dynamic_disk()
            self.root.disk_page.update_stats(dictionary)
        self.root.after(1000, self.update_disk)
    
    def update_gpu(self):
        if self.root.pages["GPU"][1]:
            dictionary = self.root_info.get_stats_dynamic_gpu()
            self.root.gpu_page.update_stats(dictionary)
        self.root.after(1000, self.update_gpu)
    
    def update_memory(self):
        if self.root.pages["Memory"][1]:
            dictionary = self.root_info.get_stats_dynamic_memory()
            self.root.memory_page.update_stats(dictionary)
        self.root.after(1000, self.update_memory)

    def update_wifi(self):
        if self.root.pages["WiFi"][1]:
            dictionary = self.root_info.get_stats_dynamic_wifi()
            self.root.wifi_page.update_stats(dictionary)
        self.root.after(1000, self.update_wifi)

if __name__ == "__main__":
    app = MainApp()
    app.root.show_page("CPU")
    app.run()