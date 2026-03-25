import ctypes
from ctypes import wintypes
from time import sleep


AF_UNSPEC = 0
IF_TYPE_IEEE80211 = 71
IF_OPER_STATUS_UP = 1
ERROR_BUFFER_OVERFLOW = 111

PDH_FMT_DOUBLE = 0x00000200

WLAN_CLIENT_VERSION_LONGHORN = 2
wlan_intf_opcode_current_connection = 7
wlan_opcode_value_type_invalid = 0


def _wstr(value):
    return value if value else ""


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


class DOT11_SSID(ctypes.Structure):
    _fields_ = [
        ("uSSIDLength", wintypes.ULONG),
        ("ucSSID", wintypes.BYTE * 32),
    ]


class WLAN_ASSOCIATION_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("dot11Ssid", DOT11_SSID),
        ("dot11BssType", wintypes.DWORD),
        ("dot11Bssid", wintypes.BYTE * 6),
        ("dot11PhyType", wintypes.DWORD),
        ("uDot11PhyIndex", wintypes.DWORD),
        ("wlanSignalQuality", wintypes.DWORD),
        ("ulRxRate", wintypes.DWORD),
        ("ulTxRate", wintypes.DWORD),
    ]


class WLAN_SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("bSecurityEnabled", wintypes.BOOL),
        ("bOneXEnabled", wintypes.BOOL),
        ("dot11AuthAlgorithm", wintypes.DWORD),
        ("dot11CipherAlgorithm", wintypes.DWORD),
    ]


class WLAN_CONNECTION_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("isState", wintypes.DWORD),
        ("wlanConnectionMode", wintypes.DWORD),
        ("strProfileName", wintypes.WCHAR * 256),
        ("wlanAssociationAttributes", WLAN_ASSOCIATION_ATTRIBUTES),
        ("wlanSecurityAttributes", WLAN_SECURITY_ATTRIBUTES),
    ]


class WLAN_INTERFACE_INFO(ctypes.Structure):
    _fields_ = [
        ("InterfaceGuid", GUID),
        ("strInterfaceDescription", wintypes.WCHAR * 256),
        ("isState", wintypes.DWORD),
    ]


class WLAN_INTERFACE_INFO_LIST(ctypes.Structure):
    _fields_ = [
        ("dwNumberOfItems", wintypes.DWORD),
        ("dwIndex", wintypes.DWORD),
        ("InterfaceInfo", WLAN_INTERFACE_INFO * 1),
    ]


class SOCKADDR(ctypes.Structure):
    _fields_ = [
        ("sa_family", wintypes.USHORT),
        ("sa_data", ctypes.c_char * 14),
    ]


class SOCKET_ADDRESS(ctypes.Structure):
    _fields_ = [
        ("lpSockaddr", ctypes.POINTER(SOCKADDR)),
        ("iSockaddrLength", ctypes.c_int),
    ]


class IP_ADAPTER_UNICAST_ADDRESS(ctypes.Structure):
    pass


