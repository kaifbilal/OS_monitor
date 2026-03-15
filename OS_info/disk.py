import json
import os
import re
import subprocess
import winreg

import psutil
import wmi


def _get_wmi_client(wmi_client=None):
    """Reuse a provided WMI client or create a new one."""
    return wmi_client or wmi.WMI()

def _ps_get_physical_disks():
    try:
        cmd = ['powershell', '-NoProfile',
               '-Command',
               "Get-PhysicalDisk | Select FriendlyName,MediaType,BusType,Size,DeviceId | ConvertTo-Json"]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        # normalize keys
        return {str(d.get("DeviceId")): d for d in data}
    except Exception:
        return {}

def _human(bytes):
    for unit in ['B','KB','MB','GB','TB']:
        if abs(bytes) < 1024.0 or unit == 'TB':
            return f"{bytes:3.2f} {unit}"
        bytes /= 1024.0

def _detect_pagefiles(wmi_client=None):
    """Return set of drive letters that host a pagefile (e.g. {'C:', 'D:'})."""
    c = _get_wmi_client(wmi_client)
    pagefiles = set()

    for cls in (c.Win32_PageFile, c.Win32_PageFileSetting):
        try:
            for pf in cls():
                name = getattr(pf, "Name", "") or ""
                match = re.search(r'([A-Za-z]):', name)
                if match:
                    pagefiles.add(match.group(1).upper() + ":")
        except Exception:
            continue

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management")
        val, _ = winreg.QueryValueEx(key, "PagingFiles")
        if isinstance(val, (list, tuple)):
            for entry in val:
                match = re.search(r'([A-Za-z]):', entry)
                if match:
                    pagefiles.add(match.group(1).upper() + ":")
    except Exception:
        pass

    return pagefiles


def get_disks_info(wmi_client=None):
    """One-time static inventory of disks, partitions, and usage."""
    c = _get_wmi_client(wmi_client)
    ps_disks = _ps_get_physical_disks()
    pagefiles = _detect_pagefiles(c)

    # map disk -> partitions -> logical disks (letters)
    disk_to_part = {}
    for link in c.Win32_DiskDriveToDiskPartition():
        try:
            disk = link.Antecedent   # Win32_DiskDrive
            part = link.Dependent    # Win32_DiskPartition
            # parse DeviceID from antecedent string like '\\\\.\\PHYSICALDRIVE0'
            disk_id = getattr(disk, "DeviceID", None)
            part_name = getattr(part, "DeviceID", None)
            if not disk_id or not part_name:
                continue
            disk_to_part.setdefault(disk_id, []).append(part_name)
        except Exception:
            continue

    part_to_logical = {}
    for link in c.Win32_LogicalDiskToPartition():
        try:
            part = link.Antecedent  # Win32_DiskPartition
            ld = link.Dependent     # Win32_LogicalDisk
            part_name = getattr(part, "DeviceID", None)
            drive_letter = getattr(ld, "DeviceID", None)  # e.g. 'C:'
            if part_name and drive_letter:
                part_to_logical.setdefault(part_name, []).append(drive_letter)
        except Exception:
            continue

    sys_drive = os.environ.get("SystemDrive", None)  # e.g. 'C:'

    results = []
    for d in c.Win32_DiskDrive():
        dev_id = getattr(d, "DeviceID", None)   # \\.\PHYSICALDRIVE0
        model = getattr(d, "Model", "") or ""
        interface = getattr(d, "InterfaceType", "") or ""
        pnp = getattr(d, "PNPDeviceID", "") or ""
        media = getattr(d, "MediaType", "") or ""
        size = int(getattr(d, "Size", 0) or 0)

        # gather partitions -> letters
        parts = disk_to_part.get(dev_id, [])
        letters = []
        for p in parts:
            letters.extend(part_to_logical.get(p, []))
        letters = sorted(set(letters))

        # per-letter usage (choose first letter for capacity display)
        disk_usage = None
        usage_info = []
        for L in letters:
            try:
                mount = L + os.sep  # e.g. 'C:\\'
                du = psutil.disk_usage(mount)
                usage_info.append({
                    "letter": L,
                    "total_bytes": du.total,
                    "used_bytes": du.used,
                    "free_bytes": du.free,
                    "percent": du.percent,
                    "total_human": _human(du.total),
                    "used_human": _human(du.used),
                    "free_human": _human(du.free)
                })
            except Exception:
                continue
        if usage_info:
            # prefer system drive if present, else first
            disk_usage = next((u for u in usage_info if u["letter"] == sys_drive), usage_info[0])

        # type detection: prefer PowerShell Get-PhysicalDisk by DeviceId if available
        ps_info = None
        # DeviceId mapping: try to match by index in DeviceID name
        if dev_id and dev_id.lower().startswith(r"\\.\physicaldrive"):
            try:
                idx = dev_id[len(r"\\.\physicaldrive"):].strip()
                ps_info = ps_disks.get(str(int(idx)))
            except Exception:
                ps_info = None

        media_type = None
        bus_type = None
        if ps_info:
            media_type = ps_info.get("MediaType")
            bus_type = ps_info.get("BusType")
        else:
            # fallback heuristics
            if "ssd" in model.lower() or "nvme" in model.lower() or "ssd" in media.lower():
                media_type = "SSD"
            elif "hdd" in model.lower() or "hard disk" in media.lower():
                media_type = "HDD"
            if "nvme" in pnp.lower() or "nvme" in model.lower():
                bus_type = "NVMe"
            else:
                bus_type = interface or None

        is_system = any(L == sys_drive for L in letters) if sys_drive else False
        is_pagefile = any(L in pagefiles for L in letters)

        results.append({
            "device_id": dev_id,
            "model": model.strip(),
            "interface": interface,
            "pnp_device_id": pnp,
            "media_field": media,
            "size_bytes": size,
            "size_human": _human(size),
            "logical_letters": letters,
            "usage": disk_usage,
            "all_usages": usage_info,
            "is_system_disk": is_system,
            "is_pagefile_host": is_pagefile,
            "media_type": media_type,
            "bus_type": bus_type
        })

    return results

def disk_perf_wmi(name="_Total", wmi_client=None):
    """Dynamic metrics for a logical disk (C:, D:) or physical aggregate (_Total)."""
    c = _get_wmi_client(wmi_client)
    perf = c.Win32_PerfFormattedData_PerfDisk_LogicalDisk(Name=name)
    if not perf:
        return None

    p = perf[0]
    active_pct = float(getattr(p, "PercentDiskTime", 0))
    avg_read_ms = float(getattr(p, "AvgDiskSecPerRead", 0)) * 1000
    avg_write_ms = float(getattr(p, "AvgDiskSecPerWrite", 0)) * 1000
    read_kb_s = int(getattr(p, "DiskReadBytesPerSec", 0)) / 1024
    write_kb_s = int(getattr(p, "DiskWriteBytesPerSec", 0)) / 1024

    reads = float(getattr(p, "DiskReadsPerSec", 0))
    writes = float(getattr(p, "DiskWritesPerSec", 0))
    combined_ms = None
    if reads + writes > 0:
        combined_ms = ((avg_read_ms * reads) + (avg_write_ms * writes)) / (reads + writes)

    return {
        "active_pct": active_pct,
        "avg_read_ms": avg_read_ms,
        "avg_write_ms": avg_write_ms,
        "combined_avg_ms": combined_ms,
        "read_kb_s": read_kb_s,
        "write_kb_s": write_kb_s,
        "reads_per_s": reads,
        "writes_per_s": writes
    }


# print(get_disks_info())
print(disk_perf_wmi())