"""Твики из пакета Optimize #Expl01t."""

from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak, run_cmd_tweak
from utils.subprocess_helper import run_command, run_powershell


# --- Input / latency ---

def keyboard_data_queue_size_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters",
        "KeyboardDataQueueSize", 50, 100, enabled=True,
    )


def keyboard_data_queue_size_revert(data) -> TweakResult:
    return reg_revert(data)


def mouse_data_queue_size_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters",
        "MouseDataQueueSize", 20, 16, enabled=True,
    )


def mouse_data_queue_size_revert(data) -> TweakResult:
    return reg_revert(data)


def usb_thread_priority_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SYSTEM\CurrentControlSet\Services\USBHUB3\Parameters", "ThreadPriority", 15, 8),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\USBXHCI\Parameters", "ThreadPriority", 15, 8),
    ], message="Приоритет USB-потоков повышен")


def usb_thread_priority_revert(data) -> TweakResult:
    return reg_batch_revert(data)


# --- Visual / UX ---

def show_seconds_in_clock_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "ShowSecondsInSystemClock", 1, 0, enabled=True,
    )


def show_seconds_in_clock_revert(data) -> TweakResult:
    return reg_revert(data)


def enable_numlock_on_boot_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Control Panel\Keyboard",
        "InitialKeyboardIndicators", "2", "0",
        value_type=winreg.REG_SZ, enabled=True,
    )


def enable_numlock_on_boot_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_search_suggestions_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Policies\Microsoft\Windows\Explorer",
        "DisableSearchBoxSuggestions", 1, 0, enabled=True,
    )


def disable_search_suggestions_revert(data) -> TweakResult:
    return reg_revert(data)


# --- Startup / shutdown ---

def disable_autoplay_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers",
        "DisableAutoplay", 1, 0, enabled=True,
    )


def disable_autoplay_revert(data) -> TweakResult:
    return reg_revert(data)


def accelerate_startup_delay_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize",
        "StartupDelayInMSec", 0, 4000, enabled=True,
    )


def accelerate_startup_delay_revert(data) -> TweakResult:
    return reg_revert(data)


def fast_app_shutdown_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Control Panel\Desktop", "AutoEndTasks", "1", "0", winreg.REG_SZ),
        (r"HKCU\Control Panel\Desktop", "HungAppTimeout", "3000", "5000", winreg.REG_SZ),
        (r"HKCU\Control Panel\Desktop", "WaitToKillAppTimeout", "3000", "20000", winreg.REG_SZ),
    ], message="Быстрое завершение приложений включено")


def fast_app_shutdown_revert(data) -> TweakResult:
    return reg_batch_revert(data)


# --- Storage ---

def ntfs_last_access_off_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem",
        "NtfsDisableLastAccessUpdate", 1, 0, enabled=True,
    )


def ntfs_last_access_off_revert(data) -> TweakResult:
    return reg_revert(data)


def ntfs_8dot3_off_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem",
        "NtfsDisable8dot3NameCreation", 1, 0, enabled=True,
    )


def ntfs_8dot3_off_revert(data) -> TweakResult:
    return reg_revert(data)


def ntfs_memory_ssd_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem",
        "NtfsMemoryUsage", 0, 1, enabled=True,
    )


def ntfs_memory_ssd_revert(data) -> TweakResult:
    return reg_revert(data)


def hdd_storage_optimize_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsMemoryUsage", 2, 1),
        (r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsDisable8dot3NameCreation", 1, 0),
        (r"HKLM\SOFTWARE\Microsoft\Dfrg\BootOptimizeFunction", "Enable", "N", "Y", winreg.REG_SZ),
        (r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", 16, 20),
    ], message="Оптимизация HDD применена")


def hdd_storage_optimize_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_low_disk_warnings_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "NoLowDiskSpaceChecks", 1, 0, enabled=True,
    )


def disable_low_disk_warnings_revert(data) -> TweakResult:
    return reg_revert(data)


