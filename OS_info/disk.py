import ctypes
import os
import time
from ctypes import wintypes
from time import sleep


GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

IOCTL_DISK_GET_LENGTH_INFO = 0x0007405C
IOCTL_DISK_PERFORMANCE = 0x00070020
IOCTL_STORAGE_QUERY_PROPERTY = 0x002D1400


class STORAGE_PROPERTY_QUERY(ctypes.Structure):
    _fields_ = [
        ("PropertyId", wintypes.DWORD),
        ("QueryType", wintypes.DWORD),
        ("AdditionalParameters", wintypes.BYTE * 1),
    ]


class STORAGE_DESCRIPTOR_HEADER(ctypes.Structure):
    _fields_ = [
        ("Version", wintypes.DWORD),
        ("Size", wintypes.DWORD),
    ]


class STORAGE_DEVICE_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ("Version", wintypes.DWORD),
        ("Size", wintypes.DWORD),
        ("DeviceType", wintypes.BYTE),
        ("DeviceTypeModifier", wintypes.BYTE),
        ("RemovableMedia", wintypes.BOOLEAN),
        ("CommandQueueing", wintypes.BOOLEAN),
        ("VendorIdOffset", wintypes.DWORD),
        ("ProductIdOffset", wintypes.DWORD),
        ("ProductRevisionOffset", wintypes.DWORD),
        ("SerialNumberOffset", wintypes.DWORD),
        ("BusType", wintypes.BYTE),
        ("RawPropertiesLength", wintypes.DWORD),
    ]


class DISK_PERFORMANCE(ctypes.Structure):
    _fields_ = [
        ("BytesRead", ctypes.c_longlong),
        ("BytesWritten", ctypes.c_longlong),
        ("ReadTime", ctypes.c_longlong),
        ("WriteTime", ctypes.c_longlong),
        ("IdleTime", ctypes.c_longlong),
        ("ReadCount", wintypes.DWORD),
        ("WriteCount", wintypes.DWORD),
        ("QueueDepth", wintypes.DWORD),
        ("SplitCount", wintypes.DWORD),
        ("QueryTime", ctypes.c_longlong),
        ("StorageDeviceNumber", wintypes.DWORD),
        ("StorageManagerName", wintypes.WCHAR * 8),
    ]


