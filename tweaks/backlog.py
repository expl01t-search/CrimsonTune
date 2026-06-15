from __future__ import annotations

import os
import shutil
from pathlib import Path

from tweaks.backlog_catalog import BACKLOG_SERVICE_MAP, BACKLOG_TWEAKS, PAUSE_UPDATES_EXTREME_ENTRIES
from tweaks.base import TweakResult
from tweaks.helpers import (
    noop_revert,
    reg_batch_apply,
    reg_batch_revert,
    run_cmd_revert,
    run_cmd_tweak,
    service_revert,
    service_tweak,
)
from tweaks.supplemental_catalog import build_reg_handlers
from utils.nic_reg import active_interface_reg_paths
from utils.subprocess_helper import run_command, run_powershell

# Power settings GUIDs (aliases SUB_USB / CPMINCORES fail on custom plans e.g. PowerX)
_SUB_USB = "2a737441-1930-4402-8d77-b2bebb308086"
_USB_SELECTIVE_SUSPEND = "48e6b7a6-50f5-4782-a5d4-53bb8fb07f85"
_SUB_PROCESSOR = "54533251-82be-4824-96c1-47b60b740d00"
_CP_MIN_CORES = "0cc5b647-c1df-4637-891a-dec35c318583"
_CP_MIN_CORES_ALT = "0ddba9f7-853e-4bd1-8615-9e6e8ae25463"
_PROCTHROTTLEMIN = "893cceff-43e6-4157-9b36-aa6dcb56ae6e"