def nvme_fast_boot_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SYSTEM\CurrentControlSet\Policies\Microsoft\FeatureManagement\Overrides", "735209102", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Policies\Microsoft\FeatureManagement\Overrides", "1853569164", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Policies\Microsoft\FeatureManagement\Overrides", "156965516", 1, 0),
    ], message="NVMe Fast Boot включён")


def nvme_fast_boot_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def large_system_cache_on_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
        "LargeSystemCache", 1, 0, enabled=True,
    )


def large_system_cache_on_revert(data) -> TweakResult:
    return reg_revert(data)


# --- Gaming / GPU ---

def nvidia_disable_preemption_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler", "EnablePreemption", 0, 1),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "DisablePreemption", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "DisableCudaContextPreemption", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\GpuEnergyDrv", "Start", 4, 2),
    ], message="NVIDIA preemption отключён")


def nvidia_disable_preemption_revert(data) -> TweakResult:
    return reg_batch_revert(data)


# --- Privacy ---

def disable_pc_experiments_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\System",
        "AllowExperimentation", 0, 1, enabled=True,
    )


def disable_pc_experiments_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_voice_activation_apply() -> TweakResult:
    return reg_batch_apply([
        (
            r"HKCU\Software\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps",
            "AgentActivationEnabled", 0, 1,
        ),
        (
            r"HKCU\Software\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps",
            "AgentActivationOnLockScreenEnabled", 0, 1,
        ),
    ], message="Голосовая активация отключена")


def disable_voice_activation_revert(data) -> TweakResult:
    return reg_batch_revert(data)


# --- Network (AutoTune-NIC из Optimize #Expl01t) ---

_AUTOTUNE_NIC_PS = r"""
$adapters = Get-NetAdapter -IncludeHidden | Where-Object {
  $_.HardwareInterface -and $_.Status -ne 'Disabled' -and
  ($_.InterfaceDescription -notmatch 'Wi-?Fi|Wireless|Bluetooth|Virtual|Hyper-V|VMware|TAP|Loopback|NPCAP|Docker') -and
  ($_.LinkLayerAddress -and $_.LinkLayerAddress -ne '000000000000')
}
$changed = 0
foreach ($nic in $adapters) {
  $props = Get-NetAdapterAdvancedProperty -Name $nic.Name -ErrorAction SilentlyContinue
  foreach ($p in $props) {
    $dn = $p.DisplayName
    if ($dn -match 'Interrupt Moderation|Модерация прерывания|Energy-Efficient Ethernet|EEE|Flow Control|Управление потоком|Power Saving|Энергосбережение') {
      if ($p.DisplayValue -notmatch 'Disabled|Выкл|Off') {
        try { Set-NetAdapterAdvancedProperty -Name $nic.Name -DisplayName $dn -DisplayValue 'Disabled' -ErrorAction Stop; $changed++ } catch {}
      }
    }
    if ($dn -match 'Receive Buffers|Буферы приема|Буферы приёма') {
      try { Set-NetAdapterAdvancedProperty -Name $nic.Name -DisplayName $dn -DisplayValue 512 -ErrorAction Stop; $changed++ } catch {}
    }
    if ($dn -match 'Transmit Buffers|Буферы передачи') {
      try { Set-NetAdapterAdvancedProperty -Name $nic.Name -DisplayName $dn -DisplayValue 128 -ErrorAction Stop; $changed++ } catch {}
    }
  }
  $pm = Get-NetAdapterPowerManagement -Name $nic.Name -ErrorAction SilentlyContinue
  if ($pm -and $pm.AllowComputerToTurnOffDevice -ne 'Unsupported') {
    $pm.AllowComputerToTurnOffDevice = 'Disabled'
    $pm | Set-NetAdapterPowerManagement -ErrorAction SilentlyContinue
    $changed++
  }
}
Write-Output "NIC tuned: $changed changes"
"""


def autotune_nic_ethernet_apply() -> TweakResult:
    code, out, err = run_powershell(_AUTOTUNE_NIC_PS)
    msg = (out or err or "Ethernet адаптер настроен").strip()
    return TweakResult(code == 0, msg, revert_data={"nic": True})


