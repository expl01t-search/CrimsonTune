"""Твики DirectX."""

from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_revert, reg_tweak
from utils.subprocess_helper import run_command


def enable_shader_cache_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
        "DpiMapIommuContiguous", 1, 0, enabled=True,
    )


def enable_shader_cache_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_dxgi_flip_model_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences",
        "DirectXUserGlobalSettings", "SwapEffectUpgradeEnable=0;", "",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def disable_dxgi_flip_model_revert(data) -> TweakResult:
    return reg_revert(data)


def clear_shader_cache_apply() -> TweakResult:
    import os
    import shutil
    from pathlib import Path

    paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "D3DSCache",
        Path(os.environ.get("LOCALAPPDATA", "")) / "NVIDIA" / "DXCache",
        Path(os.environ.get("LOCALAPPDATA", "")) / "AMD" / "DxCache",
    ]
    cleared = 0
    for p in paths:
        if p.exists():
            try:
                shutil.rmtree(p, ignore_errors=True)
                cleared += 1
            except OSError:
                pass
    return TweakResult(True, f"Очищено кэшей: {cleared}", revert_data=None)


def clear_shader_cache_revert(_data) -> TweakResult:
    return TweakResult(True, "Очистка кэша необратима")


def export_dxdiag_apply() -> TweakResult:
    import os
    from pathlib import Path

    out = Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "dxdiag_winTweaker.txt"
    code, _, err = run_command(["dxdiag", "/t", str(out)])
    if code == 0:
        return TweakResult(True, f"DxDiag сохранён: {out}")
    return TweakResult(False, err)


def export_dxdiag_revert(_data) -> TweakResult:
    return TweakResult(True, "Экспорт необратим")


def directx_12_ultimate_hint_apply() -> TweakResult:
    return TweakResult(True, "DirectX 12 Ultimate активируется драйвером GPU — обновите драйвер")


def directx_12_ultimate_hint_revert(_data) -> TweakResult:
    return TweakResult(True, "Нет изменений")


HANDLERS = {
    "enable_shader_cache": (enable_shader_cache_apply, enable_shader_cache_revert),
    "disable_dxgi_flip_model": (disable_dxgi_flip_model_apply, disable_dxgi_flip_model_revert),
    "clear_shader_cache": (clear_shader_cache_apply, clear_shader_cache_revert),
    "export_dxdiag": (export_dxdiag_apply, export_dxdiag_revert),
    "directx_12_ultimate_hint": (directx_12_ultimate_hint_apply, directx_12_ultimate_hint_revert),
}
