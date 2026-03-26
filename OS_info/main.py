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
        footer_static = self.memory.get_memory_info()
        header = footer_static["total"]
        del footer_static["total"]
        footer = self.memory.get_memory_looped_info()
        return {"header": ("Memory", header),
                "footer": footer,
                "footer_static": footer_static,
                }

    def get_stats_static_disk(self):
        footer_static = self.disk.get_disk_info()
        footer = self.disk.get_loopback_info()
        header = ""
        return {
            "header": ("Disk", header),
            "footer": footer,
            "footer_static": footer_static,
        }

    def get_stats_static_gpu(self):
        footer_static = self.gpu.get_gpu_info()
        footer = self.gpu.get_gpu_looped_info()
        header = self.gpu.get_gpu_name()
        return {
            "header": ("GPU", header),
            "footer": footer,
            "footer_static": footer_static,
        }

    def get_stats_static_wifi(self):
        footer_static = self.wifi.get_wifi_info()
        footer = self.wifi.get_wifi_looped_info()
        header = footer_static["driver_name"]
        del footer_static["driver_name"]
        return {
            "header": ("WiFi", header),
            "footer": footer,
            "footer_static": footer_static,
        }

    def get_stats_dynamic_cpu(self):
        footer = self.cpu.get_loopback_cpu_info() or {}
        footer["UptimeSeconds"] = self.cpu.get_uptime_seconds()
        return footer

    def get_stats_dynamic_memory(self):
        return self.memory.get_memory_looped_info() or {}

    def get_stats_dynamic_disk(self):
        return self.disk.get_loopback_info() or {}

    def get_stats_dynamic_gpu(self):
        return self.gpu.get_gpu_looped_info() or {}

    def get_stats_dynamic_wifi(self):
        return self.wifi.get_wifi_looped_info() or {}


if __name__ == "__main__":
    main_info = MainInfo()
    cpu_stats = main_info.get_stats_static_cpu()
    print(cpu_stats)