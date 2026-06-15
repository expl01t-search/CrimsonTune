
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_tweaks_json_has_50_plus_entries():
    config_path = ROOT / "config" / "tweaks.json"
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["tweaks"]) >= 125


def test_all_profiles_exist():
    profiles_dir = ROOT / "config" / "profiles"
    expected = {"gamer_pro.json", "max_performance.json", "privacy.json", "balanced.json"}
    actual = {p.name for p in profiles_dir.glob("*.json")}
    assert expected.issubset(actual)


def test_manager_loads_config():
    from tweaks import create_manager

    manager = create_manager()
    metas = manager.get_all_meta()
    assert len(metas) >= 125
    assert len(manager._tweaks) >= 125


def test_search_tweaks():
    from tweaks import create_manager

    manager = create_manager()
    results = manager.search("game")
    assert len(results) > 0
    assert any("game" in r.id.lower() or "game" in r.name.lower() for r in results)


def test_handlers_match_all_tweaks():
    from tweaks import create_manager

    manager = create_manager()
    ids = {m.id for m in manager.get_all_meta()}
    handlers = set(manager._handlers.keys())
    assert ids == handlers, f"missing handlers: {ids - handlers}, orphan: {handlers - ids}"


def test_tweak_meta_fields():
    from tweaks import create_manager
    from utils.categories import TWEAK_CATEGORY_KEYS

    manager = create_manager()
    allowed = set(TWEAK_CATEGORY_KEYS)
    for meta in manager.get_all_meta():
        assert meta.id
        assert meta.name
        assert meta.description
        assert meta.category in allowed
        assert meta.risk in {"safe", "medium", "high"}