IP_ADAPTER_UNICAST_ADDRESS._fields_ = [
    ("Length", wintypes.ULONG),
    ("Flags", wintypes.DWORD),
    ("Next", ctypes.POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
    ("Address", SOCKET_ADDRESS),
    ("PrefixOrigin", ctypes.c_int),
    ("SuffixOrigin", ctypes.c_int),
    ("DadState", ctypes.c_int),
    ("ValidLifetime", wintypes.ULONG),
    ("PreferredLifetime", wintypes.ULONG),
    ("LeaseLifetime", wintypes.ULONG),
    ("OnLinkPrefixLength", wintypes.BYTE),
]


class IP_ADAPTER_ADDRESSES(ctypes.Structure):
    pass


IP_ADAPTER_ADDRESSES._fields_ = [
    ("Length", wintypes.ULONG),
    ("IfIndex", wintypes.DWORD),
    ("Next", ctypes.POINTER(IP_ADAPTER_ADDRESSES)),
    ("AdapterName", ctypes.c_char_p),
    ("FirstUnicastAddress", ctypes.POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
    ("FirstAnycastAddress", ctypes.c_void_p),
    ("FirstMulticastAddress", ctypes.c_void_p),
    ("FirstDnsServerAddress", ctypes.c_void_p),
    ("DnsSuffix", wintypes.LPWSTR),
    ("Description", wintypes.LPWSTR),
    ("FriendlyName", wintypes.LPWSTR),
    ("PhysicalAddress", wintypes.BYTE * 8),
    ("PhysicalAddressLength", wintypes.DWORD),
    ("Flags", wintypes.DWORD),
    ("Mtu", wintypes.DWORD),
    ("IfType", wintypes.DWORD),
    ("OperStatus", ctypes.c_int),
    ("Ipv6IfIndex", wintypes.DWORD),
    ("ZoneIndices", wintypes.DWORD * 16),
    ("FirstPrefix", ctypes.c_void_p),
    ("TransmitLinkSpeed", ctypes.c_ulonglong),
    ("ReceiveLinkSpeed", ctypes.c_ulonglong),
]


class PDH_FMT_COUNTERVALUE(ctypes.Structure):
    _fields_ = [
        ("CStatus", wintypes.DWORD),
        ("doubleValue", ctypes.c_double),
    ]


class Wifi:
    def __init__(self):
        self.wlanapi = ctypes.WinDLL("wlanapi", use_last_error=True)
        self.iphlpapi = ctypes.WinDLL("iphlpapi", use_last_error=True)
        self.ws2_32 = ctypes.WinDLL("ws2_32", use_last_error=True)
        self.pdh = ctypes.WinDLL("pdh", use_last_error=True)

        self._configure_wlan()
        self._configure_iphlpapi()
        self._configure_ws2_32()
        self._configure_pdh()

        self._wlan_handle = self._open_wlan_handle()
        self._query = self._open_query()
        self._counters = {
            "send": self._add_wildcard_counters(r"\\Network Interface(*)\\Bytes Sent/sec"),
            "receive": self._add_wildcard_counters(r"\\Network Interface(*)\\Bytes Received/sec"),
            "throughput": self._add_wildcard_counters(r"\\Network Interface(*)\\Current Bandwidth"),
        }
        self._collect()

    def _configure_wlan(self):
        self.wlanapi.WlanOpenHandle.argtypes = [
            wintypes.DWORD,
            ctypes.c_void_p,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self.wlanapi.WlanOpenHandle.restype = wintypes.DWORD

        self.wlanapi.WlanCloseHandle.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.wlanapi.WlanCloseHandle.restype = wintypes.DWORD

        self.wlanapi.WlanEnumInterfaces.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.POINTER(WLAN_INTERFACE_INFO_LIST)),
        ]
        self.wlanapi.WlanEnumInterfaces.restype = wintypes.DWORD

        self.wlanapi.WlanQueryInterface.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(GUID),
            wintypes.DWORD,
            ctypes.c_void_p,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(wintypes.DWORD),
        ]
        self.wlanapi.WlanQueryInterface.restype = wintypes.DWORD

        self.wlanapi.WlanFreeMemory.argtypes = [ctypes.c_void_p]
        self.wlanapi.WlanFreeMemory.restype = None

    def _configure_iphlpapi(self):
        self.iphlpapi.GetAdaptersAddresses.argtypes = [
            wintypes.ULONG,
            wintypes.ULONG,
            ctypes.c_void_p,
            ctypes.POINTER(IP_ADAPTER_ADDRESSES),
            ctypes.POINTER(wintypes.ULONG),
        ]
        self.iphlpapi.GetAdaptersAddresses.restype = wintypes.ULONG

    def _configure_ws2_32(self):
        self.ws2_32.WSAAddressToStringW.argtypes = [
            ctypes.POINTER(SOCKADDR),
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self.ws2_32.WSAAddressToStringW.restype = ctypes.c_int

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

    def _open_wlan_handle(self):
        negotiated = wintypes.DWORD(0)
        handle = ctypes.c_void_p()
        status = self.wlanapi.WlanOpenHandle(
            WLAN_CLIENT_VERSION_LONGHORN,
            None,
            ctypes.byref(negotiated),
            ctypes.byref(handle),
        )
        if status != 0:
            return None
        return handle

    def _open_query(self):
        q = ctypes.c_void_p()
        st = self.pdh.PdhOpenQueryW(None, None, ctypes.byref(q))
        if st != 0:
            return None
        return q

    def _expand_paths(self, wildcard_path):
        if not self._query:
            return []

        size = wintypes.DWORD(0)
        self.pdh.PdhExpandWildCardPathW(None, wildcard_path, None, ctypes.byref(size), 0)
        if size.value == 0:
            return []

        buf = ctypes.create_unicode_buffer(size.value)
        st = self.pdh.PdhExpandWildCardPathW(None, wildcard_path, buf, ctypes.byref(size), 0)
        if st != 0:
            return []
        return [p for p in buf[:].split("\x00") if p]

    def _add_wildcard_counters(self, wildcard_path):
        if not self._query:
            return []
        handles = []
        for p in self._expand_paths(wildcard_path):
            h = ctypes.c_void_p()
            st = self.pdh.PdhAddEnglishCounterW(self._query, p, None, ctypes.byref(h))
            if st == 0:
                handles.append(h)
        return handles

    def _collect(self):
        if self._query:
            self.pdh.PdhCollectQueryData(self._query)

    def _counter_value(self, counter):
        ctype = wintypes.DWORD(0)
        val = PDH_FMT_COUNTERVALUE()
        st = self.pdh.PdhGetFormattedCounterValue(counter, PDH_FMT_DOUBLE, ctypes.byref(ctype), ctypes.byref(val))
        if st != 0:
            return 0.0
        return float(val.doubleValue)

    def _sum_counter_values(self, key):
        return sum(self._counter_value(h) for h in self._counters.get(key, []))

    def _human_bits(self, bits_per_second):
        n = float(max(0.0, bits_per_second))
        for unit in ("bps", "Kbps", "Mbps", "Gbps"):
            if n < 1000.0 or unit == "Gbps":
                return f"{n:.2f} {unit}"
            n /= 1000.0
        return f"{n:.2f} Gbps"

    def _addr_to_string(self, sock_addr):
        if not sock_addr or not sock_addr.lpSockaddr:
            return ""
        buf_len = wintypes.DWORD(128)
        buf = ctypes.create_unicode_buffer(buf_len.value)
        st = self.ws2_32.WSAAddressToStringW(
            sock_addr.lpSockaddr,
            sock_addr.iSockaddrLength,
            None,
            buf,
            ctypes.byref(buf_len),
        )
        if st != 0:
            return ""
        return buf.value.split("%", 1)[0]

    def _get_connected_wlan(self):
        if not self._wlan_handle:
            return None

        p_list = ctypes.POINTER(WLAN_INTERFACE_INFO_LIST)()
        st = self.wlanapi.WlanEnumInterfaces(self._wlan_handle, None, ctypes.byref(p_list))
        if st != 0 or not p_list:
            return None

        try:
            count = p_list.contents.dwNumberOfItems
            array_type = WLAN_INTERFACE_INFO * count
            infos = ctypes.cast(
                ctypes.addressof(p_list.contents.InterfaceInfo),
                ctypes.POINTER(array_type),
            ).contents

            for info in infos:
                data_size = wintypes.DWORD(0)
                data_ptr = ctypes.c_void_p()
                op_type = wintypes.DWORD(wlan_opcode_value_type_invalid)
                qst = self.wlanapi.WlanQueryInterface(
                    self._wlan_handle,
                    ctypes.byref(info.InterfaceGuid),
                    wlan_intf_opcode_current_connection,
                    None,
                    ctypes.byref(data_size),
                    ctypes.byref(data_ptr),
                    ctypes.byref(op_type),
                )
                if qst != 0 or not data_ptr:
                    continue

                try:
                    conn = ctypes.cast(data_ptr, ctypes.POINTER(WLAN_CONNECTION_ATTRIBUTES)).contents
                    ssid_len = int(conn.wlanAssociationAttributes.dot11Ssid.uSSIDLength)
                    ssid_bytes = bytes(conn.wlanAssociationAttributes.dot11Ssid.ucSSID[:ssid_len])
                    ssid = ssid_bytes.decode("utf-8", errors="ignore")
                    phy = self._phy_to_text(int(conn.wlanAssociationAttributes.dot11PhyType))
                    signal = int(conn.wlanAssociationAttributes.wlanSignalQuality)
                    rx = int(conn.wlanAssociationAttributes.ulRxRate)
                    tx = int(conn.wlanAssociationAttributes.ulTxRate)

                    return {
                        "adapter_name": _wstr(info.strInterfaceDescription),
                        "ssid": ssid,
                        "connection_type": phy,
                        "signal_strength": signal,
                        "rx_bps": rx,
                        "tx_bps": tx,
                    }
                finally:
                    self.wlanapi.WlanFreeMemory(data_ptr)
        finally:
            self.wlanapi.WlanFreeMemory(p_list)

        return None

    def _phy_to_text(self, phy):
        mapping = {
            1: "802.11a",
            2: "802.11b",
            3: "802.11g",
            4: "802.11n",
            5: "802.11ac",
            8: "802.11ax",
        }
        return mapping.get(phy, f"PHY({phy})")

    def _get_wifi_adapter_addresses(self):
        size = wintypes.ULONG(0)
        self.iphlpapi.GetAdaptersAddresses(AF_UNSPEC, 0, None, None, ctypes.byref(size))
        if size.value == 0:
            return None

        buf = ctypes.create_string_buffer(size.value)
        first = ctypes.cast(buf, ctypes.POINTER(IP_ADAPTER_ADDRESSES))
        st = self.iphlpapi.GetAdaptersAddresses(AF_UNSPEC, 0, None, first, ctypes.byref(size))
        if st != 0:
            if st == ERROR_BUFFER_OVERFLOW:
                buf = ctypes.create_string_buffer(size.value)
                first = ctypes.cast(buf, ctypes.POINTER(IP_ADAPTER_ADDRESSES))
                st = self.iphlpapi.GetAdaptersAddresses(AF_UNSPEC, 0, None, first, ctypes.byref(size))
            if st != 0:
                return None

        candidates = []
        current = first
        while current:
            a = current.contents
            if int(a.IfType) == IF_TYPE_IEEE80211 and int(a.OperStatus) == IF_OPER_STATUS_UP:
                friendly = _wstr(a.FriendlyName)
                desc = _wstr(a.Description)
                lower = (friendly + " " + desc).lower()
                is_virtual = ("virtual" in lower) or ("wi-fi direct" in lower) or ("loopback" in lower)

                ipv4 = ""
                ipv6 = ""
                u = a.FirstUnicastAddress
                while u:
                    ua = u.contents
                    addr = self._addr_to_string(ua.Address)
                    if addr:
                        if ":" in addr and not ipv6:
                            ipv6 = addr
                        elif "." in addr and not ipv4:
                            ipv4 = addr
                    u = ua.Next

                tx = int(a.TransmitLinkSpeed)
                rx = int(a.ReceiveLinkSpeed)
                # Ignore common sentinel values such as ULONG64 max.
                if tx > 10_000_000_000_000:
                    tx = 0
                if rx > 10_000_000_000_000:
                    rx = 0

                candidates.append(
                    {
                        "driver_name": desc,
                        "adapter_name": friendly,
                        "ipv4": ipv4 or "N/A",
                        "ipv6": ipv6 or "N/A",
                        "tx_link_bps": tx,
                        "rx_link_bps": rx,
                        "is_virtual": is_virtual,
                    }
                )

            current = a.Next

        if not candidates:
            return None

        for c in candidates:
            if not c["is_virtual"]:
                return c
        return candidates[0]

    def get_wifi_info(self):
        wlan = self._get_connected_wlan() or {}
        net = self._get_wifi_adapter_addresses() or {}

        adapter_name = net.get("adapter_name") or wlan.get("adapter_name") or "N/A"
        current_speed_bps = max(int(net.get("tx_link_bps") or 0), int(net.get("rx_link_bps") or 0))

        return {
            "driver_name": net.get("driver_name") or "N/A",
            "adapter_name": adapter_name,
            "ssid": wlan.get("ssid") or "N/A",
            "connection_type": wlan.get("connection_type") or "N/A",
            "ipv4_address": net.get("ipv4") or "N/A",
            "ipv6_address": net.get("ipv6") or "N/A",
            "current_internet_speed": self._human_bits(current_speed_bps),
        }

    def get_wifi_looped_info(self):
        wlan = self._get_connected_wlan() or {}

        self._collect()
        send_bps = self._sum_counter_values("send") * 8.0
        recv_bps = self._sum_counter_values("receive") * 8.0
        throughput_bps = self._sum_counter_values("throughput")

        return {
            "signal_strength": f"{int(wlan.get('signal_strength') or 0)}%",
            "send": self._human_bits(send_bps),
            "receive": self._human_bits(recv_bps),
            "throughput": self._human_bits(throughput_bps),
        }

    def close(self):
        if self._query:
            self.pdh.PdhCloseQuery(self._query)
            self._query = None
        if self._wlan_handle:
            self.wlanapi.WlanCloseHandle(self._wlan_handle, None)
            self._wlan_handle = None


if __name__ == "__main__":
    wifi = Wifi()
    print("WiFi Info:", wifi.get_wifi_info())
    for _ in range(1):
        print("WiFi Looped Info:", wifi.get_wifi_looped_info())
        # sleep(1)
    wifi.close()
