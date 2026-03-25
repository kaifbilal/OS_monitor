from OS_info.cpu import CPUInfo
from OS_info.memory import Memory
from OS_info.disk import Disk
from OS_info.GPU import GPU
from OS_info.wifi import Wifi

class MainInfo:
    def __init__(self):
        self.cpu = CPUInfo()
        self.memory = Memory()
        self.disk = Disk()
        self.gpu = GPU()
        self.wifi = Wifi()

    def get_stats_static_cpu(self):
        footer_static = self.cpu.get_cpu_info()
        header = self.cpu.get_cpu_name_from_registry()
        footer = self.cpu.get_loopback_cpu_info()
        footer["UptimeSeconds"] = self.cpu.get_uptime_seconds()
        return {
            "header": ("CPU", header),
            "footer": footer,
            "footer_static": footer_static,
        }

    def get_stats_static_memory(self):
        pass

    def get_stats_static_disk(self):
        pass

    def get_stats_static_gpu(self):
        pass


if __name__ == "__main__":
    main_info = MainInfo()
    cpu_stats = main_info.get_stats_static_cpu()
    print(cpu_stats)