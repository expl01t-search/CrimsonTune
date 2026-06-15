"""Твики из открытых проектов: WinUtil, Sophia, Winhance."""

from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak, service_tweak
from utils.subprocess_helper import run_command, run_powershell


def disable_storage_sense_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01", 0, 1),
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\StorageSense", "AllowStorageSenseGlobal", 0, 1),
    ], message="Storage Sense отключён")


def disable_storage_sense_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_consumer_features_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent",
        "DisableWindowsConsumerFeatures", 1, 0, enabled=True,
    )


def disable_consumer_features_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_folder_type_discovery_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags\AllFolders\Shell",
        "FolderType", "NotSpecified", "Videos",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def disable_folder_type_discovery_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_start_recommendations_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Explorer", "HideRecommendedPersonalizedSites", 1, 0),
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Start_IrisRecommendations", 0, 1),
    ], message="Рекомендации в меню Пуск отключены")


def disable_start_recommendations_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_filter_keys_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Control Panel\Accessibility\Keyboard Response",
        "Flags", "122", "126",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def disable_filter_keys_revert(data) -> TweakResult:
    return reg_revert(data)


def classic_context_menu_apply() -> TweakResult:
    code, out, err = run_powershell(
        "New-Item -Path 'HKCU:\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}' "
        "-Name 'InprocServer32' -Force -Value '' | Out-Null; "
        "Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue"
    )
    return TweakResult(code == 0, "Классическое контекстное меню включено" if code == 0 else err, revert_data={"classic_menu": True})


def classic_context_menu_revert(_data) -> TweakResult:
    run_powershell(
        "Remove-Item -Path 'HKCU:\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}' "
        "-Recurse -Force -ErrorAction SilentlyContinue; "
        "Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue"
    )
    return TweakResult(True, "Контекстное меню Win11 восстановлено")


def disable_error_reporting_apply() -> TweakResult:
    return service_tweak("WerSvc", disabled=True)


def disable_error_reporting_revert(data) -> TweakResult:
    from tweaks.helpers import service_revert
    return service_revert(data)


def disable_teredo_apply() -> TweakResult:
    code, out, err = run_command(["netsh", "interface", "teredo", "set", "state", "disabled"])
    return TweakResult(code == 0, "Teredo отключён" if code == 0 else err, revert_data={"teredo": True})


def disable_teredo_revert(_data) -> TweakResult:
    run_command(["netsh", "interface", "teredo", "set", "state", "type=default"])
    return TweakResult(True, "Teredo восстановлен")


def enable_long_paths_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem",
        "LongPathsEnabled", 1, 0, enabled=True,
    )


def enable_long_paths_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_scrollbar_autohide_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Control Panel\Accessibility",
        "DynamicScrollbars", 0, 1, enabled=True,
    )


def disable_scrollbar_autohide_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_wpbt_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager",
        "DisableWpbtExecution", 1, 0, enabled=True,
    )


def disable_wpbt_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_windows_ai_registry_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer", "SettingsPageVisibility", "hide:aicomponents", "", winreg.REG_SZ),
        (r"HKLM\SOFTWARE\Policies\WindowsNotepad", "DisableAIFeatures", 1, 0),
    ], message="Windows AI (реестр) отключён")


def disable_windows_ai_registry_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def show_file_extensions_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "HideFileExt", 0, 1, enabled=True,
    )


def show_file_extensions_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_task_view_button_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "ShowTaskViewButton", 0, 1, enabled=True,
    )


def disable_task_view_button_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_acrylic_logon_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System",
        "DisableAcrylicBackgroundOnLogon", 1, 0, enabled=True,
    )


def disable_acrylic_logon_revert(data) -> TweakResult:
    return reg_revert(data)


def exclude_wu_drivers_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate",
        "ExcludeWUDriversInQualityUpdate", 1, 0, enabled=True,
    )


def exclude_wu_drivers_revert(data) -> TweakResult:
    return reg_revert(data)


def mmcss_global_responsiveness_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
        "SystemResponsiveness", 0, 20, enabled=True,
    )


def mmcss_global_responsiveness_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_meet_now_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
        "HideSCAMeetNow", 1, 0, enabled=True,
    )


def disable_meet_now_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_s0_sleep_network_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\F15576E8-98B7-4186-B944-EAFA664402D9",
        "Attributes", 0, 1, enabled=True,
    )


def disable_s0_sleep_network_revert(data) -> TweakResult:
    return reg_revert(data)


HANDLERS = {
    "disable_storage_sense": (disable_storage_sense_apply, disable_storage_sense_revert),
    "disable_consumer_features": (disable_consumer_features_apply, disable_consumer_features_revert),
    "disable_folder_type_discovery": (disable_folder_type_discovery_apply, disable_folder_type_discovery_revert),
    "disable_start_recommendations": (disable_start_recommendations_apply, disable_start_recommendations_revert),
    "disable_filter_keys": (disable_filter_keys_apply, disable_filter_keys_revert),
    "classic_context_menu": (classic_context_menu_apply, classic_context_menu_revert),
    "disable_error_reporting": (disable_error_reporting_apply, disable_error_reporting_revert),
    "disable_teredo": (disable_teredo_apply, disable_teredo_revert),
    "enable_long_paths": (enable_long_paths_apply, enable_long_paths_revert),
    "disable_scrollbar_autohide": (disable_scrollbar_autohide_apply, disable_scrollbar_autohide_revert),
    "disable_wpbt": (disable_wpbt_apply, disable_wpbt_revert),
    "disable_windows_ai_registry": (disable_windows_ai_registry_apply, disable_windows_ai_registry_revert),
    "show_file_extensions": (show_file_extensions_apply, show_file_extensions_revert),
    "disable_task_view_button": (disable_task_view_button_apply, disable_task_view_button_revert),
    "disable_acrylic_logon": (disable_acrylic_logon_apply, disable_acrylic_logon_revert),
    "exclude_wu_drivers": (exclude_wu_drivers_apply, exclude_wu_drivers_revert),
    "mmcss_global_responsiveness": (mmcss_global_responsiveness_apply, mmcss_global_responsiveness_revert),
    "disable_meet_now": (disable_meet_now_apply, disable_meet_now_revert),
    "disable_s0_sleep_network": (disable_s0_sleep_network_apply, disable_s0_sleep_network_revert),
}
