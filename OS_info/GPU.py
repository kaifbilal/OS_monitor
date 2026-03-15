import re
import subprocess
import winreg

import wmi

def _get_wmi_client(wmi_client=None):
    """Reuse a provided WMI client or create a new one."""
    return wmi_client or wmi.WMI()

def _wmi_dt_to_iso(wmi_dt):
    if not wmi_dt:
        return None
    m = re.match(r"^(\d{4})(\d{2})(\d{2})", str(wmi_dt))
    if not m:
        return str(wmi_dt)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

def _read_directx_from_registry():
    # Try both 64/32-bit registry views
    for flag in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\DirectX",
                                 0, winreg.KEY_READ | flag)
            val, _ = winreg.QueryValueEx(key, "Version")
            winreg.CloseKey(key)
            return val
        except Exception:
            continue
    return None

def _read_directx_via_dxdiag():
    try:
        out = subprocess.check_output(["dxdiag", "/t", "-"], stderr=subprocess.DEVNULL, text=True, timeout=10)
    except Exception:
        # fallback to producing a temp file then reading it (slower)
        try:
            import tempfile, os
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            tf.close()
            subprocess.check_call(["dxdiag", "/t", tf.name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=10)
            with open(tf.name, "r", encoding="utf-8", errors="ignore") as f:
                out = f.read()
            os.unlink(tf.name)
        except Exception:
            return None
    m = re.search(r"DirectX Version:\s*(.+)", out)
    return m.group(1).strip() if m else None


def get_gpus(wmi_client=None):
    """One-time static GPU inventory (name, driver, PCI info, DirectX)."""
    c = _get_wmi_client(wmi_client)
    directx = _read_directx_from_registry() or _read_directx_via_dxdiag()
    results = []
    for vc in c.Win32_VideoController():
        name = getattr(vc, "Name", None)
        drv_ver = getattr(vc, "DriverVersion", None)
        drv_date_raw = getattr(vc, "DriverDate", None) or getattr(vc, "InstalledDisplayDrivers", None)
        drv_date = _wmi_dt_to_iso(drv_date_raw)
        pnp = getattr(vc, "PNPDeviceID", None)

        # try to find LocationInformation via matching PnPEntity
        location = None
        pci_bus = pci_device = pci_function = None
        try:
            if pnp:
                escaped = pnp.replace("\\", "\\\\")
                ents = c.query(f"SELECT * FROM Win32_PnPEntity WHERE DeviceID = '{escaped}'")
                if not ents:
                    ents = c.Win32_PnPEntity(DeviceID=pnp)
                if ents:
                    ent = ents[0]
                    location = getattr(ent, "LocationInformation", None)
            else:
                ents = None
        except Exception:
            location = None

        # parse PCI bus/device/function if present
        if location:
            m = re.search(r"PCI\s*bus\s*(\d+)[^\d]+device\s*(\d+)[^\d]+function\s*(\d+)", location, re.IGNORECASE)
            if m:
                pci_bus, pci_device, pci_function = (int(m.group(1)), int(m.group(2)), int(m.group(3)))

        # fallback: try parsing PNPDeviceID for vendor/device ids
        vid_pid = None
        if pnp:
            mvid = re.search(r"VEN_([0-9A-Fa-f]{4})", pnp)
            mdev = re.search(r"DEV_([0-9A-Fa-f]{4})", pnp)
            if mvid and mdev:
                vid_pid = f"VEN_{mvid.group(1)}&DEV_{mdev.group(1)}"

        results.append({
            "name": name,
            "driver_version": drv_ver,
            "driver_date": drv_date,
            "directx_version": directx,
            "pnp_device_id": pnp,
            "location": location,
            "pci_bus": pci_bus,
            "pci_device": pci_device,
            "pci_function": pci_function,
            "vendor_device": vid_pid
        })
    return results

def get_nvidia_gpu_stats():
    """Dynamic NVIDIA stats via NVML; returns list or None if NVML unavailable."""
    try:
        import pynvml
    except Exception:
        return None

    pynvml.nvmlInit()
    out = []
    dev_count = pynvml.nvmlDeviceGetCount()
    for i in range(dev_count):
        h = pynvml.nvmlDeviceGetHandleByIndex(i)
        name = pynvml.nvmlDeviceGetName(h).decode(errors="ignore")
        util = pynvml.nvmlDeviceGetUtilizationRates(h).gpu
        mem = pynvml.nvmlDeviceGetMemoryInfo(h)
        out.append({
            "index": i,
            "name": name,
            "util_percent": int(util),
            "mem_used_bytes": int(mem.used),
            "mem_total_bytes": int(mem.total),
            "mem_used_gb": round(mem.used / (1024**3), 3),
            "mem_total_gb": round(mem.total / (1024**3), 3),
            "shared_used_bytes": None,
            "shared_total_bytes": None
        })
    pynvml.nvmlShutdown()
    return out


def get_gpu_summary(wmi_client=None):
    """Dynamic GPU summary. Prefers NVML; falls back to WMI memory totals."""
    summary = get_nvidia_gpu_stats()
    if summary is not None:
        return summary

    c = _get_wmi_client(wmi_client)
    out = []
    for idx, vc in enumerate(c.Win32_VideoController()):
        name = getattr(vc, "Name", None)
        vram = getattr(vc, "AdapterRAM", None)
        out.append({
            "index": idx,
            "name": name,
            "util_percent": None,
            "mem_used_bytes": vram,
            "mem_total_bytes": vram,
            "mem_used_gb": None,
            "mem_total_gb": None,
            "shared_used_bytes": None,
            "shared_total_bytes": None
        })
    return out


# print(get_gpus())
print(get_gpu_summary())