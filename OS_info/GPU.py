import ctypes
import subprocess
import winreg
from ctypes import wintypes
from time import perf_counter


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


class PDH_FMT_COUNTERVALUE(ctypes.Structure):
    _fields_ = [
        ("CStatus", wintypes.DWORD),
        ("doubleValue", ctypes.c_double),
    ]


class GPU:
    def __init__(self):
        self.pdh = ctypes.WinDLL("pdh", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._configure_pdh()
        self._configure_kernel32()
        self.query = self._open_query()
        util_counters = self._add_wildcard_counters(
            r"\\GPU Engine(*)\\Utilization Percentage",
            include_tokens=("engtype_3D", "engtype_Compute"),
            max_count=12,
        )
        # Fallback to all engines if filtered paths are not present on this system.
        if not util_counters:
            util_counters = self._add_wildcard_counters(
                r"\\GPU Engine(*)\\Utilization Percentage",
                max_count=24,
            )
        self.counters = {
            "util": util_counters,
            "shared_used": self._add_wildcard_counters(r"\\GPU Adapter Memory(*)\\Shared Usage"),
            "shared_limit": self._add_wildcard_counters(r"\\GPU Adapter Memory(*)\\Shared Limit"),
            "dedicated_used": self._add_wildcard_counters(r"\\GPU Adapter Memory(*)\\Dedicated Usage"),
            "dedicated_limit": self._add_wildcard_counters(r"\\GPU Adapter Memory(*)\\Dedicated Limit"),
        }
        self._collect()
        self._collect()
        self._static_info = self._query_static_info()
        self._last_wmic_mem = {"shared_used": 0.0, "dedicated_used": 0.0}
        self._last_wmic_mem_ts = 0.0

    def _configure_pdh(self):
        self.pdh.PdhOpenQueryW.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        self.pdh.PdhOpenQueryW.restype = wintypes.LONG

        self.pdh.PdhCloseQuery.argtypes = [ctypes.c_void_p]
        self.pdh.PdhCloseQuery.restype = wintypes.LONG

        self.pdh.PdhCollectQueryData.argtypes = [ctypes.c_void_p]
        self.pdh.PdhCollectQueryData.restype = wintypes.LONG

        self.pdh.PdhAddEnglishCounterW.argtypes = [
            ctypes.c_void_p,
            wintypes.LPCWSTR,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.pdh.PdhAddEnglishCounterW.restype = wintypes.LONG

        self.pdh.PdhGetFormattedCounterValue.argtypes = [
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(PDH_FMT_COUNTERVALUE),
        ]
        self.pdh.PdhGetFormattedCounterValue.restype = wintypes.LONG

        self.pdh.PdhExpandWildCardPathW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.DWORD,
        ]
        self.pdh.PdhExpandWildCardPathW.restype = wintypes.LONG

    def _configure_kernel32(self):
        self.kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
        self.kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL

    def _open_query(self):
        query = ctypes.c_void_p()
        status = self.pdh.PdhOpenQueryW(None, None, ctypes.byref(query))
        if status != 0:
            return None
        return query

    def _expand_paths(self, wildcard_path):
        if not self.query:
            return []

        size = wintypes.DWORD(0)
        self.pdh.PdhExpandWildCardPathW(None, wildcard_path, None, ctypes.byref(size), 0)
        if size.value == 0:
            return []

        buf = ctypes.create_unicode_buffer(size.value)
        status = self.pdh.PdhExpandWildCardPathW(None, wildcard_path, buf, ctypes.byref(size), 0)
        if status != 0:
            return []

        return [p for p in buf[:].split("\x00") if p]

    def _add_wildcard_counters(self, wildcard_path, include_tokens=None, max_count=None):
        if not self.query:
            return []

        handles = []
        for path in self._expand_paths(wildcard_path):
            if include_tokens:
                p = path.lower()
                if not any(tok.lower() in p for tok in include_tokens):
                    continue
            counter = ctypes.c_void_p()
            st = self.pdh.PdhAddEnglishCounterW(self.query, path, None, ctypes.byref(counter))
            if st == 0:
                handles.append(counter)
                if max_count and len(handles) >= max_count:
                    break
        return handles

    def _collect(self):
        if self.query:
            self.pdh.PdhCollectQueryData(self.query)

    def _counter_value(self, handle):
        counter_type = wintypes.DWORD(0)
        value = PDH_FMT_COUNTERVALUE()
        st = self.pdh.PdhGetFormattedCounterValue(
            handle,
            PDH_FMT_DOUBLE,
            ctypes.byref(counter_type),
            ctypes.byref(value),
        )
        if st != 0:
            return 0.0
        return float(value.doubleValue)

    def _sum_counters(self, key):
        total = 0.0
        for h in self.counters.get(key, []):
            total += self._counter_value(h)
        return total

    def _human_bytes(self, value):
        n = float(max(0.0, value))
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024.0 or unit == "TB":
                return f"{n:.2f} {unit}"
            n /= 1024.0
        return f"{n:.2f} TB"

    def _read_directx_version(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\DirectX")
            val, _ = winreg.QueryValueEx(key, "Version")
            winreg.CloseKey(key)
            return str(val)
        except Exception:
            return "Unknown"

    def _query_static_info(self):
        # WMIC is significantly faster than spawning PowerShell + CIM on many systems.
        cmd = [
            "wmic",
            "path",
            "Win32_VideoController",
            "get",
            "Name,DriverVersion,DriverDate,PNPDeviceID,AdapterRAM",
            "/value",
        ]
        best = {}
        try:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            row = {}
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                row[k.strip()] = v.strip()
            if row.get("Name"):
                try:
                    row["_ram_int"] = int(row.get("AdapterRAM") or "0")
                except Exception:
                    row["_ram_int"] = 0
                best = row
        except Exception:
            best = {}

        pnp = str(best.get("PNPDeviceID") or "").strip()
        pnp = pnp.replace("&amp;", "&")
        driver_date = str(best.get("DriverDate") or "").strip()
        if len(driver_date) >= 8 and driver_date[:8].isdigit():
            driver_date = f"{driver_date[:4]}-{driver_date[4:6]}-{driver_date[6:8]}"

        return {
            "name": str(best.get("Name") or "Unknown").strip(),
            "driver_version": str(best.get("DriverVersion") or "Unknown").strip(),
            "driver_date": driver_date or "Unknown",
            "directx_version": self._read_directx_version(),
            "physical_location": pnp if pnp else "Unknown",
            "adapter_ram_bytes": int(best.get("_ram_int", 0) or 0),
        }

    def _read_system_shared_limit_estimate(self):
        # Windows typically exposes up to ~half of system RAM as shared GPU memory budget.
        ms = MEMORYSTATUSEX()
        ms.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ok = self.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        if not ok:
            return 0.0
        return float(int(ms.ullTotalPhys) // 2)

    def _read_wmic_gpu_memory_usage(self):
        # Cache for 1 second to avoid repeated process-launch overhead.
        now = perf_counter()
        if now - self._last_wmic_mem_ts < 1.0:
            return self._last_wmic_mem

        cmd = [
            "wmic",
            "path",
            "Win32_PerfFormattedData_GPUPerformanceCounters_GPUAdapterMemory",
            "get",
            "DedicatedUsage,SharedUsage",
            "/value",
        ]

        shared_used = 0.0
        dedicated_used = 0.0
        try:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                line = line.strip()
                if not line or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if not v:
                    continue
                try:
                    num = float(v)
                except Exception:
                    continue
                if k == "SharedUsage":
                    shared_used += num
                elif k == "DedicatedUsage":
                    dedicated_used += num
        except Exception:
            pass

        self._last_wmic_mem = {"shared_used": shared_used, "dedicated_used": dedicated_used}
        self._last_wmic_mem_ts = now
        return self._last_wmic_mem

    def get_gpu_name(self):
        return ("GPU", self._static_info["name"])

    def get_gpu_info(self):
        return {
            "driver_version": self._static_info["driver_version"],
            "driver_date": self._static_info["driver_date"],
            "directx_version": self._static_info["directx_version"],
            "physical_location": self._static_info["physical_location"],
        }

    def get_gpu_looped_info(self):
        self._collect()

        util = self._sum_counters("util")
        shared_used = self._sum_counters("shared_used")
        shared_limit = self._sum_counters("shared_limit")
        dedicated_used = self._sum_counters("dedicated_used")
        dedicated_limit = self._sum_counters("dedicated_limit")

        # Fallback for systems where PDH GPU memory counters are unavailable.
        if shared_used <= 0 and dedicated_used <= 0:
            wmic_mem = self._read_wmic_gpu_memory_usage()
            shared_used = max(shared_used, float(wmic_mem.get("shared_used", 0.0)))
            dedicated_used = max(dedicated_used, float(wmic_mem.get("dedicated_used", 0.0)))

        if shared_limit <= 0:
            shared_limit = self._read_system_shared_limit_estimate()

        # AdapterRAM is typically dedicated memory. If no dedicated limit, treat as integrated/shared.
        if dedicated_limit <= 0 and self._static_info["adapter_ram_bytes"] > 0:
            dedicated_limit = float(self._static_info["adapter_ram_bytes"])

        gpu_name = (self._static_info.get("name") or "").lower()
        integrated_hint = any(tok in gpu_name for tok in ("intel", "uhd", "iris", "integrated"))
        integrated = (dedicated_limit <= 0 and shared_limit > 0) or integrated_hint
        total_used = shared_used + dedicated_used
        total_limit = shared_limit + dedicated_limit

        return {
            "gpu_utilization": f"{util:.2f}%",
            "shared_or_integrated": "Integrated" if integrated else "Shared+Dedicated",
            "shared_gpu_memory": f"{self._human_bytes(shared_used)}/{self._human_bytes(shared_limit)}",
            "integrated_gpu_memory": (
                f"{self._human_bytes(shared_used)}/{self._human_bytes(shared_limit)}"
                if integrated
                else "N/A"
            ),
            "total_gpu_memory": f"{self._human_bytes(total_used)}/{self._human_bytes(total_limit)}",
        }

    def close(self):
        if self.query:
            self.pdh.PdhCloseQuery(self.query)
            self.query = None


if __name__ == "__main__":
    gpu = GPU()
    print("GPU Name:", gpu.get_gpu_name())
    print("GPU Info:", gpu.get_gpu_info())
    for _ in range(1):
        print("GPU Looped Info:", gpu.get_gpu_looped_info())
    gpu.close()