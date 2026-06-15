"""Визуальные твики Windows."""

from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak
from utils.subprocess_helper import run_command


def disable_animations_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", "0", "1", winreg.REG_SZ),
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2, 0),
        (
            r"HKCU\Control Panel\Desktop",
            "UserPreferencesMask",
            bytes([0x90, 0x12, 0x03, 0x80, 0x10, 0x00, 0x00, 0x00]),
            bytes([0x9E, 0x1E, 0x07, 0x80, 0x12, 0x00, 0x00, 0x00]),
            winreg.REG_BINARY,
        ),
    ], message="Анимации отключены")


def disable_animations_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_transparency_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        "EnableTransparency", 0, 1, enabled=True,
    )


def disable_transparency_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_shadows_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "ListviewShadow", 0, 1, enabled=True,
    )


def disable_shadows_revert(data) -> TweakResult:
    return reg_revert(data)


def menu_show_delay_zero_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Control Panel\Desktop",
        "MenuShowDelay", "0", "400",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def menu_show_delay_zero_revert(data) -> TweakResult:
    return reg_revert(data)


def compact_explorer_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "UseCompactMode", 1, 0, enabled=True,
    )


def compact_explorer_revert(data) -> TweakResult:
    return reg_revert(data)


HANDLERS = {
    "disable_animations": (disable_animations_apply, disable_animations_revert),
    "disable_transparency": (disable_transparency_apply, disable_transparency_revert),
    "disable_shadows": (disable_shadows_apply, disable_shadows_revert),
    "menu_show_delay_zero": (menu_show_delay_zero_apply, menu_show_delay_zero_revert),
    "compact_explorer": (compact_explorer_apply, compact_explorer_revert),
}
