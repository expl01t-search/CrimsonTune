
from __future__ import annotations

from core.i18n import t
from tweaks.base import TweakMeta
from utils.ram_tiers import is_ram_tier_compatible, match_ram_tier

_GPU_LABELS = {
    "nvidia": "NVIDIA",
    "amd": "AMD",
    "intel": "Intel",
}


def is_tweak_compatible(
    meta: TweakMeta,
    *,
    os_build: str,
    gpu_vendor: str,
    ram_total_gb: float | None = None,
) -> bool:
    if meta.compatible_os:
        build = f"10.0.{os_build}" if os_build and not os_build.startswith("10.") else os_build
        if not any(build.startswith(v) for v in meta.compatible_os):
            if not (build.startswith("10.0.") and "10.0" in meta.compatible_os):
                return False
    vendors = meta.gpu_vendor
    if vendors and "all" not in vendors:
        if gpu_vendor not in vendors:
            return False
    if meta.ram_tier_gb is not None:
        if ram_total_gb is None:
            return False
        if not is_ram_tier_compatible(meta.ram_tier_gb, ram_total_gb):
            return False
    return True


def incompatible_detail(
    meta: TweakMeta,
    gpu_vendor: str,
    *,
    ram_total_gb: float | None = None,
) -> str:
    if meta.ram_tier_gb is not None and ram_total_gb is not None:
        if not is_ram_tier_compatible(meta.ram_tier_gb, ram_total_gb):
            matched = match_ram_tier(ram_total_gb)
            return t(
                "incompatible_ram",
                installed=f"{ram_total_gb:.1f}",
                tier=matched,
            )
    vendors = meta.gpu_vendor or ["all"]
    if "all" in vendors:
        return t("incompatible_system")
    required = [_GPU_LABELS.get(v, v.upper()) for v in vendors]
    current = _GPU_LABELS.get(gpu_vendor, t("gpu_unknown_short"))
    return t("incompatible_gpu", required=", ".join(required), current=current)


def is_tweak_visible(meta: TweakMeta, is_compatible_fn) -> bool:
    if meta.ram_tier_gb is not None and not is_compatible_fn(meta):
        return False
    return True
