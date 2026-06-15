
from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak
from tweaks.supplemental_catalog import SUPPLEMENTAL_TWEAKS, build_reg_handlers
from utils.gpu_reg import gpu_adapter_paths
from utils.subprocess_helper import run_command


def enable_shader_cache_apply() -> TweakResult:
    entries = [(path, "EnableShaderCache", 1, 0) for path in gpu_adapter_paths()]
    return reg_batch_apply(entries, message="Shader Cache включён на GPU")


def enable_shader_cache_revert(data) -> TweakResult:
    return reg_batch_revert(data)


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

    out = Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "dxdiag_crimson.txt"
    code, _, err = run_command(["dxdiag", "/t", str(out)])
    if code == 0:
        return TweakResult(True, f"DxDiag сохранён: {out}")
    return TweakResult(False, err)


def export_dxdiag_revert(_data) -> TweakResult:
    return TweakResult(True, "Экспорт необратим")


_dx_ids = {t.id for t in SUPPLEMENTAL_TWEAKS if t.category == "directx"}

HANDLERS = {
    "enable_shader_cache": (enable_shader_cache_apply, enable_shader_cache_revert),
    "disable_dxgi_flip_model": (disable_dxgi_flip_model_apply, disable_dxgi_flip_model_revert),
    "clear_shader_cache": (clear_shader_cache_apply, clear_shader_cache_revert),
    "export_dxdiag": (export_dxdiag_apply, export_dxdiag_revert),
}
HANDLERS.update(build_reg_handlers([t for t in SUPPLEMENTAL_TWEAKS if t.id in _dx_ids]))
