"""Определение текущего состояния твиков в системе."""

from __future__ import annotations

import os
import winreg
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Optional

from utils import registry as reg
from utils.subprocess_helper import run_command, run_powershell


class TweakStatus(str, Enum):
    """Статус твика относительно желаемого состояния."""

    INACTIVE = "inactive"              # Не применён — можно включать
    ACTIVE_SYSTEM = "active_system"    # Уже активен в Windows (вручную или другим софтом)
    APPLIED_APP = "applied_app"        # Применён через CrimsonTune
    ACTIVE_BOTH = "active_both"        # И в системе, и записан в CrimsonTune
    UNKNOWN = "unknown"                # Невозможно определить
    ONE_SHOT = "one_shot"              # Разовое действие — не отслеживается
    INCOMPATIBLE = "incompatible"


STATUS_LABELS = {
    TweakStatus.INACTIVE: "Доступен",
    TweakStatus.ACTIVE_SYSTEM: "Уже включено в системе",
    TweakStatus.APPLIED_APP: "Применено CrimsonTune",
    TweakStatus.ACTIVE_BOTH: "Уже активно",
    TweakStatus.UNKNOWN: "Статус неизвестен",
    TweakStatus.ONE_SHOT: "Разовое действие",
    TweakStatus.INCOMPATIBLE: "Несовместимо",
}

STATUS_COLORS = {
    TweakStatus.INACTIVE: "#9aa3b8",
    TweakStatus.ACTIVE_SYSTEM: "#00c896",
    TweakStatus.APPLIED_APP: "#d63031",
    TweakStatus.ACTIVE_BOTH: "#00c896",
    TweakStatus.UNKNOWN: "#6b7280",
    TweakStatus.ONE_SHOT: "#ffcc00",
    TweakStatus.INCOMPATIBLE: "#ff4466",
}


@dataclass
class TweakStateInfo:
    """Полная информация о состоянии твика."""

    tweak_id: str
    status: TweakStatus
    is_active: bool          # Желаемое состояние уже достигнуто
    can_apply: bool          # Можно применять (не активен)
    applied_by_app: bool
    active_in_system: bool
    detail: str = ""


# Разовые действия — не блокируем повтор, но не считаем «уже активным»
ONE_SHOT_TWEAKS = {
    "clear_temp_files",
    "flush_dns",
    "clear_shader_cache",
    "export_dxdiag",
    "reset_winsock",
    "directx_12_ultimate_hint",
    "nvidia_threaded_optimization",
    "nvidia_max_performance",
    "nvidia_low_latency",
    "amd_anti_lag",
    "amd_texture_quality_performance",
    "nvidia_reflex_hint",
    "remove_onedrive",
    "set_services_manual",
    "disable_ipv6",
    "netsh_tcp_chimney",
    "autotune_nic_ethernet",
    "disable_device_power_saving",
    "classic_context_menu",
    "disable_teredo",
}


def _reg_eq(path: str, name: str, expected) -> bool:
    actual = reg.read_value(path, name, default=None)
    if actual is None:
        return False
    if isinstance(expected, str):
        return str(actual).lower() == expected.lower()
    return actual == expected


def _reg_bool(path: str, name: str, expected: bool) -> bool:
    val = reg.read_value(path, name, default=None)
    if val is None:
        return False
    return bool(val) == expected


def _service_disabled(name: str) -> bool:
    code, out, _ = run_command(["sc", "query", name])
    if code != 0:
        return True  # служба не найдена / не запущена
    return "STOPPED" in out or "DISABLED" in out.upper()


def _service_running(name: str) -> bool:
    code, out, _ = run_command(["sc", "query", name])
    return code == 0 and "RUNNING" in out


def _power_plan_active(guid: str) -> bool:
    code, out, _ = run_command(["powercfg", "/getactivescheme"])
    return code == 0 and guid.lower() in out.lower()


def _hibernation_off() -> bool:
    code, out, _ = run_command(["powercfg", "/a"])
    if code != 0:
        return False
    lower = out.lower()
    return ("hibernation" in lower and "not" in lower) or ("гибернация" in lower and "не" in lower)


