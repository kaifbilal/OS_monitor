from tkinter import BOTH

from OS_info.main import MainInfo
from GUI.main import MainWindow
import time
class MainApp:
    def __init__(self):
        self.root = MainWindow()
        self.root_info = MainInfo()


    def run(self):
        self.root.mainloop()


    def update(self):
        dictionary = self.root_info.get_stats_static_cpu()
        self.root.cpu_page.set_stats(dictionary)
        self.root.show_page("CPU")

if __name__ == "__main__":
    app = MainApp()
    app.update()
    app.run()