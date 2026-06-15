
from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_revert, reg_tweak


def force_discrete_gpu_opengl_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences",
        "DirectXUserGlobalSettings",
        "GpuPreference=2;",
        "",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def force_discrete_gpu_opengl_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_opengl_vsync_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences",
        "DirectXUserGlobalSettings",
        "VsyncOff=1;",
        "",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def disable_opengl_vsync_revert(data) -> TweakResult:
    return reg_revert(data)


def vulkan_validation_layers_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Khronos\Vulkan\Loader",
        "EnableLayerValidation", 1, 0, enabled=True,
    )


def vulkan_validation_layers_revert(data) -> TweakResult:
    return reg_revert(data)


HANDLERS = {
    "force_discrete_gpu_opengl": (force_discrete_gpu_opengl_apply, force_discrete_gpu_opengl_revert),
    "disable_opengl_vsync": (disable_opengl_vsync_apply, disable_opengl_vsync_revert),
    "vulkan_validation_layers": (vulkan_validation_layers_apply, vulkan_validation_layers_revert),
}
