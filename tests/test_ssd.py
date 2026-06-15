
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_manager_has_ssd_tweaks():
    from tweaks import create_manager

    manager = create_manager()
    ids = {m.id for m in manager.get_all_meta()}
    for tid in (
        "ssd_enable_trim",
        "ssd_disable_boot_defrag",
        "ssd_disable_layout_ini",
        "ssd_disable_defrag_service",
        "ssd_disable_system_restore",
        "ssd_disable_scheduled_defrag",
        "ssd_disable_superfetch_prefetch",
        "ssd_disable_volume_indexing",
    ):
        assert tid in ids


def test_ssd_handlers_registered():
    from tweaks.ssd import HANDLERS

    assert len(HANDLERS) == 8
    for tid in HANDLERS:
        apply_fn, revert_fn = HANDLERS[tid]
        assert callable(apply_fn)
        assert callable(revert_fn)


def test_ssd_category_in_performance_nav():
    from utils.categories import nav_categories

    assert "ssd" in nav_categories("performance")