class Disk:
    def __init__(self):
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._configure_apis()
        self.system_root = self._get_system_drive_root()
        self.volume_handle = self._open_system_volume()
        self.max_transfer_mb_s = 0.0
        self._last = self._read_perf_raw()

    def _configure_apis(self):
        self.kernel32.CreateFileW.restype = wintypes.HANDLE
        self.kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]

        self.kernel32.DeviceIoControl.restype = wintypes.BOOL
        self.kernel32.DeviceIoControl.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID,
        ]

        self.kernel32.GetDiskFreeSpaceExW.restype = wintypes.BOOL
        self.kernel32.GetDiskFreeSpaceExW.argtypes = [
            wintypes.LPCWSTR,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
        ]

        self.kernel32.GetWindowsDirectoryW.restype = wintypes.UINT
        self.kernel32.GetWindowsDirectoryW.argtypes = [wintypes.LPWSTR, wintypes.UINT]

        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL

    def _get_system_drive_root(self):
        buf = ctypes.create_unicode_buffer(260)
        if self.kernel32.GetWindowsDirectoryW(buf, 260) == 0:
            return "C:\\"
        drive = os.path.splitdrive(buf.value)[0]
        return drive + "\\" if drive else "C:\\"

    def _open_system_volume(self):
        volume = r"\\.\{}".format(self.system_root.rstrip("\\"))
        handle = self.kernel32.CreateFileW(
            volume,
            0,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None,
        )
        if not handle or handle == INVALID_HANDLE_VALUE:
            return None
        return handle

    def _human_bytes(self, value):
        units = ["B", "KB", "MB", "GB", "TB"]
        num = float(value)
        for unit in units:
            if num < 1024.0 or unit == units[-1]:
                return f"{num:.2f} {unit}"
            num /= 1024.0
        return f"{num:.2f} TB"

    def _read_formatted_size(self):
        free_bytes = ctypes.c_ulonglong(0)
        total_bytes = ctypes.c_ulonglong(0)
        total_free = ctypes.c_ulonglong(0)
        ok = self.kernel32.GetDiskFreeSpaceExW(
            self.system_root,
            ctypes.byref(free_bytes),
            ctypes.byref(total_bytes),
            ctypes.byref(total_free),
        )
        if not ok:
            return None
        return total_bytes.value

    def _read_capacity(self):
        if not self.volume_handle:
            return self._read_formatted_size()
        out_buf = ctypes.c_longlong(0)
        returned = wintypes.DWORD(0)
        ok = self.kernel32.DeviceIoControl(
            self.volume_handle,
            IOCTL_DISK_GET_LENGTH_INFO,
            None,
            0,
            ctypes.byref(out_buf),
            ctypes.sizeof(out_buf),
            ctypes.byref(returned),
            None,
        )
        if not ok:
            return self._read_formatted_size()
        return max(0, out_buf.value)

    def _detect_drive_type(self):
        if not self.volume_handle:
            return "Unknown"

        query = STORAGE_PROPERTY_QUERY()
        query.PropertyId = 0
        query.QueryType = 0
        query.AdditionalParameters[0] = 0

        header = STORAGE_DESCRIPTOR_HEADER()
        returned = wintypes.DWORD(0)
        ok = self.kernel32.DeviceIoControl(
            self.volume_handle,
            IOCTL_STORAGE_QUERY_PROPERTY,
            ctypes.byref(query),
            ctypes.sizeof(query),
            ctypes.byref(header),
            ctypes.sizeof(header),
            ctypes.byref(returned),
            None,
        )
        if not ok or header.Size == 0:
            return "Unknown"

        raw = ctypes.create_string_buffer(header.Size)
        ok = self.kernel32.DeviceIoControl(
            self.volume_handle,
            IOCTL_STORAGE_QUERY_PROPERTY,
            ctypes.byref(query),
            ctypes.sizeof(query),
            raw,
            ctypes.sizeof(raw),
            ctypes.byref(returned),
            None,
        )
        if not ok:
            return "Unknown"

        desc = STORAGE_DEVICE_DESCRIPTOR.from_buffer_copy(raw)
        bus_type = int(desc.BusType)

        # STORAGE_BUS_TYPE enum values commonly used by Windows.
        if bus_type == 17:
            return "SSD(NVMe)"
        if bus_type in (11, 12):
            return "SSD"
        if bus_type in (3, 8, 10):
            return "HDD"

        text = raw.raw.decode("latin-1", errors="ignore").lower()
        if "nvme" in text:
            return "SSD(NVMe)"
        if "ssd" in text:
            return "SSD"
        if "hdd" in text or "sata" in text or "ata" in text:
            return "HDD"
        return "Unknown"

    def _read_perf_raw(self):
        if not self.volume_handle:
            return None
        perf = DISK_PERFORMANCE()
        returned = wintypes.DWORD(0)
        ok = self.kernel32.DeviceIoControl(
            self.volume_handle,
            IOCTL_DISK_PERFORMANCE,
            None,
            0,
            ctypes.byref(perf),
            ctypes.sizeof(perf),
            ctypes.byref(returned),
            None,
        )
        if not ok:
            return None
        return {
            "t": time.perf_counter(),
            "bytes_read": int(perf.BytesRead),
            "bytes_written": int(perf.BytesWritten),
            "read_time_100ns": int(perf.ReadTime),
            "write_time_100ns": int(perf.WriteTime),
            "idle_time_100ns": int(perf.IdleTime),
            "reads": int(perf.ReadCount),
            "writes": int(perf.WriteCount),
        }

    def get_disk_info(self):
        capacity = self._read_capacity()
        formatted = self._read_formatted_size()
        drive_type = self._detect_drive_type()
        return {
            "capacity": self._human_bytes(capacity) if capacity is not None else "N/A",
            "formatted": self._human_bytes(formatted) if formatted is not None else "N/A",
            "system_disk": "Yes",
            "type": drive_type,
            "max_disk_transfer_rate": f"{self.max_transfer_mb_s:.2f} MB/s",
        }

    def get_loopback_info(self):
        current = self._read_perf_raw()
        if current is None or self._last is None:
            self._last = current
            return {
                "active_time": "N/A",
                "average_response_time": "N/A",
                "read_speed": "0.00 KB/s",
                "write_speed": "0.00 KB/s",
                "disk_transfer_rate": "0.00 MB/s",
            }

        # When samples are too close in time, counters often look like zeros.
        # Take one short delayed sample to produce stable rates.
        dt = current["t"] - self._last["t"]
        if dt < 0.25:
            time.sleep(0.25)
            current = self._read_perf_raw()
            if current is None:
                return {
                    "active_time": "N/A",
                    "average_response_time": "N/A",
                    "read_speed": "0.00 KB/s",
                    "write_speed": "0.00 KB/s",
                    "disk_transfer_rate": "0.00 MB/s",
                }

        dt = current["t"] - self._last["t"]
        if dt <= 0:
            dt = 1e-6

        rb = max(0, current["bytes_read"] - self._last["bytes_read"])
        wb = max(0, current["bytes_written"] - self._last["bytes_written"])
        rr = max(0, current["reads"] - self._last["reads"])
        wr = max(0, current["writes"] - self._last["writes"])
        rt = max(0, current["read_time_100ns"] - self._last["read_time_100ns"])
        wt = max(0, current["write_time_100ns"] - self._last["write_time_100ns"])
        idle = max(0, current["idle_time_100ns"] - self._last["idle_time_100ns"])

        read_kb_s = rb / dt / 1024.0
        write_kb_s = wb / dt / 1024.0
        total_mb_s = (rb + wb) / dt / (1024.0 * 1024.0)
        self.max_transfer_mb_s = max(self.max_transfer_mb_s, total_mb_s)

        # IOCTL_DISK_PERFORMANCE times are in 100ns units.
        total_ops = rr + wr
        avg_ms = ((rt + wt) / total_ops / 10000.0) if total_ops > 0 else 0.0
        active_pct = 100.0 - ((idle / dt) / 10_000_000.0 * 100.0)
        active_pct = max(0.0, min(100.0, active_pct))

        self._last = current
        return {
            "active_time": f"{active_pct:.2f}%",
            "average_response_time": f"{avg_ms:.2f} ms",
            "read_speed": f"{read_kb_s:.2f} KB/s",
            "write_speed": f"{write_kb_s:.2f} KB/s",
            "disk_transfer_rate": f"{total_mb_s:.2f} MB/s",
        }

    def close(self):
        if self.volume_handle:
            self.kernel32.CloseHandle(self.volume_handle)
            self.volume_handle = None


if __name__ == "__main__":
    disk = Disk()
    disk_info = disk.get_disk_info()
    print("Disk Info:", disk_info)
    for _ in range(5):
        loopback_info = disk.get_loopback_info()
        print("Loop Back Info:", loopback_info)
        sleep(1)
    # print max after sampling so the static section can be refreshed by caller
    disk.close()
