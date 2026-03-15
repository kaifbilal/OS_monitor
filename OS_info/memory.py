import ctypes

import psutil
import wmi


def _get_wmi_client(wmi_client=None):
    """Reuse a provided WMI client or create a new one."""
    return wmi_client or wmi.WMI()


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def get_memory_info(wmi_client=None):
    """One-time static memory inventory (modules, slots, totals)."""
    c = _get_wmi_client(wmi_client)
    modules = list(c.Win32_PhysicalMemory()) or []
    arrays = list(c.Win32_PhysicalMemoryArray()) or []

    module_list = []
    installed_total = 0
    for m in modules:
        cap = int(getattr(m, "Capacity", 0) or 0)
        installed_total += cap
        speed = getattr(m, "Speed", None)
        module_list.append({
            "BankLabel": getattr(m, "BankLabel", None),
            "DeviceLocator": getattr(m, "DeviceLocator", None),
            "CapacityBytes": cap,
            "CapacityMB": cap // (1024**2),
            "SpeedMHz": int(speed) if speed else None,
        })

    # robust total slots detection
    total_slots = 0
    for a in arrays:
        n = getattr(a, "NumberOfMemoryDevices", None)
        if n is None:
            n = getattr(a, "MemoryDevices", None)
        try:
            if n:
                total_slots += int(n)
        except (TypeError, ValueError):
            continue

    # fallback: if no arrays reported, try Manufacturer-specific field or leave None
    if total_slots == 0:
        total_slots = None

    slots_used = len(modules)

    # OS-visible physical memory
    ms = MEMORYSTATUSEX()
    ms.dwLength = ctypes.sizeof(ms)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    os_visible_total = ms.ullTotalPhys

    hardware_reserved = max(0, installed_total - os_visible_total)

    return {
        "modules": module_list,
        "slots_used": slots_used,
        "total_slots": total_slots,
        "installed_total_bytes": installed_total,
        "installed_total_mb": installed_total // (1024**2),
        "os_visible_total_bytes": os_visible_total,
        "os_visible_total_mb": os_visible_total // (1024**2),
        "hardware_reserved_bytes": hardware_reserved,
        "hardware_reserved_mb": hardware_reserved // (1024**2)
    }

def _bytes_to_gb(b):
    return round(b / (1024**3), 3)


def get_windows_memory_stats(wmi_client=None):
    """Dynamic memory stats (psutil + PerfOS Memory for extra fields)."""
    vm = psutil.virtual_memory()
    stats = {
        "total_bytes": vm.total,
        "total_gb": _bytes_to_gb(vm.total),
        "available_bytes": vm.available,
        "available_gb": _bytes_to_gb(vm.available),
        "used_bytes": vm.used,
        "used_gb": _bytes_to_gb(vm.used),
        "free_bytes": getattr(vm, "free", None),
        "free_gb": _bytes_to_gb(getattr(vm, "free", 0)) if getattr(vm, "free", None) is not None else None,
        "cached_bytes": getattr(vm, "cached", None),
        "cached_gb": _bytes_to_gb(getattr(vm, "cached", 0)) if getattr(vm, "cached", None) is not None else None,
    }

    try:
        c = _get_wmi_client(wmi_client)
        perf = c.Win32_PerfFormattedData_PerfOS_Memory()[0]
        compressed = int(getattr(perf, "CompressedBytes", 0) or 0)
        committed = int(getattr(perf, "CommittedBytes", 0) or 0)
        commit_limit = int(getattr(perf, "CommitLimit", 0) or 0)
        cache_bytes = int(getattr(perf, "CacheBytes", 0) or 0)
        paged_pool = int(getattr(perf, "PoolPagedBytes", 0) or 0)
        nonpaged_pool = int(getattr(perf, "PoolNonpagedBytes", 0) or 0)

        stats.update({
            "compressed_bytes": compressed,
            "compressed_gb": _bytes_to_gb(compressed),
            "committed_bytes": committed,
            "committed_gb": _bytes_to_gb(committed),
            "commit_limit_bytes": commit_limit,
            "commit_limit_gb": _bytes_to_gb(commit_limit),
            "committed_ratio": round(committed / commit_limit, 3) if commit_limit else None,
            "cache_bytes_perf": cache_bytes,
            "cache_gb_perf": _bytes_to_gb(cache_bytes),
            "paged_pool_bytes": paged_pool,
            "paged_pool_gb": _bytes_to_gb(paged_pool),
            "nonpaged_pool_bytes": nonpaged_pool,
            "nonpaged_pool_gb": _bytes_to_gb(nonpaged_pool),
        })

        if stats["cached_bytes"] in (None, 0):
            stats["cached_bytes"] = cache_bytes
            stats["cached_gb"] = _bytes_to_gb(cache_bytes)

    except Exception:
        stats.update({
            "compressed_bytes": None,
            "compressed_gb": None,
            "committed_bytes": None,
            "committed_gb": None,
            "commit_limit_bytes": None,
            "commit_limit_gb": None,
            "committed_ratio": None,
            "cache_bytes_perf": None,
            "cache_gb_perf": None,
            "paged_pool_bytes": None,
            "paged_pool_gb": None,
            "nonpaged_pool_bytes": None,
            "nonpaged_pool_gb": None,
        })

    return stats

print(get_memory_info())
print(get_windows_memory_stats())