
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_dedupe_preserve_order():
    from utils.tweak_ids import dedupe_preserve_order

    assert dedupe_preserve_order(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]


def test_gpu_compatibility_nvidia_only():
    from core.i18n import init_locale
    from tweaks.base import TweakMeta
    from utils.compatibility import incompatible_detail, is_tweak_compatible

    init_locale("ru")
    meta = TweakMeta(
        id="gpu_test",
        name="NVIDIA only",
        description="",
        category="gaming",
        gpu_vendor=["nvidia"],
    )
    assert is_tweak_compatible(meta, os_build="19044", gpu_vendor="nvidia") is True
    assert is_tweak_compatible(meta, os_build="19044", gpu_vendor="amd") is False
    detail = incompatible_detail(meta, "amd")
    assert "NVIDIA" in detail
    assert "AMD" in detail


def test_incompatible_state_not_cached_as_inactive():
    from core.tweak_state import TweakStateDetector, TweakStatus

    det = TweakStateDetector()
    s1 = det.get_state("amd_anti_lag", compatible=True)
    assert s1.status != TweakStatus.INCOMPATIBLE

    s2 = det.get_state("amd_anti_lag", compatible=False)
    assert s2.status == TweakStatus.INCOMPATIBLE
    assert s2.can_apply is False


def test_filter_applicable_dedupes_input():
    from core.tweak_state import TweakStateDetector

    det = TweakStateDetector()
    applicable, skipped = det.filter_applicable(
        ["flush_dns", "flush_dns", "flush_dns"],
        {"flush_dns": True},
    )
    assert applicable == ["flush_dns"]
    assert skipped == []


def test_manager_resolve_tweak_names_dedupes():
    from tweaks import create_manager

    manager = create_manager()
    meta = manager.get_meta("enable_game_mode")
    assert meta is not None
    names = manager.resolve_tweak_names(["enable_game_mode", "enable_game_mode"])
    assert names == [meta.name]


def test_no_duplicate_tweak_ids_in_config():
    from tweaks import create_manager

    manager = create_manager()
    ids = [m.id for m in manager.get_all_meta()]
    assert len(ids) == len(set(ids))


def test_ram_tier_shows_only_matching_tweak():
    from core.i18n import init_locale
    from tweaks.base import TweakMeta
    from utils.compatibility import is_tweak_compatible, is_tweak_visible
    from utils.ram_tiers import match_ram_tier, ram_svchost_tweak_id

    init_locale("ru")
    ram_total = 16.0
    tier = match_ram_tier(ram_total)
    assert tier == 16

    visible_ids = []
    for gb in (2, 4, 6, 8, 12, 16, 32, 64):
        meta = TweakMeta(
            id=ram_svchost_tweak_id(gb),
            name=f"RAM {gb} GB",
            description="",
            category="performance",
            ram_tier_gb=gb,
        )
        compatible = is_tweak_compatible(meta, os_build="19044", gpu_vendor="nvidia", ram_total_gb=ram_total)
        visible = is_tweak_visible(meta, lambda m: compatible)
        if visible:
            visible_ids.append(meta.id)

    assert visible_ids == [ram_svchost_tweak_id(16)]


def test_ram_tier_match_rounds_to_nearest():
    from utils.ram_tiers import match_ram_tier

    assert match_ram_tier(15.4) == 16
    assert match_ram_tier(11.0) == 12
    assert match_ram_tier(3.6) == 4
