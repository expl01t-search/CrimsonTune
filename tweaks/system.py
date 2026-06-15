
from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import power_plan_tweak, reg_revert, reg_tweak
from utils.subprocess_helper import run_command, run_powershell


HIGH_PERFORMANCE_GUID = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
ULTIMATE_PERFORMANCE_GUID = "e9a42b02-d5df-448d-aa00-03f14749eb61"


def high_performance_power_apply() -> TweakResult:
    run_command(["powercfg", "-duplicatescheme", ULTIMATE_PERFORMANCE_GUID])
    return power_plan_tweak(HIGH_PERFORMANCE_GUID)


def high_performance_power_revert(_data) -> TweakResult:
    balanced = "381b4222-f694-41f0-9685-ff5bb260df2e"
    return power_plan_tweak(balanced)


def ultimate_performance_power_apply() -> TweakResult:
    run_command(["powercfg", "-duplicatescheme", ULTIMATE_PERFORMANCE_GUID])
    return power_plan_tweak(ULTIMATE_PERFORMANCE_GUID)


def ultimate_performance_power_revert(_data) -> TweakResult:
    return high_performance_power_revert(_data)


def disable_fast_startup_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power",
        "HiberbootEnabled", 0, 1, enabled=True,
    )


def disable_fast_startup_revert(data) -> TweakResult:
    return reg_revert(data)


def pause_windows_update_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings",
        "PauseFeatureUpdatesStartTime", 1, 0, enabled=True,
    )


def pause_windows_update_revert(data) -> TweakResult:
    return reg_revert(data)


def small_taskbar_icons_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "TaskbarSmallIcons", 1, 0, enabled=True,
    )


def small_taskbar_icons_revert(data) -> TweakResult:
    return reg_revert(data)


def hide_taskbar_search_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search",
        "SearchboxTaskbarMode", 0, 1, enabled=True,
    )


def hide_taskbar_search_revert(data) -> TweakResult:
    return reg_revert(data)


def intel_panel_refresh_off_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000",
        "EnablePSR", 0, 1, enabled=True,
    )


def intel_panel_refresh_off_revert(data) -> TweakResult:
    return reg_revert(data)


def enable_hpet_apply() -> TweakResult:
    code, out, err = run_command(["bcdedit", "/set", "useplatformclock", "true"])
    return TweakResult(code == 0, "HPET включён. Перезагрузка может потребоваться." if code == 0 else err)


def enable_hpet_revert(_data) -> TweakResult:
    code, out, err = run_command(["bcdedit", "/deletevalue", "useplatformclock"])
    return TweakResult(code == 0, out or err)


def disable_hpet_apply() -> TweakResult:
    code, out, err = run_command(["bcdedit", "/deletevalue", "useplatformclock"])
    return TweakResult(code == 0, "HPET отключён" if code == 0 else err)


def disable_hpet_revert(_data) -> TweakResult:
    return enable_hpet_apply()


HANDLERS = {
    "high_performance_power": (high_performance_power_apply, high_performance_power_revert),
    "ultimate_performance_power": (ultimate_performance_power_apply, ultimate_performance_power_revert),
    "disable_fast_startup": (disable_fast_startup_apply, disable_fast_startup_revert),
    "pause_windows_update": (pause_windows_update_apply, pause_windows_update_revert),
    "small_taskbar_icons": (small_taskbar_icons_apply, small_taskbar_icons_revert),
    "hide_taskbar_search": (hide_taskbar_search_apply, hide_taskbar_search_revert),
    "intel_panel_refresh_off": (intel_panel_refresh_off_apply, intel_panel_refresh_off_revert),
    "enable_hpet": (enable_hpet_apply, enable_hpet_revert),
    "disable_hpet": (disable_hpet_apply, disable_hpet_revert),
}
