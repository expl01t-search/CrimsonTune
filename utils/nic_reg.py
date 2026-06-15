from __future__ import annotations

import winreg

_INTERFACES = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"


def active_interface_reg_paths() -> list[str]:
    paths: list[str] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _INTERFACES) as base:
            index = 0
            while True:
                try:
                    guid = winreg.EnumKey(base, index)
                    index += 1
                except OSError:
                    break
                sub = rf"{_INTERFACES}\{guid}"
                if _interface_has_address(sub):
                    paths.append(rf"HKLM\{sub}")
    except OSError:
        return []
    return paths


def _interface_has_address(subkey: str) -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey) as key:
            for name in ("DhcpIPAddress", "IPAddress", "DhcpDefaultGateway", "DefaultGateway"):
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                    if value and str(value).strip() not in ("", "0.0.0.0"):
                        return True
                except OSError:
                    continue
    except OSError:
        return False
    return False
