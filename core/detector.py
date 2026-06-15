"""Определение характеристик системы."""

from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass, field
from typing import Optional

import psutil

from utils.subprocess_helper import run_command, run_powershell


@dataclass
class SystemInfo:
    """Информация о системе."""

    os_name: str = "Windows"
    os_version: str = ""
    os_build: str = ""
    cpu_name: str = ""
    cpu_cores: int = 0
    cpu_threads: int = 0
    ram_total_gb: float = 0.0
    ram_used_gb: float = 0.0
    gpu_name: str = "Не определено"
    gpu_vendor: str = "unknown"
    gpu_vram_gb: float = 0.0
    uptime_hours: float = 0.0
    is_admin: bool = False
    game_mode_enabled: Optional[bool] = None
    hags_enabled: Optional[bool] = None
    power_plan: str = ""


_cached_system_info: SystemInfo | None = None

# WMI AdapterRAM — UInt32, ломается на VRAM > 4 ГБ (RTX 3050 6GB → часто 4 GB).
_WMI_VRAM_OVERFLOW_GB = 4.2


def _classify_gpu_vendor(name: str) -> str:
    lower = name.lower()
    if "nvidia" in lower or "geforce" in lower or "rtx" in lower or "gtx" in lower:
        return "nvidia"
    if "amd" in lower or "radeon" in lower:
        return "amd"
    if "intel" in lower:
        return "intel"
    return "unknown"


def _parse_nvidia_smi_vram(output: str, gpu_name: str = "") -> float:
    """Парсит `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits`."""
    if not output.strip():
        return 0.0
    target = gpu_name.lower().strip()
    fallback = 0.0
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if "," in line:
            name_part, mem_part = line.split(",", 1)
        else:
            parts = line.split()
            if len(parts) < 2:
                continue
            name_part, mem_part = " ".join(parts[:-1]), parts[-1]
        name = name_part.strip().strip('"')
        try:
            mib = float(mem_part.strip().strip('"').replace(" MiB", "").replace(" MB", ""))
        except ValueError:
            continue
        gb = round(mib / 1024, 1)
        fallback = max(fallback, gb)
        if not target:
            continue
        name_l = name.lower()
        if target in name_l or name_l in target:
            return gb
        # Частичное совпадение: RTX 3050 vs GeForce RTX 3050
        for token in target.replace("(", " ").replace(")", " ").split():
            if len(token) >= 4 and token in name_l:
                return gb
    return fallback


def _vram_from_nvidia_smi(gpu_name: str = "") -> float:
    code, out, _ = run_command(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
    )
    if code == 0:
        vram = _parse_nvidia_smi_vram(out, gpu_name)
        if vram > 0:
            return vram
    return 0.0


def _vram_from_nvidia_registry() -> float:
    """QWORD HardwareInformation.qwMemorySize — точный VRAM на Win10+."""
    code, out, _ = run_powershell(
        r"Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Control\Class"
        r"\{4d36e968-e325-11ce-bfc1-08002be10318}' -ErrorAction SilentlyContinue | "
        r"ForEach-Object { Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue } | "
        r"Where-Object { $_.DriverDesc -and $_.'HardwareInformation.qwMemorySize' -gt 0 } | "
        r"Sort-Object { $_.'HardwareInformation.qwMemorySize' } -Descending | "
        r"Select-Object -First 1 -ExpandProperty 'HardwareInformation.qwMemorySize'"
    )
    if code == 0 and out.strip():
        try:
            raw = int(out.strip())
            if raw > 0:
                return round(raw / (1024 ** 3), 1)
        except ValueError:
            pass
    return 0.0


