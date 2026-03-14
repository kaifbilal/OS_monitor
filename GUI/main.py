from tkinter import *
from tkinter import ttk
from sidebar import Sidebar
from header import Header
from chart import Chart
from footer import Footer

class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("OS Monitor")
        self.geometry("1024x600")
        self.configure(bg="#191919")
        self.sidebar = Sidebar(self)
        self.header = Header(self)
        self.header.setup_cpu()  # Default to CPU screen
        self.chart = Chart(self)
        self.footer = Footer(self)
        self.footer.setup_cpu()  # Default to CPU stats
    
    def show_cpu(self):
        self.header.setup_cpu()
        # self.footer.clear() # Clear previous stats
        self.footer.setup_cpu()
        # Update chart with CPU data
    
    def show_memory(self):
        self.header.setup_memory()
        # self.footer.clear() # Clear previous stats
        self.footer.setup_memory()
        # Update chart with Memory data
    
    def show_disk(self):
        self.header.setup_disk()
        # self.footer.clear() # Clear previous stats
        self.footer.setup_disk()
        # Update chart with Disk data
    
    def show_gpu(self):
        self.header.setup_gpu()
        # self.footer.clear() # Clear previous stats
        self.footer.setup_gpu()
        # Update chart with GPU data


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()