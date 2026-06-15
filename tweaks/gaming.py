"""Игровые твики."""

from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak, services_batch_apply, services_batch_revert


def enable_game_mode_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", 1, 0),
        (r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", 1, 0),
    ], message="Game Mode включён")


def enable_game_mode_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_game_mode_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", 0, 1),
        (r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", 0, 1),
    ], message="Game Mode отключён")


def disable_game_mode_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def enable_hags_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
        "HwSchMode", 2, 1, enabled=True,
    )


def enable_hags_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_hags_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
        "HwSchMode", 1, 2, enabled=True,
    )


def disable_hags_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_game_dvr_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\System\GameConfigStore", "GameDVR_Enabled", 0, 1),
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0, 1),
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", 0, 1),
    ], message="Xbox Game DVR отключён")


def disable_game_dvr_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_fullscreen_optimizations_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2, 0),
        (r"HKCU\System\GameConfigStore", "GameDVR_FSEBehavior", 2, 0),
    ], message="Fullscreen Optimizations отключены")


def disable_fullscreen_optimizations_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_mouse_acceleration_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Control Panel\Mouse", "MouseSpeed", "0", "1", winreg.REG_SZ),
        (r"HKCU\Control Panel\Mouse", "MouseThreshold1", "0", "6", winreg.REG_SZ),
        (r"HKCU\Control Panel\Mouse", "MouseThreshold2", "0", "10", winreg.REG_SZ),
    ], message="Ускорение мыши отключено")


def disable_mouse_acceleration_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def mmcss_games_priority_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
        "GPU Priority", 8, 8, enabled=True,
    )


def mmcss_games_priority_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_xbox_services_apply() -> TweakResult:
    return services_batch_apply(
        ["XblAuthManager", "XblGameSave", "XboxGipSvc", "XboxNetApiSvc"],
        disabled=True,
        message="Xbox службы отключены",
    )


def disable_xbox_services_revert(data) -> TweakResult:
    return services_batch_revert(data)


HANDLERS = {
    "enable_game_mode": (enable_game_mode_apply, enable_game_mode_revert),
    "disable_game_mode": (disable_game_mode_apply, disable_game_mode_revert),
    "enable_hags": (enable_hags_apply, enable_hags_revert),
    "disable_hags": (disable_hags_apply, disable_hags_revert),
    "disable_game_dvr": (disable_game_dvr_apply, disable_game_dvr_revert),
    "disable_fullscreen_optimizations": (disable_fullscreen_optimizations_apply, disable_fullscreen_optimizations_revert),
    "disable_mouse_acceleration": (disable_mouse_acceleration_apply, disable_mouse_acceleration_revert),
    "mmcss_games_priority": (mmcss_games_priority_apply, mmcss_games_priority_revert),
    "disable_xbox_services": (disable_xbox_services_apply, disable_xbox_services_revert),
}