# Проверки: tweak_id → функция, возвращающая True если желаемое состояние УЖЕ достигнуто
SYSTEM_CHECKS: dict[str, Callable[[], bool]] = {
    # Performance
    "disable_sysmain": lambda: _service_disabled("SysMain"),
    "disable_search_indexing": lambda: _service_disabled("WSearch"),
    "disable_prefetch": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
        "EnablePrefetcher", 0,
    ),
    "high_timer_resolution": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel",
        "GlobalTimerResolutionRequests", True,
    ),
    "disable_background_apps": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
        "GlobalUserDisabled", True,
    ),
    "disable_hibernation": _hibernation_off,
    "optimize_svchost": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Control",
        "SvcHostSplitThresholdInKB", 380000,
    ),
    "disable_hags": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", 1,
    ),
    "disable_game_dvr": lambda: _reg_bool(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", False),
    "disable_fullscreen_optimizations": lambda: _reg_eq(
        r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2,
    ),
    "disable_mouse_acceleration": lambda: _reg_eq(
        r"HKCU\Control Panel\Mouse", "MouseSpeed", "0",
    ),
    "mmcss_games_priority": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
        "GPU Priority", 8,
    ),
    "disable_xbox_services": lambda: all(
        _service_disabled(s) for s in ["XblAuthManager", "XblGameSave", "XboxGipSvc", "XboxNetApiSvc"]
    ),

    # DirectX
    "enable_shader_cache": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "DpiMapIommuContiguous", True,
    ),
    "disable_dxgi_flip_model": lambda: "SwapEffectUpgradeEnable=0" in str(
        reg.read_value(r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences", "DirectXUserGlobalSettings", "")
    ),

    # OpenGL
    "force_discrete_gpu_opengl": lambda: "GpuPreference=2" in str(
        reg.read_value(r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences", "DirectXUserGlobalSettings", "")
    ),
    "disable_opengl_vsync": lambda: "VsyncOff=1" in str(
        reg.read_value(r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences", "DirectXUserGlobalSettings", "")
    ),
    "nvidia_max_prerendered_frames": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler", "EnablePreemption", True,
    ),
    "vulkan_validation_layers": lambda: _reg_bool(
        r"HKCU\Software\Khronos\Vulkan\Loader", "EnableLayerValidation", True,
    ),

    # Network
    "set_dns_cloudflare": lambda: _dns_is(["1.1.1.1", "1.0.0.1"]),
    "set_dns_google": lambda: _dns_is(["8.8.8.8", "8.8.4.4"]),
    "disable_nagle": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TCPNoDelay", 1,
    ),
    "network_throttling_disable": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
        "NetworkThrottlingIndex", 0xFFFFFFFF,
    ),
    "disable_tcp_autotuning": lambda: _tcp_autotuning_disabled(),

    # Privacy
    "disable_telemetry": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0,
    ) and _service_disabled("DiagTrack"),
    "disable_advertising_id": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", False,
    ),
    "disable_cortana": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", 0,
    ),
    "disable_location": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
        "Value", "Deny",
    ),
    "disable_feedback": lambda: _reg_eq(
        r"HKCU\Software\Microsoft\Siuf\Rules", "NumberOfSIUFInPeriod", 0,
    ),
    "disable_tailored_experiences": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Privacy",
        "TailoredExperiencesWithDiagnosticDataEnabled", False,
    ),
    "disable_app_tracking": lambda: _reg_eq(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Privacy", "LetAppsAccessAccountInfo", 0,
    ),

    # Visual
    "disable_animations": lambda: _reg_eq(r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", "0"),
    "disable_transparency": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", False,
    ),
    "disable_shadows": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ListviewShadow", False,
    ),
    "menu_show_delay_zero": lambda: _reg_eq(r"HKCU\Control Panel\Desktop", "MenuShowDelay", "0"),
    "compact_explorer": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "UseCompactMode", True,
    ),

    # System
    "high_performance_power": lambda: _power_plan_active("8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"),
    "ultimate_performance_power": lambda: _power_plan_active("e9a42b02-d5df-448d-aa00-03f14749eb61"),
    "disable_fast_startup": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", False,
    ),
    "pause_windows_update": lambda: reg.key_exists(
        r"HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
    ) and _reg_bool(r"HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings", "PauseFeatureUpdatesStartTime", True),
    "small_taskbar_icons": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarSmallIcons", True,
    ),
    "hide_taskbar_search": lambda: _reg_eq(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "SearchboxTaskbarMode", 0,
    ),
    "intel_panel_refresh_off": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000",
        "EnablePSR", False,
    ),
    "enable_hpet": lambda: _bcd_has("useplatformclock", "true"),
    "disable_hpet": lambda: not _bcd_has("useplatformclock", "true"),

    # Extended (WinUtil / Winhance / DLCI)
    "disable_game_bar_presence": lambda: _reg_bool(r"HKCU\Software\Microsoft\GameBar", "ShowStartupPanel", False),
    "enable_end_task_rightclick": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarEndTask", True,
    ),
    "mmcss_audio_priority": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Audio", "Priority", 6,
    ),
    "system_responsiveness_games": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "SystemResponsiveness", 0,
    ),
    "disable_widgets_board": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarDa", False,
    ),
    "disable_copilot": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCopilotButton", False,
    ),
    "disable_sticky_keys": lambda: _reg_eq(
        r"HKCU\Control Panel\Accessibility\StickyKeys", "Flags", "506",
    ),
    "disable_tips_suggestions": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SoftLandingEnabled", False,
    ),
    "disable_delivery_optimization": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization", "DODownloadMode", 0,
    ),
    "disable_paging_executive": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive", True,
    ),
    "large_system_cache_off": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", False,
    ),
    "disable_throttling_idle": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", True,
    ),
    "disable_wifi_sense": lambda: _reg_bool(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\NetworkConnectivityStatusIndicator", "DisablePassivePolling", True,
    ),
    "disable_activity_history": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", 0,
    ),
    "disable_ink_suggestions": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\InputPersonalization", "RestrictImplicitInkCollection", True,
    ),
    "disable_store_suggestions": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-310093Enabled", False,
    ),
    "disable_edge_telemetry": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\Microsoft\Edge", "MetricsReportingEnabled", 0,
    ),
    "disable_defender_samples": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Spynet", "SpynetReporting", 0,
    ),
    "disable_network_location": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Network Connections", "NC_LocationAwareness", 0,
    ),
    "enable_dark_mode": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", False,
    ),
    "disable_bing_search": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", False,
    ),
    "show_hidden_files": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", True,
    ),

    # Optimize #Expl01t
    "keyboard_data_queue_size": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters", "KeyboardDataQueueSize", 50,
    ),
    "mouse_data_queue_size": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters", "MouseDataQueueSize", 20,
    ),
    "usb_thread_priority": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Services\USBHUB3\Parameters", "ThreadPriority", 15,
    ),
    "show_seconds_in_clock": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowSecondsInSystemClock", True,
    ),
    "enable_numlock_on_boot": lambda: _reg_eq(
        r"HKCU\Control Panel\Keyboard", "InitialKeyboardIndicators", "2",
    ),
    "disable_search_suggestions": lambda: _reg_bool(
        r"HKCU\Software\Policies\Microsoft\Windows\Explorer", "DisableSearchBoxSuggestions", True,
    ),
    "disable_autoplay": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers", "DisableAutoplay", True,
    ),
    "accelerate_startup_delay": lambda: _reg_eq(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize", "StartupDelayInMSec", 0,
    ),
    "fast_app_shutdown": lambda: _reg_eq(r"HKCU\Control Panel\Desktop", "AutoEndTasks", "1"),
    "ntfs_last_access_off": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsDisableLastAccessUpdate", True,
    ),
    "ntfs_8dot3_off": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsDisable8dot3NameCreation", True,
    ),
    "ntfs_memory_ssd": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsMemoryUsage", 0,
    ),
    "hdd_storage_optimize": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsMemoryUsage", 2,
    ),
    "disable_low_disk_warnings": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoLowDiskSpaceChecks", True,
    ),
    "nvme_fast_boot": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Policies\Microsoft\FeatureManagement\Overrides", "735209102", 1,
    ),
    "large_system_cache_on": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", True,
    ),
    "nvidia_disable_preemption": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "DisablePreemption", True,
    ),
    "disable_pc_experiments": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\System", "AllowExperimentation", 0,
    ),
    "disable_voice_activation": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps",
        "AgentActivationEnabled", False,
    ),
    "disable_dynamic_tick": lambda: _bcd_has("disabledynamictick", "yes"),

    # Open source (WinUtil / Sophia / Winhance)
    "disable_storage_sense": lambda: _reg_eq(
        r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01", 0,
    ),
    "disable_consumer_features": lambda: _reg_bool(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent", "DisableWindowsConsumerFeatures", True,
    ),
    "disable_folder_type_discovery": lambda: _reg_eq(
        r"HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags\AllFolders\Shell",
        "FolderType", "NotSpecified",
    ),
    "disable_start_recommendations": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Start_IrisRecommendations", False,
    ),
    "disable_filter_keys": lambda: _reg_eq(
        r"HKCU\Control Panel\Accessibility\Keyboard Response", "Flags", "122",
    ),
    "disable_error_reporting": lambda: _service_disabled("WerSvc"),
    "enable_long_paths": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "LongPathsEnabled", True,
    ),
    "disable_scrollbar_autohide": lambda: _reg_bool(
        r"HKCU\Control Panel\Accessibility", "DynamicScrollbars", False,
    ),
    "disable_wpbt": lambda: _reg_bool(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager", "DisableWpbtExecution", True,
    ),
    "disable_windows_ai_registry": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Policies\WindowsNotepad", "DisableAIFeatures", 1,
    ),
    "show_file_extensions": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", False,
    ),
    "disable_task_view_button": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowTaskViewButton", False,
    ),
    "disable_acrylic_logon": lambda: _reg_bool(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "DisableAcrylicBackgroundOnLogon", True,
    ),
    "exclude_wu_drivers": lambda: _reg_bool(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate", "ExcludeWUDriversInQualityUpdate", True,
    ),
    "mmcss_global_responsiveness": lambda: _reg_eq(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", 0,
    ),
    "disable_meet_now": lambda: _reg_bool(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "HideSCAMeetNow", True,
    ),
    "disable_s0_sleep_network": lambda: _reg_eq(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\F15576E8-98B7-4186-B944-EAFA664402D9",
        "Attributes", 0,
    ),
}