def autotune_nic_ethernet_revert(_data) -> TweakResult:
    return TweakResult(True, "Верните значения по умолчанию в свойствах сетевого адаптера")


def disable_device_power_saving_apply() -> TweakResult:
    script = (
        "Get-NetAdapter -Physical | Get-NetAdapterPowerManagement -ErrorAction SilentlyContinue | "
        "Where-Object AllowComputerToTurnOffDevice -ne 'Unsupported' | ForEach-Object { "
        "$_.AllowComputerToTurnOffDevice = 'Disabled'; $_ | Set-NetAdapterPowerManagement }; "
        "if (Get-CimClass -Namespace root/wmi -ClassName MSPower_DeviceEnable -ErrorAction SilentlyContinue) { "
        "Get-CimInstance -Namespace root/wmi -ClassName MSPower_DeviceEnable | "
        "Where-Object Enable | ForEach-Object { $_.Enable = $false; Set-CimInstance -InputObject $_ } }"
    )
    code, out, err = run_powershell(script)
    return TweakResult(code == 0, "Энергосбережение устройств отключено" if code == 0 else err, revert_data={"pwr": True})


def disable_device_power_saving_revert(_data) -> TweakResult:
    return TweakResult(True, "Включите энергосбережение в Диспетчере устройств")


# --- Boot / timer ---

def disable_dynamic_tick_apply() -> TweakResult:
    return run_cmd_tweak(
        ["bcdedit", "/set", "disabledynamictick", "yes"],
        ["bcdedit", "/deletevalue", "disabledynamictick"],
    )


def disable_dynamic_tick_revert(data) -> TweakResult:
    cmd = (data or {}).get("revert_cmd")
    if cmd:
        run_command(cmd)
    return TweakResult(True, "Dynamic tick восстановлен")


HANDLERS = {
    "keyboard_data_queue_size": (keyboard_data_queue_size_apply, keyboard_data_queue_size_revert),
    "mouse_data_queue_size": (mouse_data_queue_size_apply, mouse_data_queue_size_revert),
    "usb_thread_priority": (usb_thread_priority_apply, usb_thread_priority_revert),
    "show_seconds_in_clock": (show_seconds_in_clock_apply, show_seconds_in_clock_revert),
    "enable_numlock_on_boot": (enable_numlock_on_boot_apply, enable_numlock_on_boot_revert),
    "disable_search_suggestions": (disable_search_suggestions_apply, disable_search_suggestions_revert),
    "disable_autoplay": (disable_autoplay_apply, disable_autoplay_revert),
    "accelerate_startup_delay": (accelerate_startup_delay_apply, accelerate_startup_delay_revert),
    "fast_app_shutdown": (fast_app_shutdown_apply, fast_app_shutdown_revert),
    "ntfs_last_access_off": (ntfs_last_access_off_apply, ntfs_last_access_off_revert),
    "ntfs_8dot3_off": (ntfs_8dot3_off_apply, ntfs_8dot3_off_revert),
    "ntfs_memory_ssd": (ntfs_memory_ssd_apply, ntfs_memory_ssd_revert),
    "hdd_storage_optimize": (hdd_storage_optimize_apply, hdd_storage_optimize_revert),
    "disable_low_disk_warnings": (disable_low_disk_warnings_apply, disable_low_disk_warnings_revert),
    "nvme_fast_boot": (nvme_fast_boot_apply, nvme_fast_boot_revert),
    "large_system_cache_on": (large_system_cache_on_apply, large_system_cache_on_revert),
    "nvidia_disable_preemption": (nvidia_disable_preemption_apply, nvidia_disable_preemption_revert),
    "disable_pc_experiments": (disable_pc_experiments_apply, disable_pc_experiments_revert),
    "disable_voice_activation": (disable_voice_activation_apply, disable_voice_activation_revert),
    "autotune_nic_ethernet": (autotune_nic_ethernet_apply, autotune_nic_ethernet_revert),
    "disable_device_power_saving": (disable_device_power_saving_apply, disable_device_power_saving_revert),
    "disable_dynamic_tick": (disable_dynamic_tick_apply, disable_dynamic_tick_revert),
}
