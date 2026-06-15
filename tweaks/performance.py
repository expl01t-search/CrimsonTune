"""Твики производительности."""

from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_revert, reg_tweak, service_revert, service_tweak
from utils.subprocess_helper import run_command, run_powershell


def disable_sysmain_apply() -> TweakResult:
    return service_tweak("SysMain", disabled=True)


def disable_sysmain_revert(data) -> TweakResult:
    return service_revert(data)


def disable_search_indexing_apply() -> TweakResult:
    return service_tweak("WSearch", disabled=True)


def disable_search_indexing_revert(data) -> TweakResult:
    return service_revert(data)


def disable_prefetch_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
        "EnablePrefetcher", 0, 3, enabled=True,
    )


def disable_prefetch_revert(data) -> TweakResult:
    return reg_revert(data)


def high_timer_resolution_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel",
        "GlobalTimerResolutionRequests", 1, 0, enabled=True,
    )


def high_timer_resolution_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_background_apps_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
        "GlobalUserDisabled", 1, 0, enabled=True,
    )


def disable_background_apps_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_hibernation_apply() -> TweakResult:
    code, out, err = run_command(["powercfg", "/hibernate", "off"])
    if code == 0:
        return TweakResult(True, "Гибернация отключена", revert_data={"cmd": "on"})
    return TweakResult(False, err or out)


def disable_hibernation_revert(data) -> TweakResult:
    cmd = data.get("cmd", "on") if data else "on"
    code, out, err = run_command(["powercfg", "/hibernate", cmd])
    return TweakResult(code == 0, out or err)


def optimize_svchost_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control",
        "SvcHostSplitThresholdInKB", 380000, 2097152, enabled=True,
    )


def optimize_svchost_revert(data) -> TweakResult:
    return reg_revert(data)


def clear_temp_apply() -> TweakResult:
    script = (
        "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; "
        "Remove-Item -Path C:\\Windows\\Temp\\* -Recurse -Force -ErrorAction SilentlyContinue"
    )
    code, out, err = run_powershell(script)
    return TweakResult(code == 0, "Временные файлы очищены" if code == 0 else err)


def clear_temp_revert(_data) -> TweakResult:
    return TweakResult(True, "Очистка temp необратима")


HANDLERS = {
    "disable_sysmain": (disable_sysmain_apply, disable_sysmain_revert),
    "disable_search_indexing": (disable_search_indexing_apply, disable_search_indexing_revert),
    "disable_prefetch": (disable_prefetch_apply, disable_prefetch_revert),
    "high_timer_resolution": (high_timer_resolution_apply, high_timer_resolution_revert),
    "disable_background_apps": (disable_background_apps_apply, disable_background_apps_revert),
    "disable_hibernation": (disable_hibernation_apply, disable_hibernation_revert),
    "optimize_svchost": (optimize_svchost_apply, optimize_svchost_revert),
    "clear_temp_files": (clear_temp_apply, clear_temp_revert),
}
