"""Тесты PySide6 UI."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_no_customtkinter_in_ui():
    ui_dir = ROOT / "ui"
    for py in ui_dir.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "customtkinter" not in text, f"customtkinter found in {py}"
        assert "import tkinter" not in text, f"tkinter found in {py}"


def test_pyside6_imports():
    from PySide6.QtWidgets import QApplication, QMainWindow
    from ui.animations import AnimationHelper
    from ui.splash import SplashWindow
    from ui.theme import load_stylesheet

    assert QApplication is not None
    assert AnimationHelper is not None
    assert SplashWindow is not None
    assert len(load_stylesheet()) > 0


def test_extended_handlers_registered():
    from tweaks import create_manager

    manager = create_manager()
    assert manager.get_meta("disable_game_bar_presence") is not None
    assert "disable_game_bar_presence" in manager._tweaks
