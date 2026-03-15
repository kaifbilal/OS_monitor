import psutil
import time
import cpuinfo
import platform
import subprocess
import re
import wmi
import glob
from cpuinfo import get_cpu_info
import os

system = platform.system()

def get_cpu_utilization():
    utilization =  psutil.cpu_percent(interval=1)
    return utilization

def get_cpu_speed():
    cpu_freq = float(psutil.cpu_freq().current) / 1000
    return cpu_freq

def get_process():
    total_procs = len(psutil.pids())
    return total_procs

def get_threads_handles():
    # Sum threads and handles (handles available on Windows)
    total_threads = 0
    total_handles = 0
    for p in psutil.process_iter(['pid', 'name', 'num_threads']):
        try:
            # num_threads may be available in p.info (faster) or via method
            nt = p.info.get('num_threads') or p.num_threads()
            total_threads += int(nt or 0)

            # num_handles exists on Windows (psutil.Process.num_handles)
            if hasattr(p, "num_handles"):
                try:
                    total_handles += int(p.num_handles() or 0)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return total_threads, total_handles

def get_uptime():
    # Uptime in seconds and formatted
    boot = psutil.boot_time()
    uptime_seconds = int(time.time() - boot)
    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_readable = f"{days}d {hours}h {minutes}m {seconds}s"
    return uptime_readable

def get_cpu_sockets():
    global system
        # Linux: try lscpu, fallback to /proc/cpuinfo physical id
    if system == "Linux":
            try:
                out = subprocess.check_output(["lscpu"], stderr=subprocess.DEVNULL).decode()
                m = re.search(r"Socket\(s\):\s*(\d+)", out)
                if m:
                    return int(m.group(1))
            except Exception:
                pass
            try:
                ids = set()
                with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.startswith("physical id"):
                            ids.add(line.split(":", 1)[1].strip())
                if ids:
                    return len(ids)
            except Exception:
                pass
            return None

        # Windows: use WMI (preferred) or wmic command
    if system == "Windows":
            try:
                return len(wmi.WMI().Win32_Processor())
            except Exception:
                try:
                    out = subprocess.check_output(["wmic", "cpu", "get", "DeviceID"], stderr=subprocess.DEVNULL).decode()
                    lines = [l.strip() for l in out.splitlines() if l.strip() and "DeviceID" not in l]
                    return len(lines) or None
                except Exception:
                    return None

        # macOS: hw.packages if available (typically 1)
    if system == "Darwin":
            try:
                out = subprocess.check_output(["sysctl", "-n", "hw.packages"], stderr=subprocess.DEVNULL).decode().strip()
                return int(out)
            except Exception:
                return 1

    return None

def get_caches():
    global system

    if system == "Linux":
        out = {}
        for idx in sorted(glob.glob("/sys/devices/system/cpu/cpu0/cache/index*")):
            try:
                level = open(os.path.join(idx, "level")).read().strip()
                size = open(os.path.join(idx, "size")).read().strip()   # e.g. "32K"
                out[f"L{level} cache"] = size
            except Exception:
                continue
        return out
    
    if system == "Windows":
        try:
            import wmi
        except ImportError:
            return None
        try:
            c = wmi.WMI()
            l1_cache = 0
            l2_cache = 0
            l3_cache = 0
            caches = []
            for cache in c.Win32_CacheMemory():
                size_kb = int(getattr(cache, "MaxCacheSize", 0) or 0)
                purpose = (getattr(cache, "Purpose", "") or "").lower()
                if "l1" in purpose:
                    l1_cache += size_kb
                elif "l2" in purpose:
                    l2_cache += size_kb
                elif "l3" in purpose:
                    l3_cache += size_kb
                else:
                    caches.append({
                        "Level": cache.Level,
                        "MaxCacheSizeKB": cache.MaxCacheSize,
                        "Name": cache.Name,
                        "Purpose": cache.Purpose
                        })
            if caches:
                return [{"L1 cache":l1_cache}, {"L2 cache":l2_cache}, {"L3 cache":l3_cache}, {"Other caches": caches}]
            return [{"L1 cache":l1_cache}, {"L2 cache":l2_cache}, {"L3 cache":l3_cache}]
        except Exception:
            return None

def detect_virtualization():
        global system
        # 1) cpuinfo flags
        try:
            flags = get_cpu_info().get("flags", [])
            if "hypervisor" in flags:
                return True, "cpuinfo:hypervisor-flag"
        except Exception:
            pass

        # 2) Linux: systemd-detect-virt -> /proc/cpuinfo fallback
        if system == "Linux":
            try:
                p = subprocess.run(["systemd-detect-virt"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
                out = p.stdout.decode().strip()
                if p.returncode == 0 and out:
                    return True, f"systemd-detect-virt:{out}"
            except Exception:
                pass
            try:
                with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
                    if "hypervisor" in f.read():
                        return True, "/proc/cpuinfo:hypervisor-flag"
            except Exception:
                pass

        # 3) Windows: WMIC
        if system == "Windows":
            try:
                out = subprocess.check_output(["wmic", "computersystem", "get", "HypervisorPresent"], stderr=subprocess.DEVNULL)
                lines = [l.strip().lower() for l in out.decode().splitlines() if l.strip()]
                if lines and lines[-1] == "true":
                    return True, "wmic:HypervisorPresent"
            except Exception:
                pass

        # 4) fallback: try virt-what or systeminfo
        try:
            out = subprocess.check_output(["virt-what"], stderr=subprocess.DEVNULL).decode().strip()
            if out:
                return True, f"virt-what:{out}"
        except Exception:
            pass

        return False, "no-hypervisor-detected"

    # Example usage



def dynamic_func():
    utilization = get_cpu_utilization()
    speed = get_cpu_speed()
    process = get_process()
    threads, handles = get_threads_handles()
    return {
        "Utilization": utilization,
        "Speed": speed,
        "Processes": process,
        "CPU Threads": threads,
        "Handles": handles
    }

def static_func():
    info = cpuinfo.get_cpu_info()
    cpu_name = info['brand_raw']
    base_speed = info['hz_actual_friendly']
    sockets = get_cpu_sockets()
    cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    cache = get_caches()
    is_virt, method = detect_virtualization()

    return {
        "CPU": cpu_name,
        "Base Speed": base_speed,
        "Sockets": sockets,
        "Cores": cores,
        "Logical Cores": logical_cores,
        "Cache": cache,
        "Is Virtualized": (is_virt, method)
    }


print(dynamic_func())
print(static_func())