def _dns_is(servers: list[str]) -> bool:
    code, out, _ = run_powershell(
        "Get-DnsClientServerAddress -AddressFamily IPv4 | "
        "Where-Object { $_.ServerAddresses } | "
        "Select-Object -ExpandProperty ServerAddresses"
    )
    if code != 0 or not out:
        return False
    active = [s.strip() for s in out.replace("\n", " ").split() if s.strip()]
    return all(s in active for s in servers[:1])


def _tcp_autotuning_disabled() -> bool:
    code, out, _ = run_command(["netsh", "interface", "tcp", "show", "global"])
    return code == 0 and "disabled" in out.lower()


def _bcd_has(key: str, value: str) -> bool:
    code, out, _ = run_command(["bcdedit", "/enum", "{current}"])
    return code == 0 and key in out.lower() and value in out.lower()


class TweakStateDetector:
    """Определяет состояние твиков в системе и в истории приложения."""

    def __init__(self, applied_by_app: Optional[set[str]] = None) -> None:
        self._applied_by_app = applied_by_app or set()
        self._cache: dict[tuple[str, bool], TweakStateInfo] = {}

    def set_applied_by_app(self, tweak_ids: set[str]) -> None:
        self._applied_by_app = tweak_ids
        self._cache.clear()

    def check_system(self, tweak_id: str) -> bool:
        """Проверяет, достигнуто ли желаемое состояние в Windows."""
        if tweak_id in ONE_SHOT_TWEAKS:
            return False
        checker = SYSTEM_CHECKS.get(tweak_id)
        if not checker:
            return False
        try:
            return checker()
        except Exception:
            return False

    def get_state(self, tweak_id: str, *, compatible: bool = True) -> TweakStateInfo:
        """Возвращает полное состояние твика."""
        cache_key = (tweak_id, compatible)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not compatible:
            info = TweakStateInfo(
                tweak_id=tweak_id,
                status=TweakStatus.INCOMPATIBLE,
                is_active=False,
                can_apply=False,
                applied_by_app=False,
                active_in_system=False,
            )
            self._cache[cache_key] = info
            return info

        if tweak_id in ONE_SHOT_TWEAKS:
            info = TweakStateInfo(
                tweak_id=tweak_id,
                status=TweakStatus.ONE_SHOT,
                is_active=False,
                can_apply=True,
                applied_by_app=False,
                active_in_system=False,
                detail="",
            )
            self._cache[cache_key] = info
            return info

        applied_app = tweak_id in self._applied_by_app
        active_sys = self.check_system(tweak_id)
        checker_exists = tweak_id in SYSTEM_CHECKS

        if applied_app and active_sys:
            status = TweakStatus.ACTIVE_BOTH
        elif active_sys:
            status = TweakStatus.ACTIVE_SYSTEM
        elif applied_app:
            status = TweakStatus.APPLIED_APP
        elif not checker_exists:
            status = TweakStatus.UNKNOWN
        else:
            status = TweakStatus.INACTIVE

        is_active = active_sys or (applied_app and not checker_exists)
        can_apply = not is_active or status == TweakStatus.APPLIED_APP and not active_sys

        # Блокируем повторное применение если уже активно в системе
        if active_sys:
            can_apply = False

        info = TweakStateInfo(
            tweak_id=tweak_id,
            status=status,
            is_active=is_active or active_sys,
            can_apply=can_apply,
            applied_by_app=applied_app,
            active_in_system=active_sys,
            detail="",
        )
        self._cache[(tweak_id, True)] = info
        return info

    def get_all_states(self, tweak_ids: list[str], compatible_map: dict[str, bool]) -> dict[str, TweakStateInfo]:
        return {tid: self.get_state(tid, compatible=compatible_map.get(tid, True)) for tid in tweak_ids}

    def filter_applicable(self, tweak_ids: list[str], compatible_map: dict[str, bool]) -> tuple[list[str], list[str]]:
        """Разделяет твики на применимые и уже активные."""
        from utils.tweak_ids import dedupe_preserve_order

        applicable, skipped = [], []
        for tid in dedupe_preserve_order(tweak_ids):
            compatible = compatible_map.get(tid, True)
            state = self.get_state(tid, compatible=compatible)
            if state.status == TweakStatus.INCOMPATIBLE:
                skipped.append(tid)
                continue
            if state.can_apply and not state.is_active:
                applicable.append(tid)
            elif state.is_active or not state.can_apply:
                if state.status != TweakStatus.ONE_SHOT:
                    skipped.append(tid)
                else:
                    applicable.append(tid)
            else:
                applicable.append(tid)
        return applicable, skipped

    def scan_all(self, tweak_ids: list[str], compatible_map: dict[str, bool] | None = None) -> None:
        """Полное сканирование — вызывать только из фонового потока."""
        compat = compatible_map or {tid: True for tid in tweak_ids}
        for tid in tweak_ids:
            self.get_state(tid, compatible=compat.get(tid, True))

    def invalidate(self, tweak_ids: Iterable[str] | None = None) -> None:
        """Сбрасывает кэш для указанных твиков или полностью."""
        if tweak_ids is None:
            self._cache.clear()
        else:
            drop = set(tweak_ids)
            for key in list(self._cache):
                if key[0] in drop:
                    del self._cache[key]

    def clear_cache(self) -> None:
        """Совместимость — полный сброс кэша."""
        self.invalidate()

    def count_active(self, tweak_ids: list[str], compatible_map: dict[str, bool]) -> dict[str, int]:
        """Считает твики по статусам."""
        counts = {"active": 0, "inactive": 0, "one_shot": 0, "unknown": 0}
        for tid in tweak_ids:
            s = self.get_state(tid, compatible=compatible_map.get(tid, True))
            if s.status == TweakStatus.ONE_SHOT:
                counts["one_shot"] += 1
            elif s.is_active:
                counts["active"] += 1
            elif s.status == TweakStatus.UNKNOWN:
                counts["unknown"] += 1
            else:
                counts["inactive"] += 1
        return counts
