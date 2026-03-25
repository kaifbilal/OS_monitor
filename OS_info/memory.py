import ctypes
import struct
from ctypes import wintypes
from time import sleep


PDH_FMT_DOUBLE = 0x00000200


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class PERFORMANCE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("CommitTotal", ctypes.c_size_t),
        ("CommitLimit", ctypes.c_size_t),
        ("CommitPeak", ctypes.c_size_t),
        ("PhysicalTotal", ctypes.c_size_t),
        ("PhysicalAvailable", ctypes.c_size_t),
        ("SystemCache", ctypes.c_size_t),
        ("KernelTotal", ctypes.c_size_t),
        ("KernelPaged", ctypes.c_size_t),
        ("KernelNonpaged", ctypes.c_size_t),
        ("PageSize", ctypes.c_size_t),
        ("HandleCount", wintypes.DWORD),
        ("ProcessCount", wintypes.DWORD),
        ("ThreadCount", wintypes.DWORD),
    ]


class PDH_FMT_COUNTERVALUE(ctypes.Structure):
    _fields_ = [
        ("CStatus", wintypes.DWORD),
        ("doubleValue", ctypes.c_double),
    ]


class Memory:
    def __init__(self):
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.psapi = ctypes.WinDLL("psapi", use_last_error=True)
        self.pdh = ctypes.WinDLL("pdh", use_last_error=True)
        self._configure_apis()
        self._init_pdh_query()

    def _configure_apis(self):
        self.kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
        self.kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL

        self.kernel32.GetPhysicallyInstalledSystemMemory.argtypes = [ctypes.POINTER(ctypes.c_ulonglong)]
        self.kernel32.GetPhysicallyInstalledSystemMemory.restype = wintypes.BOOL

        self.kernel32.GetSystemFirmwareTable.argtypes = [
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
        ]
        self.kernel32.GetSystemFirmwareTable.restype = wintypes.UINT

        self.psapi.GetPerformanceInfo.argtypes = [ctypes.POINTER(PERFORMANCE_INFORMATION), wintypes.DWORD]
        self.psapi.GetPerformanceInfo.restype = wintypes.BOOL

        self.pdh.PdhOpenQueryW.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.pdh.PdhOpenQueryW.restype = wintypes.LONG

        self.pdh.PdhAddEnglishCounterW.argtypes = [
            ctypes.c_void_p,
            wintypes.LPCWSTR,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.pdh.PdhAddEnglishCounterW.restype = wintypes.LONG

        self.pdh.PdhCollectQueryData.argtypes = [ctypes.c_void_p]
        self.pdh.PdhCollectQueryData.restype = wintypes.LONG

        self.pdh.PdhGetFormattedCounterValue.argtypes = [
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(PDH_FMT_COUNTERVALUE),
        ]
        self.pdh.PdhGetFormattedCounterValue.restype = wintypes.LONG

        self.pdh.PdhCloseQuery.argtypes = [ctypes.c_void_p]
        self.pdh.PdhCloseQuery.restype = wintypes.LONG

    def _init_pdh_query(self):
        self._query = ctypes.c_void_p()
        status = self.pdh.PdhOpenQueryW(None, None, ctypes.byref(self._query))
        if status != 0:
            self._query = None
            self._counters = {}
            return

        paths = {
            "compressed": r"\\Memory\\Compressed Bytes",
            "modified": r"\\Memory\\Modified Page List Bytes",
            "standby": r"\\Memory\\Standby Cache Core Bytes",
            "free_zero": r"\\Memory\\Free & Zero Page List Bytes",
        }

        self._counters = {}
        for key, path in paths.items():
            counter = ctypes.c_void_p()
            st = self.pdh.PdhAddEnglishCounterW(self._query, path, None, ctypes.byref(counter))
            if st == 0:
                self._counters[key] = counter

        # Prime PDH counters so next read has a computed value.
        self.pdh.PdhCollectQueryData(self._query)

    def _read_pdh_counter(self, name):
        if not self._query or name not in self._counters:
            return 0.0
        counter_type = wintypes.DWORD(0)
        value = PDH_FMT_COUNTERVALUE()
        st = self.pdh.PdhGetFormattedCounterValue(
            self._counters[name],
            PDH_FMT_DOUBLE,
            ctypes.byref(counter_type),
            ctypes.byref(value),
        )
        if st != 0:
            return 0.0
        return float(value.doubleValue)

    def _human_bytes(self, value):
        units = ["B", "KB", "MB", "GB", "TB"]
        n = float(value)
        for unit in units:
            if n < 1024.0 or unit == units[-1]:
                return f"{n:.2f} {unit}"
            n /= 1024.0
        return f"{n:.2f} TB"

    def _memory_status(self):
        ms = MEMORYSTATUSEX()
        ms.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ok = self.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        if not ok:
            return None
        return ms

    def _performance_info(self):
        pi = PERFORMANCE_INFORMATION()
        pi.cb = ctypes.sizeof(PERFORMANCE_INFORMATION)
        ok = self.psapi.GetPerformanceInfo(ctypes.byref(pi), pi.cb)
        if not ok:
            return None
        return pi

    def _read_installed_memory(self):
        kb = ctypes.c_ulonglong(0)
        ok = self.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(kb))
        if not ok:
            return None
        return kb.value * 1024

    def _read_smbios_memory(self):
        # 'RSMB' provider signature.
        provider = 0x52534D42
        size = self.kernel32.GetSystemFirmwareTable(provider, 0, None, 0)
        if size == 0:
            return {"speed_mt_s": None, "slots_used": None, "slots_total": None}

        buf = ctypes.create_string_buffer(size)
        copied = self.kernel32.GetSystemFirmwareTable(provider, 0, buf, size)
        if copied == 0:
            return {"speed_mt_s": None, "slots_used": None, "slots_total": None}

        data = bytes(buf.raw)
        if len(data) < 8:
            return {"speed_mt_s": None, "slots_used": None, "slots_total": None}

        table_data = data[8:]
        i = 0
        speeds = []
        slots_used = 0
        slots_total = 0

        while i + 4 <= len(table_data):
            stype = table_data[i]
            slen = table_data[i + 1]
            if slen < 4 or i + slen > len(table_data):
                break

            formatted = table_data[i : i + slen]
            if stype == 17:
                slots_total += 1
                size_mb = 0
                if slen >= 14:
                    size_mb = struct.unpack_from("<H", formatted, 12)[0]
                if size_mb not in (0, 0xFFFF):
                    slots_used += 1

                if slen >= 23:
                    speed = struct.unpack_from("<H", formatted, 21)[0]
                    if speed not in (0, 0xFFFF):
                        speeds.append(int(speed))

            j = i + slen
            while j + 1 < len(table_data):
                if table_data[j] == 0 and table_data[j + 1] == 0:
                    j += 2
                    break
                j += 1
            if j <= i:
                break
            i = j

        avg_speed = int(sum(speeds) / len(speeds)) if speeds else None
        return {"speed_mt_s": avg_speed, "slots_used": slots_used, "slots_total": slots_total}

    def get_memory_info(self):
        mem = self._memory_status()
        smbios = self._read_smbios_memory()
        installed = self._read_installed_memory()

        if mem is None:
            return {
                "speed": "N/A",
                "slots_used": "N/A",
                "hardware_reserved": "N/A",
                "total": "N/A",
                "usable": "N/A",
            }

        total_phys = int(mem.ullTotalPhys)
        usable = int(mem.ullAvailPhys)
        if installed is None:
            installed = total_phys

        reserved = max(0, int(installed - total_phys))
        speed = f"{smbios['speed_mt_s']} MT/s" if smbios["speed_mt_s"] else "N/A"

        if smbios["slots_total"]:
            slots = f"{smbios['slots_used']}/{smbios['slots_total']}"
        else:
            slots = "N/A"

        return {
            "speed": speed,
            "slots_used": slots,
            "hardware_reserved": self._human_bytes(reserved),
            "total": self._human_bytes(total_phys),
            "usable": self._human_bytes(usable),
        }

    def get_memory_looped_info(self):
        mem = self._memory_status()
        perf = self._performance_info()

        if self._query:
            self.pdh.PdhCollectQueryData(self._query)

        if mem is None:
            return {
                "in_use_memory": "N/A",
                "compressed": "N/A",
                "committed": "N/A",
                "cached": "N/A",
                "paged_pool": "N/A",
                "non_paged_pool": "N/A",
                "memory_composition": "N/A",
            }

        in_use = max(0, int(mem.ullTotalPhys - mem.ullAvailPhys))
        commit_used = max(0, int(mem.ullTotalPageFile - mem.ullAvailPageFile))
        commit_total = int(mem.ullTotalPageFile)

        cached = 0
        paged_pool = 0
        non_paged_pool = 0
        if perf is not None:
            page_size = int(perf.PageSize)
            cached = int(perf.SystemCache) * page_size
            paged_pool = int(perf.KernelPaged) * page_size
            non_paged_pool = int(perf.KernelNonpaged) * page_size

        compressed = self._read_pdh_counter("compressed")
        modified = self._read_pdh_counter("modified")
        standby = self._read_pdh_counter("standby")
        free_zero = self._read_pdh_counter("free_zero")

        composition = {
            "in_use": self._human_bytes(in_use),
            "in_use_compressed": self._human_bytes(compressed),
            "modified": self._human_bytes(modified),
            "standby": self._human_bytes(standby),
            "free": self._human_bytes(free_zero),
        }

        return {
            # --
            "In use (Compressed)": self._human_bytes(in_use),
            "In use": self._human_bytes(in_use),
            "Compressed": self._human_bytes(compressed),
            "Available": "N/a",
            "Committed": f"{self._human_bytes(commit_used)}/{self._human_bytes(commit_total)}",
            "Cached": self._human_bytes(cached),
            "Paged pool": self._human_bytes(paged_pool),
            "Non-paged pool": self._human_bytes(non_paged_pool),
            "memory_composition": composition,
        }

    def close(self):
        if getattr(self, "_query", None):
            self.pdh.PdhCloseQuery(self._query)
            self._query = None


if __name__ == "__main__":
    m = Memory()
    print("Memory Info:", m.get_memory_info())
    for _ in range(1):
        print("Loop Backed Info:", m.get_memory_looped_info())
        # sleep(1)
    m.close()
        