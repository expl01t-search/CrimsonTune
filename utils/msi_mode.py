from __future__ import annotations

import winreg
from dataclasses import dataclass
from typing import Any, Iterator

_HKLM = winreg.HKEY_LOCAL_MACHINE
_PCI_ROOT = r"SYSTEM\CurrentControlSet\Enum\PCI"
_MSI_SUB = r"Device Parameters\Interrupt Management\MessageSignaledInterruptProperties"
_AFFINITY_SUB = r"Device Parameters\Interrupt Management\Affinity Policy"
_HIGH_PRIORITY = 3


@dataclass(frozen=True)
class PciDevice:
    hardware_id: str
    instance_id: str
    reg_prefix: str
    description: str
    categories: frozenset[str]


def _read_sz(root: int, path: str, name: str) -> str:
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value) if value is not None else ""
    except OSError:
        return ""


def _classify(hardware_id: str, description: str) -> frozenset[str]:
    hid = hardware_id.upper()
    desc = description.lower()
    cats: set[str] = set()

    if "VEN_10DE" in hid or "nvidia" in desc or "geforce" in desc:
        cats.add("gpu")
    elif "VEN_1002" in hid and any(x in desc for x in ("radeon", "graphics", "gpu")):
        cats.add("gpu")
    elif "VEN_8086" in hid and any(x in desc for x in ("iris", "uhd graphics", "hd graphics")):
        cats.add("gpu")

    if any(x in desc for x in ("ethernet", " wi-fi", "wifi", "wireless", " wlan", "network controller", " lan ")):
        if not any(x in desc for x in ("virtual", "hyper-v", "vmware", "tap", "vpn", "bluetooth")):
            cats.add("network")
    if "realtek" in desc and any(x in desc for x in ("fe ", "gbe", "gaming", "ethernet", " lan")):
        cats.add("network")
    if "intel" in desc and "ethernet" in desc:
        cats.add("network")

    if "usb" in desc and any(
        x in desc for x in ("host controller", "xhci", "extensible", "enhanced host", "usb controller")
    ):
        cats.add("usb")

    return frozenset(cats)


def iter_pci_devices(*, categories: frozenset[str] | None = None) -> Iterator[PciDevice]:
    try:
        with winreg.OpenKey(_HKLM, _PCI_ROOT) as pci_root:
            hw_count = winreg.QueryInfoKey(pci_root)[0]
            for hi in range(hw_count):
                hardware_id = winreg.EnumKey(pci_root, hi)
                with winreg.OpenKey(pci_root, hardware_id) as hw_key:
                    inst_count = winreg.QueryInfoKey(hw_key)[0]
                    for ii in range(inst_count):
                        instance_id = winreg.EnumKey(hw_key, ii)
                        rel = rf"{_PCI_ROOT}\{hardware_id}\{instance_id}"
                        desc = _read_sz(_HKLM, rel, "DeviceDesc") or _read_sz(_HKLM, rel, "FriendlyName")
                        cats = _classify(hardware_id, desc)
                        if not cats:
                            continue
                        if categories and not (cats & categories):
                            continue
                        yield PciDevice(
                            hardware_id=hardware_id,
                            instance_id=instance_id,
                            reg_prefix=rf"HKLM\{rel}",
                            description=desc,
                            categories=cats,
                        )
    except OSError:
        return


def _read_dword_hklm_path(hklm_path: str, subkey: str, name: str) -> Any:
    rel = hklm_path.replace("HKLM\\", "").replace("HKLM/", "")
    full = rf"{rel}\{subkey}"
    try:
        with winreg.OpenKey(_HKLM, full, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except OSError:
        return None


def _write_dword_hklm_path(hklm_path: str, subkey: str, name: str, value: int) -> None:
    rel = hklm_path.replace("HKLM\\", "").replace("HKLM/", "")
    full = rf"{rel}\{subkey}"
    with winreg.CreateKeyEx(_HKLM, full, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)


def _delete_dword_hklm_path(hklm_path: str, subkey: str, name: str) -> None:
    rel = hklm_path.replace("HKLM\\", "").replace("HKLM/", "")
    full = rf"{rel}\{subkey}"
    try:
        with winreg.OpenKey(_HKLM, full, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except OSError:
        pass


def _msi_supported_allowed(device: PciDevice) -> bool:
    old = _read_dword_hklm_path(device.reg_prefix, _MSI_SUB, "MSISupported")
    if old is not None:
        return True
    if "gpu" in device.categories and "VEN_10DE" in device.hardware_id.upper():
        return True
    try:
        rel = device.reg_prefix.replace("HKLM\\", "")
        with winreg.OpenKey(_HKLM, rf"{rel}\{_MSI_SUB}", 0, winreg.KEY_READ):
            return True
    except OSError:
        return False


def apply_msi_high_priority(*, categories: frozenset[str]) -> tuple[list[dict], list[str]]:
    snapshots: list[dict] = []
    labels: list[str] = []
    for device in iter_pci_devices(categories=categories):
        if not (device.categories & categories):
            continue
        snap: dict[str, Any] = {
            "prefix": device.reg_prefix,
            "description": device.description,
            "msi_old": None,
            "priority_old": None,
            "msi_touched": False,
            "priority_touched": False,
        }
        label = device.description or device.hardware_id

        if _msi_supported_allowed(device):
            snap["msi_old"] = _read_dword_hklm_path(device.reg_prefix, _MSI_SUB, "MSISupported")
            _write_dword_hklm_path(device.reg_prefix, _MSI_SUB, "MSISupported", 1)
            snap["msi_touched"] = True

        snap["priority_old"] = _read_dword_hklm_path(device.reg_prefix, _AFFINITY_SUB, "DevicePriority")
        _write_dword_hklm_path(device.reg_prefix, _AFFINITY_SUB, "DevicePriority", _HIGH_PRIORITY)
        snap["priority_touched"] = True

        snapshots.append(snap)
        labels.append(label)
    return snapshots, labels


def revert_msi_high_priority(snapshots: list[dict]) -> None:
    for snap in snapshots or []:
        prefix = snap.get("prefix")
        if not prefix:
            continue
        if snap.get("msi_touched"):
            old = snap.get("msi_old")
            if old is None:
                _delete_dword_hklm_path(prefix, _MSI_SUB, "MSISupported")
            else:
                _write_dword_hklm_path(prefix, _MSI_SUB, "MSISupported", int(old))
        if snap.get("priority_touched"):
            old = snap.get("priority_old")
            if old is None:
                _delete_dword_hklm_path(prefix, _AFFINITY_SUB, "DevicePriority")
            else:
                _write_dword_hklm_path(prefix, _AFFINITY_SUB, "DevicePriority", int(old))


def primary_gpu_msi_active() -> bool:
    for device in iter_pci_devices(categories=frozenset({"gpu"})):
        if _read_dword_hklm_path(device.reg_prefix, _AFFINITY_SUB, "DevicePriority") == _HIGH_PRIORITY:
            msi = _read_dword_hklm_path(device.reg_prefix, _MSI_SUB, "MSISupported")
            if msi == 1:
                return True
    return False
