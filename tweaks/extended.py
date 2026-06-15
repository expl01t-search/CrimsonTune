
from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak, run_cmd_tweak
from utils.subprocess_helper import run_command, run_powershell, set_service_start_type



def disable_game_bar_presence_apply() -> TweakResult:
    return reg_tweak(r"HKCU\Software\Microsoft\GameBar", "ShowStartupPanel", 0, 1, enabled=True)


def disable_game_bar_presence_revert(data) -> TweakResult:
    return reg_revert(data)


def enable_end_task_rightclick_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "TaskbarEndTask", 1, 0, enabled=True,
    )


def enable_end_task_rightclick_revert(data) -> TweakResult:
    return reg_revert(data)


def mmcss_audio_priority_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Audio",
        "Priority", 6, 2, enabled=True,
    )


def mmcss_audio_priority_revert(data) -> TweakResult:
    return reg_revert(data)


def system_responsiveness_games_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
        "SystemResponsiveness", 0, 20, enabled=True,
    )


def system_responsiveness_games_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_mpo_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Windows\Dwm",
        "OverlayTestMode", 5, 0, enabled=True,
    )


def disable_mpo_revert(data) -> TweakResult:
    return reg_revert(data)


def win32_priority_separation_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl",
        "Win32PrioritySeparation", 38, 2, enabled=True,
    )


def win32_priority_separation_revert(data) -> TweakResult:
    return reg_revert(data)



MANUAL_SERVICES = [
    "DiagTrack", "dmwappushservice", "MapsBroker", "lfsvc",
    "SharedAccess", "WbioSrvc", "WMPNetworkSvc",
]


def set_services_manual_apply() -> TweakResult:
    ok = 0
    for svc in MANUAL_SERVICES:
        code, _ = set_service_start_type(svc, "manual")
        if code == 0:
            ok += 1
    return TweakResult(True, f"Служб переведено в Manual: {ok}", revert_data={"services": MANUAL_SERVICES})


def set_services_manual_revert(data) -> TweakResult:
    for svc in (data or {}).get("services", MANUAL_SERVICES):
        set_service_start_type(svc, "auto")
    return TweakResult(True, "Службы восстановлены")


def disable_widgets_board_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarDa", 0, 1),
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Feeds", "ShellFeedsTaskbarViewMode", 2, 0),
    ], message="Виджеты отключены")


def disable_widgets_board_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_copilot_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "ShowCopilotButton", 0, 1, enabled=True,
    )


def disable_copilot_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_sticky_keys_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Control Panel\Accessibility\StickyKeys",
        "Flags", "506", "510", value_type=winreg.REG_SZ, enabled=True,
    )


def disable_sticky_keys_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_tips_suggestions_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338389Enabled", 0, 1),
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SoftLandingEnabled", 0, 1),
    ], message="Советы отключены")


def disable_tips_suggestions_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_delivery_optimization_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization",
        "DODownloadMode", 0, 1, enabled=True,
    )


def disable_delivery_optimization_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_paging_executive_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
        "DisablePagingExecutive", 1, 0, enabled=True,
    )


def disable_paging_executive_revert(data) -> TweakResult:
    return reg_revert(data)


def large_system_cache_off_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
        "LargeSystemCache", 0, 1, enabled=True,
    )


def large_system_cache_off_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_throttling_idle_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling",
        "PowerThrottlingOff", 1, 0, enabled=True,
    )


def disable_throttling_idle_revert(data) -> TweakResult:
    return reg_revert(data)



def disable_wifi_sense_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\NetworkConnectivityStatusIndicator",
        "DisablePassivePolling", 1, 0, enabled=True,
    )


def disable_wifi_sense_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_activity_history_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "PublishUserActivities", 0, 1),
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", 0, 1),
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "UploadUserActivities", 0, 1),
    ], message="История активности отключена")


def disable_activity_history_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_ink_suggestions_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\InputPersonalization",
        "RestrictImplicitInkCollection", 1, 0, enabled=True,
    )


def disable_ink_suggestions_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_store_suggestions_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
        "SubscribedContent-310093Enabled", 0, 1, enabled=True,
    )


def disable_store_suggestions_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_edge_telemetry_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Edge",
        "MetricsReportingEnabled", 0, 1, enabled=True,
    )


def disable_edge_telemetry_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_defender_samples_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Spynet",
        "SpynetReporting", 0, 1, enabled=True,
    )


def disable_defender_samples_revert(data) -> TweakResult:
    return reg_revert(data)



def disable_ipv6_apply() -> TweakResult:
    code, out, err = run_powershell(
        "Disable-NetAdapterBinding -Name '*' -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue"
    )
    return TweakResult(code == 0, "IPv6 отключён" if code == 0 else err, revert_data={"ipv6": True})


