"""Пути к ресурсам в dev и в PyInstaller bundle."""

from __future__ import annotations

import sys
from pathlib import Path


def bundle_root() -> Path:
    """Корень read-only ресурсов (config, locales, ui/assets)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    return bundle_root().joinpath(*parts)
