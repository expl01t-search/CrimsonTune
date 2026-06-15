from __future__ import annotations

RAM_SVCHOST_TIERS_GB: tuple[int, ...] = (2, 4, 6, 8, 12, 16, 32, 64)

RAM_SVCHOST_THRESHOLD_KB: dict[int, int] = {
    2: 2_097_152,
    4: 4_194_304,
    6: 6_291_456,
    8: 8_388_608,
    12: 12_582_912,
    16: 16_777_216,
    32: 33_554_432,
    64: 67_108_864,
}

RAM_SVCHOST_DEFAULT_KB = 380_000

_SVCHOST_REG = r"HKLM\SYSTEM\CurrentControlSet\Control"
_SVCHOST_VALUE = "SvcHostSplitThresholdInKB"


def match_ram_tier(ram_total_gb: float) -> int:
    gb = max(1.0, round(ram_total_gb))
    return min(RAM_SVCHOST_TIERS_GB, key=lambda tier: abs(tier - gb))


def ram_svchost_tweak_id(tier_gb: int) -> str:
    return f"ram_svchost_{tier_gb}gb"


def is_ram_tier_compatible(meta_tier_gb: int | None, ram_total_gb: float) -> bool:
    if meta_tier_gb is None:
        return True
    return meta_tier_gb == match_ram_tier(ram_total_gb)
