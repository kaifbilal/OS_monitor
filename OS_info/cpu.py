import ctypes
from ctypes import *
from ctypes import wintypes
import winreg
import time
from time import sleep
import os
#-------------------------------
#
#  For __init__ loading we need
# Base Speed in GHz - kernel32
# then Number of Sockets - kernel32
# then Number of Cores - kernel32
# Logical Processors - kernel32
# size of L1 Cache - kernel32
# size of L2 Cache - kernel32
# size of L3 Cache - kernel32
# Up Time - kernel32
#
#----------------------------
#
# For every second cycle we need
# Utilization in % - pdh
# Speed in GHz - pdh
# Processes - pdh
# Threads - pdh
# Handles - pdh
# -----------------------------




class PROCESSOR_POWER_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("Number", wintypes.ULONG),
        ("MaxMhz", wintypes.ULONG),
        ("CurrentMhz", wintypes.ULONG),
        ("MhzLimit", wintypes.ULONG),
        ("MaxIdleState", wintypes.ULONG),
        ("CurrentIdleState", wintypes.ULONG),
    ]


class PDH_FMT_COUNTERVALUE(ctypes.Structure):
            _fields_ = [('CStatus', wintypes.DWORD), ('doubleValue', ctypes.c_double)]

class PROCESSOR_CORE(ctypes.Structure):
    _fields_ = [('Flags', ctypes.c_byte)]

class CACHE_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ('Level', ctypes.c_byte),
        ('Associativity', ctypes.c_byte),
        ('LineSize', ctypes.c_ushort),
        ('Size', ctypes.c_ulong),
        ('Type', ctypes.c_uint)
    ]

class _PROC_INFO_UNION(ctypes.Union):
    _fields_ = [
        ('ProcessorCore', PROCESSOR_CORE),
        ('NumaNode', ctypes.c_uint),        # NodeNumber (DWORD)
        ('Cache', CACHE_DESCRIPTOR),
        ('Reserved', ctypes.c_ulonglong * 2)
    ]

class SYSTEM_LOGICAL_PROCESSOR_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('ProcessorMask', ctypes.c_size_t),
        ('Relationship', ctypes.c_uint),
        ('ProcessorInformation', _PROC_INFO_UNION)
    ]