_USB_SUSPEND_REG = (
    r"HKLM\SYSTEM\CurrentControlSet\Services\USB",
    "DisableSelectiveSuspend",
    1,
    0,
)
_CORE_PARKING_REG = (
    (
        r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings"
        r"\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318583",
        "Attributes",
        2,
        0,
    ),
    (r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", 1, 0),
)


def _power_setting_supported(subgroup: str, setting: str) -> bool:
    code, _, _ = run_command(["powercfg", "/query", "SCHEME_CURRENT", subgroup, setting])
    return code == 0


def _powercfg_scheme_value(
    scheme: str,
    subgroup: str,
    setting: str,
    ac_value: str,
    dc_value: str,
) -> bool:
    ok = True
    for flag, value in (("/setacvalueindex", ac_value), ("/setdcvalueindex", dc_value)):
        code, _, _ = run_command(["powercfg", flag, scheme, subgroup, setting, value])
        if code != 0:
            ok = False
    run_command(["powercfg", "/setactive", scheme])
    return ok


def _powercfg_core_parking_disable() -> bool:
    applied = False
    for setting in (_CP_MIN_CORES, _CP_MIN_CORES_ALT):
        if _power_setting_supported(_SUB_PROCESSOR, setting):
            if _powercfg_scheme_value("SCHEME_CURRENT", _SUB_PROCESSOR, setting, "100", "100"):
                applied = True
    # Minimum processor state 100% — partial effect when core-parking key absent
    if _power_setting_supported(_SUB_PROCESSOR, _PROCTHROTTLEMIN):
        if _powercfg_scheme_value("SCHEME_CURRENT", _SUB_PROCESSOR, _PROCTHROTTLEMIN, "100", "100"):
            applied = True
    return applied

_ENTRIES_BY_ID = {t.id: list(t.entries) for t in BACKLOG_TWEAKS}

_BACKLOG_CUSTOM_IDS = {
    "optimize_netsh_gaming",
    "disable_boot_splash",
    "disable_nic_lso",
    "disable_nic_rss",
    "disable_usb_selective_suspend",
    "disable_cpu_core_parking",
    "enable_compact_os",
    "debloat_uwp_apps",
    "empty_standby_list",
    "kill_gaming_overlays",
    "flush_standby_memory",
    "create_god_mode_folder",
    "disable_telemetry_scheduled_tasks",
    "block_microsoft_telemetry_domains",
    "disable_windows_recall",
    "restore_legacy_photo_viewer",
    "pause_updates_extreme",
}


def _make_service_handler(service: str):
    def apply():
        return service_tweak(service, disabled=True)

    def revert(data):
        return service_revert(data)

    return apply, revert


_CEIP_TASKS = [
    r"\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
    r"\Microsoft\Windows\Customer Experience Improvement Program\KernelCeipTask",
    r"\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
    r"\Microsoft\Windows\Customer Experience Improvement Program\Uploader",
]

_TELEMETRY_HOSTS = [
    "vortex-win.data.microsoft.com",
    "vortex.data.microsoft.com",
    "telecommand.telemetry.microsoft.com",
    "oca.telemetry.microsoft.com",
    "sqm.telemetry.microsoft.com",
    "watson.telemetry.microsoft.com",
    "settings-win.data.microsoft.com",
    "i.telemetry.microsoft.com",
    "df.telemetry.microsoft.com",
    "reports.wes.df.telemetry.microsoft.com",
    "wes.df.telemetry.microsoft.com",
    "services.wes.df.telemetry.microsoft.com",
]

_GAMING_OVERLAY_PROCESSES = [
    "GameBarPresenceWriter.exe",
    "XboxGameBarWidgets.exe",
    "XboxPcAppFT.exe",
    "GameBar.exe",
]

_DEBLOAT_UWP_PS = r"""
$patterns = @(
  'Clipchamp*', 'Microsoft.BingNews', 'Microsoft.BingWeather', 'Microsoft.GetHelp',
  'Microsoft.Getstarted', 'Microsoft.MicrosoftOfficeHub', 'Microsoft.MicrosoftSolitaireCollection',
  'Microsoft.People', 'Microsoft.WindowsFeedbackHub', 'Microsoft.Xbox.TCFApp',
  'Microsoft.XboxGameOverlay', 'Microsoft.XboxGamingOverlay', 'Microsoft.YourPhone',
  'Microsoft.ZuneMusic', 'Microsoft.ZuneVideo', 'MicrosoftTeams', 'Microsoft.Teams',
  'Microsoft.WindowsCommunicationsApps', 'Microsoft.Microsoft3DViewer',
  'Microsoft.MixedReality.Portal', 'Microsoft.SkypeApp', 'Microsoft.OneConnect'
)
$removed = 0
foreach ($pattern in $patterns) {
  Get-AppxPackage -Name $pattern -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-AppxPackage -Package $_.PackageFullName -ErrorAction SilentlyContinue
    $removed++
  }
  Get-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -like $pattern } |
    ForEach-Object {
      Remove-AppxProvisionedPackage -Online -PackageName $_.PackageName -ErrorAction SilentlyContinue
      $removed++
    }
}
Write-Output "Removed packages: $removed"
"""

_PHOTO_VIEWER_PS = r"""
$exts = @('.bmp','.cr2','.dib','.gif','.ico','.jfif','.jpe','.jpeg','.jpg','.jxr','.png','.tif','.tiff','.wdp')
New-Item -Path 'HKLM:\SOFTWARE\Microsoft\Windows Photo Viewer\Capabilities\FileAssociations' -Force | Out-Null
New-Item -Path 'HKLM:\SOFTWARE\Classes\Applications\photoviewer.dll\shell\open\command' -Force | Out-Null
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Classes\Applications\photoviewer.dll\shell\open\command' -Name '(default)' `
  -Value '%SystemRoot%\System32\rundll32.exe "%ProgramFiles%\Windows Photo Viewer\PhotoViewer.dll", ImageView_Fullscreen %1'
foreach ($ext in $exts) {
  $name = $ext.TrimStart('.')
  New-Item -Path "HKLM:\SOFTWARE\Classes\Applications\photoviewer.dll\SupportedTypes\$name" -Force | Out-Null
  Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows Photo Viewer\Capabilities\FileAssociations' `
    -Name $name -Value 'PhotoViewer.FileAssoc.Tiff' -Type String
  New-ItemProperty -Path "HKCR:\$ext\OpenWithProgids" -Name 'PhotoViewer.FileAssoc.Tiff' -PropertyType None -Force | Out-Null
}
Write-Output 'Legacy Photo Viewer associations restored'
"""


def _nic_adapter_toggle(feature: str, enable: bool) -> TweakResult:
    if not active_interface_reg_paths():
        return TweakResult(False, "Активные сетевые интерфейсы не найдены")
    verb = "Enable" if enable else "Disable"
    if feature == "lso":
        action = f"{verb}-NetAdapterLso -Name $_.Name -IPv4 -IPv6 -ErrorAction SilentlyContinue"
        label = "LSO"
    else:
        action = f"{verb}-NetAdapterRss -Name $_.Name -ErrorAction SilentlyContinue"
        label = "RSS"
    script = f"Get-NetAdapter | Where-Object Status -eq 'Up' | ForEach-Object {{ {action} }}"
    code, out, err = run_powershell(script)
    if enable:
        msg = f"{label} включён на активных адаптерах" if code == 0 else (err or out)
    else:
        msg = f"{label} отключён на активных адаптерах" if code == 0 else err
    return TweakResult(code == 0, msg, revert_data={f"nic_{feature}": True} if not enable else None)


def optimize_netsh_gaming_apply() -> TweakResult:
    cmds = [
        [
            "netsh", "int", "tcp", "set", "global",
            "autotuninglevel=disabled", "chimney=disabled", "dca=enabled",
            "netdma=disabled", "ecncapability=enabled", "timestamps=disabled", "rss=enabled",
        ],
        ["netsh", "int", "tcp", "set", "supplemental", "internet", "congestionprovider=ctcp"],
    ]
    for cmd in cmds:
        code, out, err = run_command(cmd)
        if code != 0:
            return TweakResult(False, err or out)
    return TweakResult(True, "Netsh gaming-профиль применён", revert_data={"netsh_gaming": True})


def optimize_netsh_gaming_revert(_data) -> TweakResult:
    revert_cmds = [
        [
            "netsh", "int", "tcp", "set", "global",
            "autotuninglevel=normal", "chimney=disabled", "dca=enabled",
            "netdma=enabled", "ecncapability=disabled", "timestamps=enabled", "rss=enabled",
        ],
        ["netsh", "int", "tcp", "set", "supplemental", "internet", "congestionprovider=default"],
    ]
    for cmd in revert_cmds:
        run_command(cmd)
    return TweakResult(True, "Netsh TCP сброшен к значениям по умолчанию")


def disable_boot_splash_apply() -> TweakResult:
    return run_cmd_tweak(
        ["bcdedit", "/set", "bootuxdisabled", "on"],
        ["bcdedit", "/set", "bootuxdisabled", "off"],
    )


def disable_boot_splash_revert(data) -> TweakResult:
    return run_cmd_revert(data, message="Boot splash восстановлен")


def disable_nic_lso_apply() -> TweakResult:
    return _nic_adapter_toggle("lso", enable=False)


def disable_nic_lso_revert(_data) -> TweakResult:
    return _nic_adapter_toggle("lso", enable=True)


def disable_nic_rss_apply() -> TweakResult:
    return _nic_adapter_toggle("rss", enable=False)


def disable_nic_rss_revert(_data) -> TweakResult:
    return _nic_adapter_toggle("rss", enable=True)


def disable_usb_selective_suspend_apply() -> TweakResult:
    reg_result = reg_batch_apply([_USB_SUSPEND_REG], message="USB DisableSelectiveSuspend=1")
    if not reg_result.success:
        return reg_result
    powercfg_ok = False
    if _power_setting_supported(_SUB_USB, _USB_SELECTIVE_SUSPEND):
        powercfg_ok = _powercfg_scheme_value(
            "SCHEME_CURRENT", _SUB_USB, _USB_SELECTIVE_SUSPEND, "0", "0",
        )
    msg = "USB Selective Suspend отключён (реестр"
    if powercfg_ok:
        msg += " + powercfg"
    msg += ")"
    return TweakResult(True, msg, revert_data={**reg_result.revert_data, "powercfg": powercfg_ok})


def disable_usb_selective_suspend_revert(data) -> TweakResult:
    reg_result = reg_batch_revert(data)
    if reg_result.success and (data or {}).get("powercfg") and _power_setting_supported(_SUB_USB, _USB_SELECTIVE_SUSPEND):
        _powercfg_scheme_value("SCHEME_CURRENT", _SUB_USB, _USB_SELECTIVE_SUSPEND, "1", "1")
    return reg_result


def disable_cpu_core_parking_apply() -> TweakResult:
    reg_result = reg_batch_apply(list(_CORE_PARKING_REG), message="Core parking policies (реестр)")
    if not reg_result.success:
        return reg_result
    powercfg_ok = _powercfg_core_parking_disable()
    msg = "Core Parking: реестр применён"
    if powercfg_ok:
        msg += " · powercfg на текущем плане"
    else:
        msg += " · powercfg недоступен на этом плане (PowerX/кастом) — использован реестр"
    return TweakResult(
        True,
        msg,
        revert_data={**reg_result.revert_data, "powercfg": powercfg_ok},
    )


def disable_cpu_core_parking_revert(data) -> TweakResult:
    reg_result = reg_batch_revert(data)
    if reg_result.success and (data or {}).get("powercfg"):
        for setting in (_CP_MIN_CORES, _CP_MIN_CORES_ALT):
            if _power_setting_supported(_SUB_PROCESSOR, setting):
                _powercfg_scheme_value("SCHEME_CURRENT", _SUB_PROCESSOR, setting, "0", "0")
    return reg_result


def enable_compact_os_apply() -> TweakResult:
    return run_cmd_tweak(
        ["compact", "/CompactOS:always"],
        ["compact", "/CompactOS:never"],
    )


def enable_compact_os_revert(data) -> TweakResult:
    return run_cmd_revert(data, message="Compact OS отключён")


def debloat_uwp_apps_apply() -> TweakResult:
    code, out, err = run_powershell(_DEBLOAT_UWP_PS)
    msg = (out or err or "UWP-приложения удалены").strip()
    return TweakResult(code == 0, msg, revert_data=None)


def debloat_uwp_apps_revert(_data) -> TweakResult:
    return TweakResult(True, "Переустановите приложения через Microsoft Store")


def empty_standby_list_apply() -> TweakResult:
    tool = Path(os.environ.get("TEMP", ".")) / "EmptyStandbyList.exe"
    if not tool.exists():
        code, out, err = run_powershell(
            f"Invoke-WebRequest -Uri 'https://www.wagnardsoft.com/content/img/standby/EmptyStandbyList.exe' "
            f"-OutFile '{tool}' -UseBasicParsing"
        )
        if code != 0 or not tool.exists():
            return TweakResult(False, err or out or "Не удалось загрузить EmptyStandbyList.exe")
    code, out, err = run_command([str(tool), "standbylist"])
    return TweakResult(code == 0, (out or "Standby list очищен").strip(), revert_data=None)


def empty_standby_list_revert(_data) -> TweakResult:
    return noop_revert(_data)


def kill_gaming_overlays_apply() -> TweakResult:
    killed: list[str] = []
    for proc in _GAMING_OVERLAY_PROCESSES:
        code, _, _ = run_command(["taskkill", "/IM", proc, "/F"])
        if code == 0:
            killed.append(proc)
    if killed:
        return TweakResult(True, f"Завершены процессы: {', '.join(killed)}", revert_data=None)
    return TweakResult(True, "Игровые оверлеи не запущены", revert_data=None)


def kill_gaming_overlays_revert(_data) -> TweakResult:
    return noop_revert(_data)


def flush_standby_memory_apply() -> TweakResult:
    script = (
        "$sig = @'\n"
        "using System;\n"
        "using System.Runtime.InteropServices;\n"
        "public static class MemUtil {\n"
        "  [DllImport(\"Psapi.dll\")] public static extern bool EmptyWorkingSet(IntPtr hwProc);\n"
        "}\n"
        "'@\n"
        "Add-Type -TypeDefinition $sig -ErrorAction SilentlyContinue\n"
        "Get-Process | ForEach-Object { [MemUtil]::EmptyWorkingSet($_.Handle) | Out-Null }\n"
        "[System.GC]::Collect()\n"
        "[System.GC]::WaitForPendingFinalizers()\n"
        "Write-Output 'RAM working set trimmed'"
    )
    code, out, err = run_powershell(script)
    return TweakResult(code == 0, (out or "RAM очищена").strip(), revert_data=None)


def flush_standby_memory_revert(_data) -> TweakResult:
    return noop_revert(_data)


def create_god_mode_folder_apply() -> TweakResult:
    desktop = Path.home() / "Desktop"
    folder = desktop / "GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}"
    try:
        folder.mkdir(parents=True, exist_ok=True)
        return TweakResult(True, f"God Mode создан: {folder}", revert_data={"god_mode_path": str(folder)})
    except OSError as exc:
        return TweakResult(False, str(exc))


def create_god_mode_folder_revert(data) -> TweakResult:
    path = Path((data or {}).get("god_mode_path", ""))
    if path.is_dir():
        try:
            path.rmdir()
            return TweakResult(True, "Папка God Mode удалена")
        except OSError as exc:
            return TweakResult(False, str(exc))
    return TweakResult(True, "Папка God Mode не найдена")


def disable_telemetry_scheduled_tasks_apply() -> TweakResult:
    disabled: list[str] = []
    for task in _CEIP_TASKS:
        code, _, _ = run_command(["schtasks", "/Change", "/TN", task, "/DISABLE"])
        if code == 0:
            disabled.append(task)
    if disabled:
        return TweakResult(
            True,
            f"Отключено задач CEIP: {len(disabled)}",
            revert_data={"tasks": disabled},
        )
    return TweakResult(False, "Не удалось отключить задачи CEIP")


def disable_telemetry_scheduled_tasks_revert(data) -> TweakResult:
    for task in (data or {}).get("tasks") or _CEIP_TASKS:
        run_command(["schtasks", "/Change", "/TN", task, "/ENABLE"])
    return TweakResult(True, "Задачи CEIP включены")


def block_microsoft_telemetry_domains_apply() -> TweakResult:
    hosts_path = Path(r"C:\Windows\System32\drivers\etc\hosts")
    backup_path = hosts_path.with_suffix(".hosts.crimsontune.bak")
    try:
        original = hosts_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return TweakResult(False, str(exc))
    if not backup_path.exists():
        try:
            shutil.copy2(hosts_path, backup_path)
        except OSError as exc:
            return TweakResult(False, str(exc))
    marker = "# CrimsonTune telemetry block"
    if marker in original:
        return TweakResult(True, "Блокировка телеметрии уже в hosts", revert_data={"hosts_backup": str(backup_path)})
    lines = [original.rstrip(), "", marker]
    lines.extend(f"127.0.0.1 {host}" for host in _TELEMETRY_HOSTS)
    try:
        hosts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        return TweakResult(False, str(exc))
    return TweakResult(
        True,
        f"Добавлено {len(_TELEMETRY_HOSTS)} записей в hosts",
        revert_data={"hosts_backup": str(backup_path), "marker": marker},
    )


def block_microsoft_telemetry_domains_revert(data) -> TweakResult:
    hosts_path = Path(r"C:\Windows\System32\drivers\etc\hosts")
    backup_path = Path((data or {}).get("hosts_backup", hosts_path.with_suffix(".hosts.crimsontune.bak")))
    if backup_path.exists():
        try:
            shutil.copy2(backup_path, hosts_path)
            return TweakResult(True, "Файл hosts восстановлен из резервной копии")
        except OSError as exc:
            return TweakResult(False, str(exc))
    marker = (data or {}).get("marker", "# CrimsonTune telemetry block")
    try:
        content = hosts_path.read_text(encoding="utf-8", errors="replace")
        if marker in content:
            trimmed = content.split(marker)[0].rstrip() + "\n"
            hosts_path.write_text(trimmed, encoding="utf-8")
        return TweakResult(True, "Записи телеметрии удалены из hosts")
    except OSError as exc:
        return TweakResult(False, str(exc))


def disable_windows_recall_apply() -> TweakResult:
    entries = _ENTRIES_BY_ID.get("disable_windows_recall", [])
    reg_result = (
        reg_batch_apply(entries, message="Recall policies применены")
        if entries
        else TweakResult(True, "Recall policies пропущены")
    )
    if not reg_result.success:
        return reg_result
    code, out, err = run_command(["dism", "/Online", "/Disable-Feature", "/FeatureName:Recall", "/NoRestart"])
    if code != 0:
        combined = f"{err or ''} {out or ''}".lower()
        if "unknown" in combined or "не найден" in combined or "not found" in combined:
            return TweakResult(
                True,
                "Recall policies применены (функция недоступна на этой сборке)",
                revert_data={"reg": reg_result.revert_data, "dism": False},
            )
        return TweakResult(False, err or out, revert_data={"reg": reg_result.revert_data, "dism": True})
    return TweakResult(
        True,
        "Windows Recall отключён",
        revert_data={"reg": reg_result.revert_data, "dism": True},
    )


def disable_windows_recall_revert(data) -> TweakResult:
    payload = data or {}
    reg_data = payload.get("reg")
    if reg_data:
        reg_batch_revert(reg_data)
    if payload.get("dism"):
        run_command(["dism", "/Online", "/Enable-Feature", "/FeatureName:Recall", "/NoRestart"])
    return TweakResult(True, "Windows Recall восстановлен")


def restore_legacy_photo_viewer_apply() -> TweakResult:
    code, out, err = run_powershell(_PHOTO_VIEWER_PS)
    return TweakResult(
        code == 0,
        (out or "Legacy Photo Viewer восстановлен").strip() if code == 0 else err,
        revert_data={"photo_viewer": True},
    )


def restore_legacy_photo_viewer_revert(_data) -> TweakResult:
    return TweakResult(True, "Откат Photo Viewer вручную через «Приложения по умолчанию»")


def pause_updates_extreme_apply() -> TweakResult:
    entries = list(PAUSE_UPDATES_EXTREME_ENTRIES)
    reg_result = reg_batch_apply(entries, message="WU pause policies применены")
    if not reg_result.success:
        return reg_result
    ps = (
        "$until = [DateTime]'2077-01-01'\n"
        "$path = 'HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings'\n"
        "New-Item -Path $path -Force | Out-Null\n"
        "Set-ItemProperty -Path $path -Name 'PauseUpdatesStartTime' -Value $until.ToString('o') -Type String"
    )
    code, out, err = run_powershell(ps)
    if code != 0:
        reg_batch_revert(reg_result.revert_data)
        return TweakResult(False, err or out)
    return TweakResult(True, "Обновления приостановлены до 2077", revert_data=reg_result.revert_data)


def pause_updates_extreme_revert(data) -> TweakResult:
    reg_batch_revert(data)
    run_powershell(
        "Remove-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings' "
        "-Name 'PauseUpdatesStartTime' -ErrorAction SilentlyContinue"
    )
    return TweakResult(True, "Пауза обновлений снята")


handlers = build_reg_handlers([
    t for t in BACKLOG_TWEAKS if t.entries and t.id not in _BACKLOG_CUSTOM_IDS
])

for _tweak_id, _service in BACKLOG_SERVICE_MAP.items():
    handlers[_tweak_id] = _make_service_handler(_service)

handlers.update({
    "optimize_netsh_gaming": (optimize_netsh_gaming_apply, optimize_netsh_gaming_revert),
    "disable_boot_splash": (disable_boot_splash_apply, disable_boot_splash_revert),
    "disable_nic_lso": (disable_nic_lso_apply, disable_nic_lso_revert),
    "disable_nic_rss": (disable_nic_rss_apply, disable_nic_rss_revert),
    "disable_usb_selective_suspend": (disable_usb_selective_suspend_apply, disable_usb_selective_suspend_revert),
    "disable_cpu_core_parking": (disable_cpu_core_parking_apply, disable_cpu_core_parking_revert),
    "enable_compact_os": (enable_compact_os_apply, enable_compact_os_revert),
    "debloat_uwp_apps": (debloat_uwp_apps_apply, debloat_uwp_apps_revert),
    "empty_standby_list": (empty_standby_list_apply, empty_standby_list_revert),
    "kill_gaming_overlays": (kill_gaming_overlays_apply, kill_gaming_overlays_revert),
    "flush_standby_memory": (flush_standby_memory_apply, flush_standby_memory_revert),
    "create_god_mode_folder": (create_god_mode_folder_apply, create_god_mode_folder_revert),
    "disable_telemetry_scheduled_tasks": (
        disable_telemetry_scheduled_tasks_apply,
        disable_telemetry_scheduled_tasks_revert,
    ),
    "block_microsoft_telemetry_domains": (
        block_microsoft_telemetry_domains_apply,
        block_microsoft_telemetry_domains_revert,
    ),
    "disable_windows_recall": (disable_windows_recall_apply, disable_windows_recall_revert),
    "restore_legacy_photo_viewer": (restore_legacy_photo_viewer_apply, restore_legacy_photo_viewer_revert),
    "pause_updates_extreme": (pause_updates_extreme_apply, pause_updates_extreme_revert),
})

HANDLERS = handlers
