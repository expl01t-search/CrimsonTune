
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_locale_keys_match():
    ru = json.loads((ROOT / "locales" / "ru.json").read_text(encoding="utf-8"))
    en = json.loads((ROOT / "locales" / "en.json").read_text(encoding="utf-8"))
    ru_keys = set(ru)
    en_keys = set(en)
    assert ru_keys == en_keys, f"Missing keys: ru-only={ru_keys - en_keys}, en-only={en_keys - ru_keys}"


def test_i18n_defaults_to_russian():
    from core.i18n import init_locale, t

    init_locale("ru")
    assert t("nav_settings") == "Настройки"
    init_locale("en")
    assert t("nav_settings") == "Settings"


def test_tweak_locale_covers_catalog():
    from tweaks import create_manager

    manager = create_manager()
    from tweaks.supplemental_catalog import supplemental_en_strings

    en = json.loads((ROOT / "locales" / "tweaks" / "en.json").read_text(encoding="utf-8"))
    en = {**supplemental_en_strings(), **en}
    ids = {m.id for m in manager.get_all_meta()}
    assert ids == set(en), f"missing tweak locales: {ids - set(en)}"
    for tid in ids:
        entry = en[tid]
        assert entry.get("name") and entry.get("description"), tid


def test_localize_meta_english():
    from core.i18n import init_locale, localize_meta
    from tweaks.base import TweakMeta

    init_locale("en")
    meta = TweakMeta(
        id="disable_sysmain",
        name="RU name",
        description="RU desc",
        category="performance",
        hint="RU hint",
    )
    localized = localize_meta(meta)
    assert localized.name == "Disable SysMain (Superfetch)"
    assert localized.description != "RU desc"
    assert localized.hint != "RU hint"


def test_localize_profile_english():
    from core.i18n import init_locale, localize_profile

    init_locale("en")
    profile = {
        "id": "balanced",
        "name": "Сбалансированный",
        "description": "RU",
        "tweaks": [],
    }
    out = localize_profile(profile)
    assert out["name"] == "Balanced"
    assert out["description"] != "RU"