class CPUInfo:
    def __init__(self):
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.pdh = ctypes.WinDLL('pdh', use_last_error=True)

        self.BaseSpeedGHz = self.base_speed()
        self.NumSockets = None
        self.NumCores = None
        self.LogicalProcessors = None
        self.L1CacheSize = None
        self.L2CacheSize = None
        self.L3CacheSize = None
        self.UptimeSeconds = None
    

        


        # Constants for LOGICAL_PROCESSOR_RELATIONSHIP
        self.RelationProcessorCore = 0
        self.RelationNumaNode = 1
        self.RelationCache = 2
        self.RelationProcessorPackage = 3
        self.RelationGroup = 4
        self.RelationAll = 0xFFFF

        # bindings
        # pdh
        self.PdhOpenQuery = self.pdh.PdhOpenQueryW
        self.PdhOpenQuery.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p, ctypes.POINTER(wintypes.HANDLE)]
        self.PdhOpenQuery.restype = wintypes.DWORD

        self.PdhAddCounter = self.pdh.PdhAddCounterW
        self.PdhAddCounter.argtypes = [wintypes.HANDLE, wintypes.LPCWSTR, ctypes.c_void_p, ctypes.POINTER(wintypes.HANDLE)]
        self.PdhAddCounter.restype = wintypes.DWORD

        self.PdhCollectQueryData = self.pdh.PdhCollectQueryData
        self.PdhCollectQueryData.argtypes = [wintypes.HANDLE]
        self.PdhCollectQueryData.restype = wintypes.DWORD

        self.PdhGetFormattedCounterValue = self.pdh.PdhGetFormattedCounterValue
        self.PdhGetFormattedCounterValue.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        self.PdhGetFormattedCounterValue.restype = wintypes.DWORD

        self.PdhCloseQuery = self.pdh.PdhCloseQuery
        self.PDH_FMT_DOUBLE = 0x200

        # initialize PDH query and counters
        # open once and add counters
        self.query = wintypes.HANDLE()
        if self.PdhOpenQuery(None, 0, ctypes.byref(self.query)) != 0:
            raise RuntimeError("PdhOpenQuery failed")
        self.counters = {}
        paths = {
            'util': r'\Processor(_Total)\% Processor Time',
            'freq': r'\Processor Information(_Total)\Processor Frequency',

            'proc': r'\System\Processes',
            'thread': r'\System\Threads',
            'handles': r'\Process(_Total)\Handle Count'
        }
        for k, p in paths.items():
            h = wintypes.HANDLE()
            if self.PdhAddCounter(self.query, p, 0, ctypes.byref(h)) == 0:
                self.counters[k] = h

        # prime the counters once (small sleep)
        self.PdhCollectQueryData(self.query)
        time.sleep(0.05)
        self.PdhCollectQueryData(self.query)

        # bindings 
        # kernel32
        self.GetLogicalProcessorInformation = self.kernel32.GetLogicalProcessorInformation
        self.GetLogicalProcessorInformation.argtypes = [ctypes.POINTER(SYSTEM_LOGICAL_PROCESSOR_INFORMATION), ctypes.POINTER(wintypes.DWORD)]
        self.GetLogicalProcessorInformation.restype = wintypes.BOOL

        self.GetTickCount64 = self.kernel32.GetTickCount64
        self.GetTickCount64.restype = ctypes.c_ulonglong

    def get_cpu_name_from_registry(self):
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            name, _ = winreg.QueryValueEx(k, "ProcessorNameString")
            return name.strip()
        except OSError:
            return None


    def popcount(self, x: int) -> int:
        return bin(x).count('1')
    
    def get_cpu_info(self):
        needed = wintypes.DWORD(0)
        # first call to get buffer size
        res = self.GetLogicalProcessorInformation(None, ctypes.byref(needed))
        if res != 0:
            raise RuntimeError("Unexpected success on first GetLogicalProcessorInformation call")

        buf = ctypes.create_string_buffer(needed.value)
        p = ctypes.cast(buf, ctypes.POINTER(SYSTEM_LOGICAL_PROCESSOR_INFORMATION))

        res = self.GetLogicalProcessorInformation(p, ctypes.byref(needed))
        if not res:
            raise ctypes.WinError(ctypes.get_last_error())

        struct_size = ctypes.sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION)
        count = needed.value // struct_size

        logical_mask_union = 0
        core_count = 0
        socket_count = 0
        l1 = 0
        l2 = 0
        l3 = 0


        for i in range(count):
            entry = p[i]
            logical_mask_union |= entry.ProcessorMask
            rel = entry.Relationship
            if rel == self.RelationProcessorCore:
                core_count += 1
            elif rel == self.RelationProcessorPackage:
                socket_count += 1
            elif rel == self.RelationCache:
                level = entry.ProcessorInformation.Cache.Level
                size = entry.ProcessorInformation.Cache.Size
                if level == 1:
                    l1 += size
                elif level == 2:
                    l2 += size
                elif level == 3:
                    l3 += size

        logical_processors = self.popcount(logical_mask_union)

        uptime_ms = self.GetTickCount64()
        uptime_seconds = int(uptime_ms // 1000)

        return {
            'NumSockets': socket_count,
            'NumCores': core_count,
            'LogicalProcessors': logical_processors,
            'L1CacheBytes': (l1//1024),
            'L2CacheBytes': (l2//(1024)**2),
            'L3CacheBytes': (l3//(1024)**2),
            'UptimeSeconds': uptime_seconds,
            }
    
    def get_cpu_name_from_registry(self):
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            name, _ = winreg.QueryValueEx(k, "ProcessorNameString")
            return name.strip()
        except OSError:
            return None

    def base_speed(self):
    
        """
        Returns base/max clock in GHz reported by Windows (MaxMhz) or None on failure.
        Also returns per-processor details as a list of dicts under 'per_proc'.
        """
        try:
            powrprof = ctypes.WinDLL("PowrProf.dll")
            CallNtPowerInformation = powrprof.CallNtPowerInformation
            CallNtPowerInformation.argtypes = [wintypes.DWORD, ctypes.c_void_p, wintypes.ULONG,
                                            ctypes.c_void_p, wintypes.ULONG]
            CallNtPowerInformation.restype = wintypes.DWORD

            PROCESSOR_INFORMATION = 11  # POWER_INFORMATION_LEVEL::ProcessorInformation

            nproc = os.cpu_count() or 1
            arr_type = PROCESSOR_POWER_INFORMATION * nproc
            arr = arr_type()
            out_size = ctypes.sizeof(arr)

            ret = CallNtPowerInformation(PROCESSOR_INFORMATION, None, 0, ctypes.byref(arr), out_size)
            if ret != 0:
                return None

            max_mhz_values = []
            for i in range(nproc):
                p = arr[i]
                max_mhz_values.append(p.MaxMhz)

            # Use the first non-zero MaxMhz or the max across CPUs
            chosen_mhz = next((m for m in max_mhz_values if m), max(max_mhz_values) if max_mhz_values else 0)
            base_ghz = round(chosen_mhz / 1000.0, 3) if chosen_mhz else None

            return base_ghz
        except Exception:
            return None
    

    def get_loopback_cpu_info(self):
        # Placeholder for CPUID-based info
        # single collect per sample (fast)
        if self.PdhCollectQueryData(self.query) != 0:
            return {}

        out = {}
        for k, h in self.counters.items():
            val = PDH_FMT_COUNTERVALUE()
            if self.PdhGetFormattedCounterValue(h, self.PDH_FMT_DOUBLE, None, ctypes.byref(val)) == 0:
                if k == 'util':
                    out['UtilizationPercent'] = round(val.doubleValue, 2)
                elif k == 'freq':
                    out['SpeedGHz'] = round(val.doubleValue / 1000.0, 3) if val.doubleValue > 0 else None
                elif k == 'proc':
                    out['Processes'] = int(round(val.doubleValue))
                elif k == 'thread':
                    out['Threads'] = int(round(val.doubleValue))
                elif k == 'handles':
                    out['Handles'] = int(round(val.doubleValue))
        #------------------------------------------------------

        return out
    def loopclose(self):
        if hasattr(self, 'query') and self.query:
            self.PdhCloseQuery(self.query)
            self.query = None

if __name__ == '__main__':
    cpu_info = CPUInfo()
    info = cpu_info.get_cpu_info()
    print("Kernel32 CPU Info:\n")
    for k, v in info.items():
        print(f'{k}: {v}')
    print("Base Speed", cpu_info.BaseSpeedGHz, "GHz")
    for _ in range(1):
        info = cpu_info.get_loopback_cpu_info()
        print("\n\nLoopback CPU Info:\n")
        for k, v in info.items():
            print(f'{k}: {v}')
        # sleep(0.91)
    print("\n\nCPU Name from Registry:")
    print(cpu_info.get_cpu_name_from_registry())
    cpu_info.loopclose()