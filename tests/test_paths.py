"""Тесты путей к bundled-ресурсам."""

from __future__ import annotations

from pathlib import Path

from core.paths import bundle_root, resource_path


def test_resource_paths_exist_in_dev():
    root = bundle_root()
    assert root.is_dir()
    assert resource_path("config", "tweaks.json").is_file()
    assert resource_path("locales", "en.json").is_file()
    assert resource_path("locales", "ru.json").is_file()
    assert resource_path("icon.ico").is_file()
