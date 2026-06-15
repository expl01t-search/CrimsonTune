"""Регрессионные тесты polish/QA."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REMOVE_IDS = {
    "disable_pointer_precision_full",
    "disable_transparency_effects",
    "disable_tailored_ads",
    "disable_widgets",
    "disable_news_interests",
    "gpu_priority_games",
    "optimize_network_adapter",
    "enhanced_telemetry_block",
    "disable_diagtrack_service",
    "disable_timeline",
    "disable_superfetch",
    "processor_scheduling_foreground",
    "best_performance_visual",
    "disable_game_bar",
    "disable_fullscreen_optimizations_global",
    "disable_hibernation_fast_startup_combo",
}


def test_profile_ids_valid():
    tweaks_path = ROOT / "config" / "tweaks.json"
    catalog = {t["id"] for t in json.loads(tweaks_path.read_text(encoding="utf-8"))["tweaks"]}
    for pf in (ROOT / "config" / "profiles").glob("*.json"):
        profile = json.loads(pf.read_text(encoding="utf-8"))
        for tid in profile.get("tweaks", []):
            assert tid not in REMOVE_IDS, f"{pf.name} references removed {tid}"
            assert tid in catalog, f"{pf.name} references unknown {tid}"


def test_filter_skips_incompatible():
    from core.tweak_state import TweakStateDetector, TweakStatus

    det = TweakStateDetector()
    applicable, skipped = det.filter_applicable(
        ["amd_anti_lag"],
        {"amd_anti_lag": False},
    )
    assert applicable == []
    assert skipped == ["amd_anti_lag"]
    state = det.get_state("amd_anti_lag", compatible=False)
    assert state.status == TweakStatus.INCOMPATIBLE


def test_resolve_tweak_names_no_dupes():
    from tweaks import create_manager

    manager = create_manager()
    names = manager.resolve_tweak_names(["flush_dns", "flush_dns", "enable_game_mode"])
    assert len(names) == len(set(names))
    assert len(names) == 2


def test_blacklist_not_in_catalog():
    from tweaks import create_manager

    manager = create_manager()
    blacklist_path = ROOT / "config" / "blacklist.json"
    if not blacklist_path.exists():
        return
    blocked = {item["id"] for item in json.loads(blacklist_path.read_text(encoding="utf-8")) if item.get("id")}
    catalog = {m.id for m in manager.get_all_meta()}
    assert not blocked & catalog


def test_one_category_per_tweak():
    tweaks = json.loads((ROOT / "config" / "tweaks.json").read_text(encoding="utf-8"))["tweaks"]
    by_id: dict[str, list[str]] = {}
    for t in tweaks:
        by_id.setdefault(t["id"], []).append(t["category"])
    assert all(len(v) == 1 for v in by_id.values())


def test_incompatible_toggle_blocked():
    from PySide6.QtWidgets import QApplication

    from tweaks import create_manager
    from ui.components.tweak_row import TweakRow
    from utils.tweak_state_ui import build_incompatible_state

    app = QApplication.instance() or QApplication([])
    manager = create_manager()
    meta = manager.get_meta("amd_anti_lag")
    assert meta is not None
    state = build_incompatible_state(meta, "nvidia")
    row = TweakRow(meta, state)
    assert row.is_selected() is False
    row._toggle.setChecked(True, animate=False)
    row._on_switch(True)
    assert row.is_selected() is False
    assert row._toggle.isChecked() is False
    assert row._toggle.isLocked() is True


def test_no_orphan_handler_functions():
    import re

    tweaks_dir = ROOT / "tweaks"
    dead_all: list[str] = []
    for py in sorted(tweaks_dir.glob("*.py")):
        if py.name in ("__init__.py", "base.py"):
            continue
        text = py.read_text(encoding="utf-8")
        if "HANDLERS = {" not in text:
            continue
        funcs = set(re.findall(r"^def (\w+_(?:apply|revert))\(", text, re.M))
        refs = set(re.findall(r"(\w+_apply|\w+_revert)", text.split("HANDLERS = {", 1)[-1]))
        dead = funcs - refs
        dead_all.extend(f"{py.name}:{name}" for name in sorted(dead))
    assert dead_all == [], f"Orphan handler functions: {dead_all}"


def test_all_tweaks_have_hints():
    tweaks = json.loads((ROOT / "config" / "tweaks.json").read_text(encoding="utf-8"))["tweaks"]
    missing = [t["id"] for t in tweaks if not (t.get("hint") or "").strip()]
    assert missing == [], f"no hint: {missing[:5]}"


def test_build_display_hint_compact():
    from tweaks import create_manager
    from utils.tweak_hints import build_display_hint

    manager = create_manager()
    meta = manager.get_meta("enable_hags")
    assert meta is not None
    text = build_display_hint(meta)
    assert len(text) <= 320
    assert "WDDM" in text or len(text) > 10


_BANNED_UI = re.compile(
    r"администратор|права администратора|нужен администратор|требует админа|запустите от администратора",
    re.IGNORECASE,
)


def test_no_admin_phrases_in_hints():
    import re

    tweaks = json.loads((ROOT / "config" / "tweaks.json").read_text(encoding="utf-8"))["tweaks"]
    banned = []
    for t in tweaks:
        hint = (t.get("hint") or "").strip()
        if _BANNED_UI.search(hint):
            banned.append(t["id"])
    assert banned == [], f"admin wording in hints: {banned[:5]}"


def test_no_admin_wording_in_ui_strings():
    hits: list[str] = []

    locales = json.loads((ROOT / "locales" / "ru.json").read_text(encoding="utf-8"))
    for key, value in locales.items():
        if isinstance(value, str) and _BANNED_UI.search(value):
            hits.append(f"locales:{key}")

    ui_files = [
        ROOT / "ui" / "sidebar.py",
        ROOT / "ui" / "dashboard.py",
        ROOT / "utils" / "tweak_state_ui.py",
    ]
    for path in ui_files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if _BANNED_UI.search(line) and not line.strip().startswith("#"):
                hits.append(f"{path.name}:{line.strip()[:60]}")
                break

    assert hits == [], f"admin wording in UI: {hits}"


def test_all_tweaks_have_unique_hint_starts():
    tweaks = json.loads((ROOT / "config" / "tweaks.json").read_text(encoding="utf-8"))["tweaks"]
    starts: dict[str, list[str]] = {}
    for t in tweaks:
        hint = (t.get("hint") or "").strip()
        start = hint[:40]
        starts.setdefault(start, []).append(t["id"])
    dupes = {k: v for k, v in starts.items() if len(v) > 3}
    assert dupes == {}, f"too many identical hint starts: {list(dupes.items())[:2]}"


def test_apply_category_filters_active_and_incompatible():
    from core.tweak_state import TweakStateDetector

    det = TweakStateDetector()
    ids = ["amd_anti_lag", "enable_game_mode"]
    applicable, skipped = det.filter_applicable(
        ids,
        {"amd_anti_lag": False, "enable_game_mode": True},
    )
    assert "amd_anti_lag" in skipped
    assert "enable_game_mode" in applicable or "enable_game_mode" in skipped


def test_reg_backup_parse_paths():
    from core.reg_backup import _parse_check_paths

    paths = _parse_check_paths()
    assert isinstance(paths, dict)
    assert len(paths) > 50
    assert "enable_hags" in paths or "disable_sysmain" in paths


def test_parse_nvidia_smi_vram_rtx3050():
    from core.detector import _parse_nvidia_smi_vram

    out = "NVIDIA GeForce RTX 3050, 6144"
    vram = _parse_nvidia_smi_vram(out, "NVIDIA GeForce RTX 3050")
    assert vram == 6.0


def test_parse_nvidia_smi_vram_picks_largest():
    from core.detector import _parse_nvidia_smi_vram

    out = "Intel UHD Graphics 630, 1024\nNVIDIA GeForce RTX 3050, 6144"
    vram = _parse_nvidia_smi_vram(out, "")
    assert vram == 6.0


def test_wmi_overflow_not_trusted_for_nvidia():
    from core.detector import _WMI_VRAM_OVERFLOW_GB

    assert _WMI_VRAM_OVERFLOW_GB == 4.2


def test_format_freed_size():
    from core.disk_cleanup import format_freed_size

    assert format_freed_size(512) == "512 Б"
    assert "МБ" in format_freed_size(5 * 1024 * 1024)
    assert "ГБ" in format_freed_size(3 * 1024 ** 3)


def test_reg_backup_export_mock(monkeypatch, tmp_path):
    from tweaks import create_manager
    from core import reg_backup

    manager = create_manager()

    def fake_export(path: str):
        return {"TestValue": {"value": 1, "type": 4}}

    monkeypatch.setattr(reg_backup.reg, "export_key", fake_export)
    monkeypatch.setattr(reg_backup, "get_app_data_dir", lambda: tmp_path)

    monkeypatch.setattr(
        reg_backup,
        "_parse_check_paths",
        lambda: {"enable_game_mode": [r"HKCU\\Software\\Test\\Key"]},
    )

    original_get_state = manager.get_tweak_state

    def patched_get_state(tid, compatible=True):
        info = original_get_state(tid, compatible=compatible)
        if tid == "enable_game_mode":
            info.is_active = True
        return info

    monkeypatch.setattr(manager, "get_tweak_state", patched_get_state)

    path, msg = reg_backup.export_active_baseline(manager)
    assert path is not None
    assert path.exists()
    assert path.suffix == ".reg"