def disable_ipv6_revert(_data) -> TweakResult:
    run_powershell("Enable-NetAdapterBinding -Name '*' -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue")
    return TweakResult(True, "IPv6 включён")


def disable_network_location_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Network Connections",
        "NC_LocationAwareness", 0, 1, enabled=True,
    )


def disable_network_location_revert(data) -> TweakResult:
    return reg_revert(data)


def netsh_tcp_chimney_apply() -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "chimney=enabled"])
    return TweakResult(code == 0, out or err, revert_data={"chimney": True})


def netsh_tcp_chimney_revert(_data) -> TweakResult:
    run_command(["netsh", "int", "tcp", "set", "global", "chimney=disabled"])
    return TweakResult(True, "Chimney отключён")



def enable_dark_mode_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 0, 1),
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", 0, 1),
    ], message="Тёмная тема включена")


def enable_dark_mode_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_bing_search_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search",
        "BingSearchEnabled", 0, 1, enabled=True,
    )


def disable_bing_search_revert(data) -> TweakResult:
    return reg_revert(data)


def show_hidden_files_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "Hidden", 1, 0, enabled=True,
    )


def show_hidden_files_revert(data) -> TweakResult:
    return reg_revert(data)


def remove_onedrive_apply() -> TweakResult:
    code, out, err = run_powershell(
        "if (Get-Process OneDrive -ErrorAction SilentlyContinue) { Stop-Process -Name OneDrive -Force }; "
        "if (Test-Path $env:SystemRoot\\System32\\OneDriveSetup.exe) { "
        "Start-Process $env:SystemRoot\\System32\\OneDriveSetup.exe '/uninstall' -Wait }"
    )
    return TweakResult(code == 0, "OneDrive удаление запущено" if code == 0 else err, revert_data=None)


def remove_onedrive_revert(_data) -> TweakResult:
    return TweakResult(True, "Переустановите OneDrive с сайта Microsoft")


HANDLERS = {
    "disable_game_bar_presence": (disable_game_bar_presence_apply, disable_game_bar_presence_revert),
    "enable_end_task_rightclick": (enable_end_task_rightclick_apply, enable_end_task_rightclick_revert),
    "mmcss_audio_priority": (mmcss_audio_priority_apply, mmcss_audio_priority_revert),
    "system_responsiveness_games": (system_responsiveness_games_apply, system_responsiveness_games_revert),
    "disable_mpo": (disable_mpo_apply, disable_mpo_revert),
    "win32_priority_separation": (win32_priority_separation_apply, win32_priority_separation_revert),
    "set_services_manual": (set_services_manual_apply, set_services_manual_revert),
    "disable_widgets_board": (disable_widgets_board_apply, disable_widgets_board_revert),
    "disable_copilot": (disable_copilot_apply, disable_copilot_revert),
    "disable_sticky_keys": (disable_sticky_keys_apply, disable_sticky_keys_revert),
    "disable_tips_suggestions": (disable_tips_suggestions_apply, disable_tips_suggestions_revert),
    "disable_delivery_optimization": (disable_delivery_optimization_apply, disable_delivery_optimization_revert),
    "disable_paging_executive": (disable_paging_executive_apply, disable_paging_executive_revert),
    "large_system_cache_off": (large_system_cache_off_apply, large_system_cache_off_revert),
    "disable_throttling_idle": (disable_throttling_idle_apply, disable_throttling_idle_revert),
    "disable_wifi_sense": (disable_wifi_sense_apply, disable_wifi_sense_revert),
    "disable_activity_history": (disable_activity_history_apply, disable_activity_history_revert),
    "disable_ink_suggestions": (disable_ink_suggestions_apply, disable_ink_suggestions_revert),
    "disable_store_suggestions": (disable_store_suggestions_apply, disable_store_suggestions_revert),
    "disable_edge_telemetry": (disable_edge_telemetry_apply, disable_edge_telemetry_revert),
    "disable_defender_samples": (disable_defender_samples_apply, disable_defender_samples_revert),
    "disable_ipv6": (disable_ipv6_apply, disable_ipv6_revert),
    "disable_network_location": (disable_network_location_apply, disable_network_location_revert),
    "netsh_tcp_chimney": (netsh_tcp_chimney_apply, netsh_tcp_chimney_revert),
    "enable_dark_mode": (enable_dark_mode_apply, enable_dark_mode_revert),
    "disable_bing_search": (disable_bing_search_apply, disable_bing_search_revert),
    "show_hidden_files": (show_hidden_files_apply, show_hidden_files_revert),
    "remove_onedrive": (remove_onedrive_apply, remove_onedrive_revert),
}
