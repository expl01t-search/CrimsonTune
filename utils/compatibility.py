"""Проверка совместимости твиков с системой."""

from __future__ import annotations

from core.i18n import t
from tweaks.base import TweakMeta

_GPU_LABELS = {
    "nvidia": "NVIDIA",
    "amd": "AMD",
    "intel": "Intel",
}


def is_tweak_compatible(meta: TweakMeta, *, os_build: str, gpu_vendor: str) -> bool:
    """Проверяет совместимость твика с ОС и GPU."""
    if meta.compatible_os:
        build = f"10.0.{os_build}" if os_build and not os_build.startswith("10.") else os_build
        if not any(build.startswith(v) for v in meta.compatible_os):
            return False
    vendors = meta.gpu_vendor
    if vendors and "all" not in vendors:
        if gpu_vendor not in vendors:
            return False
    return True


def incompatible_detail(meta: TweakMeta, gpu_vendor: str) -> str:
    """Текст для бейджа несовместимого твика."""
    vendors = meta.gpu_vendor or ["all"]
    if "all" in vendors:
        return t("incompatible_system")
    required = [_GPU_LABELS.get(v, v.upper()) for v in vendors]
    current = _GPU_LABELS.get(gpu_vendor, t("gpu_unknown_short"))
    return t("incompatible_gpu", required=", ".join(required), current=current)