def _vram_from_dxgi() -> float:
    """DedicatedVideoMemory через DXGI (корректно для >4 ГБ)."""
    script = r"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DxgiVram {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct DXGI_ADAPTER_DESC1 {
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string Description;
        public uint VendorId, DeviceId, SubSysId, Revision;
        public UIntPtr DedicatedVideoMemory, DedicatedSystemMemory, SharedSystemMemory;
        public uint Flags;
    }
    [ComImport, Guid("770aae78-f26f-4dda-a829-3c1cce5380f2")]
    public class FactoryGuid {}
    [ComImport, Guid("770aae78-f26f-4dda-a829-3c1cce5380f2"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IDXGIFactory1 {
        [PreserveSig] int EnumAdapters1(uint i, out IntPtr adapter);
    }
    [ComImport, Guid("29038f61-3839-4626-91fd-086879011a05"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IDXGIAdapter1 {
        [PreserveSig] int GetDesc1(out DXGI_ADAPTER_DESC1 desc);
    }
    [DllImport("dxgi.dll", EntryPoint="CreateDXGIFactory1")]
    public static extern int CreateFactory(ref Guid id, [MarshalAs(UnmanagedType.IUnknown)] out object factory);
}
"@ -ErrorAction SilentlyContinue
$max = [uint64]0
$g = [Guid]'770aae78-f26f-4dda-a829-3c1cce5380f2'
$fac = $null
if ([DxgiVram]::CreateFactory([ref]$g, [ref]$fac) -ne 0) { exit 1 }
$factory = [DxgiVram+IDXGIFactory1]$fac
$i = 0
while ($true) {
    $adp = [IntPtr]::Zero
    if ($factory.EnumAdapters1([uint32]$i, [ref]$adp) -ne 0) { break }
    $adapter = [DxgiVram+IDXGIAdapter1][System.Runtime.InteropServices.Marshal]::GetObjectForIUnknown($adp)
    $desc = [DxgiVram+DXGI_ADAPTER_DESC1]::new()
    if ($adapter.GetDesc1([ref]$desc) -eq 0) {
        if ($desc.Description -notmatch 'Microsoft|Basic|Remote') {
            $v = [uint64]$desc.DedicatedVideoMemory
            if ($v -gt $max) { $max = $v }
        }
    }
    [void][System.Runtime.InteropServices.Marshal]::Release($adp)
    $i++
}
if ($max -gt 0) { [Math]::Round($max / 1GB, 1) }
"""
    code, out, _ = run_powershell(script, timeout=20)
    if code == 0 and out.strip():
        try:
            gb = float(out.strip().replace(",", "."))
            if gb > 0:
                return gb
        except ValueError:
            pass
    return 0.0


def _vram_from_wmi() -> float:
    code, out, _ = run_powershell(
        "(Get-CimInstance Win32_VideoController | "
        "Where-Object { $_.Name -notmatch 'Microsoft|Basic|Remote' } | "
        "Sort-Object AdapterRAM -Descending | "
        "Select-Object -First 1 -ExpandProperty AdapterRAM)"
    )
    if code == 0 and out.strip():
        try:
            raw = int(out.strip())
            if raw > 0:
                return round(raw / (1024 ** 3), 1)
        except ValueError:
            pass
    return 0.0


def _detect_gpu_name() -> tuple[str, str]:
    """Имя и вендор GPU без WMI VRAM (он часто неверен)."""
    code, out, _ = run_powershell(
        "Get-CimInstance Win32_VideoController | "
        "Where-Object { $_.Name -notmatch 'Microsoft|Basic|Remote' } | "
        "Select-Object -First 1 -ExpandProperty Name"
    )
    if code == 0 and out.strip():
        name = out.strip()
        return name, _classify_gpu_vendor(name)

    code, out, _ = run_command(["wmic", "path", "win32_VideoController", "get", "name"])
    if code == 0:
        for line in out.splitlines():
            line = line.strip()
            if not line or line == "Name" or "Microsoft" in line or "Basic" in line:
                continue
            return line, _classify_gpu_vendor(line)

    return "Не определено", "unknown"


def _detect_gpu_vram(gpu_name: str, vendor: str) -> float:
    """Точный VRAM: nvidia-smi / DXGI, WMI только как запасной вариант."""
    if vendor == "nvidia":
        vram = _vram_from_nvidia_smi(gpu_name)
        if vram > 0:
            return vram
        vram = _vram_from_nvidia_registry()
        if vram > 0:
            return vram

    if vendor == "amd":
        code, out, _ = run_command(
            ["amd-smi", "static", "--gpu", "0", "--vram"],
        )
        if code == 0 and out.strip():
            try:
                mib = float(out.strip().splitlines()[-1].split()[-1])
                return round(mib / 1024, 1)
            except (ValueError, IndexError):
                pass

    vram = _vram_from_dxgi()
    if vram > 0:
        return vram

    if vendor == "nvidia":
        vram = _vram_from_nvidia_smi()
        if vram > 0:
            return vram

    vram = _vram_from_wmi()
    if 0 < vram <= _WMI_VRAM_OVERFLOW_GB and vendor == "nvidia":
        retry = _vram_from_nvidia_smi(gpu_name) or _vram_from_dxgi()
        if retry > vram:
            return retry
    return vram


def _detect_gpu() -> tuple[str, str, float]:
    """Определяет GPU, вендора и объём VRAM (ГБ)."""
    name, vendor = _detect_gpu_name()
    vram = _detect_gpu_vram(name, vendor)
    return name, vendor, vram


def _get_power_plan() -> str:
    """Возвращает активный план питания."""
    code, out, _ = run_command(["powercfg", "/getactivescheme"])
    if code == 0 and out:
        return out
    return "Неизвестно"


def _read_registry_bool(path: str, name: str) -> Optional[bool]:
    """Читает DWORD из реестра как bool."""
    try:
        import winreg

        parts = path.split("\\", 1)
        root_map = {
            "HKCU": winreg.HKEY_CURRENT_USER,
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
        }
        with winreg.OpenKey(root_map[parts[0]], parts[1], 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return bool(value)
    except OSError:
        return None


def detect_system(*, force: bool = False) -> SystemInfo:
    """Собирает полную информацию о системе (кэшируется)."""
    global _cached_system_info
    if _cached_system_info is not None and not force:
        return _cached_system_info

    from utils.admin import is_admin

    version = platform.version()
    build = version.split(".")[-1] if version else ""

    mem = psutil.virtual_memory()
    boot_time = psutil.boot_time()
    uptime = (psutil.time.time() - boot_time) / 3600

    gpu_name, gpu_vendor, gpu_vram_gb = _detect_gpu()

    cpu_name = platform.processor() or "CPU"
    try:
        code, out, _ = run_powershell(
            "(Get-CimInstance Win32_Processor).Name | Select-Object -First 1"
        )
        if code == 0 and out:
            cpu_name = out.strip()
    except Exception:
        pass

    _cached_system_info = SystemInfo(
        os_name=platform.system(),
        os_version=platform.release(),
        os_build=build,
        cpu_name=cpu_name,
        cpu_cores=psutil.cpu_count(logical=False) or psutil.cpu_count() or 0,
        cpu_threads=psutil.cpu_count(logical=True) or 0,
        ram_total_gb=round(mem.total / (1024 ** 3), 1),
        ram_used_gb=round(mem.used / (1024 ** 3), 1),
        gpu_name=gpu_name,
        gpu_vendor=gpu_vendor,
        gpu_vram_gb=gpu_vram_gb,
        uptime_hours=round(uptime, 1),
        is_admin=is_admin(),
        game_mode_enabled=_read_registry_bool(
            r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled"
        ),
        hags_enabled=_read_registry_bool(
            r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode"
        ),
        power_plan=_get_power_plan(),
    )
    return _cached_system_info


def get_live_stats() -> dict[str, float]:
    """Возвращает текущую загрузку CPU/RAM."""
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "ram_percent": mem.percent,
        "ram_used_gb": round(mem.used / (1024 ** 3), 1),
    }
