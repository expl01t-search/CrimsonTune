
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_state_detector_inactive():
    from core.tweak_state import TweakStateDetector, TweakStatus

    det = TweakStateDetector()
    state = det.get_state("nonexistent_tweak_xyz", compatible=True)
    assert state.status in (TweakStatus.UNKNOWN, TweakStatus.INACTIVE)


def test_state_detector_one_shot():
    from core.tweak_state import TweakStateDetector, TweakStatus

    det = TweakStateDetector()
    state = det.get_state("flush_dns", compatible=True)
    assert state.status == TweakStatus.ONE_SHOT
    assert state.can_apply is True


def test_filter_applicable():
    from core.tweak_state import TweakStateDetector

    det = TweakStateDetector()

    def fake_check():
        return True

    from core import tweak_state
    tweak_state.SYSTEM_CHECKS["_test_active"] = fake_check

    try:
        applicable, skipped = det.filter_applicable(
            ["_test_active", "flush_dns"],
            {"_test_active": True, "flush_dns": True},
        )
        assert "_test_active" in skipped
        assert "flush_dns" in applicable
    finally:
        tweak_state.SYSTEM_CHECKS.pop("_test_active", None)


def test_manager_has_state_detector():
    from tweaks import create_manager

    manager = create_manager()
    assert manager.state_detector is not None
    state = manager.get_tweak_state("enable_game_mode")
    assert state.tweak_id == "enable_game_mode"


def test_system_checks_coverage():
    from core.tweak_state import ONE_SHOT_TWEAKS, SYSTEM_CHECKS
    from tweaks import create_manager

    manager = create_manager()
    all_ids = {m.id for m in manager.get_all_meta()}
    covered = set(SYSTEM_CHECKS.keys()) | ONE_SHOT_TWEAKS
    missing = all_ids - covered
    assert len(missing) <= 15, f"Твики без проверки состояния: {missing}"
