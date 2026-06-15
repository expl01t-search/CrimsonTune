
from __future__ import annotations

import json
from pathlib import Path

from core.logger import get_app_data_dir
from core.paths import resource_path
from core.tweak_state import TweakStatus

SUPPORTED_LANGUAGES: dict[str, str] = {
    "ru": "Русский",
    "en": "English",
}
DEFAULT_LANGUAGE = "ru"


def _locales_dir() -> Path:
    return resource_path("locales")


_STATUS_KEYS: dict[TweakStatus, str] = {
    TweakStatus.INACTIVE: "status_available",
    TweakStatus.ACTIVE_SYSTEM: "status_active_system",
    TweakStatus.APPLIED_APP: "status_applied_app",
    TweakStatus.ACTIVE_BOTH: "status_active",
    TweakStatus.UNKNOWN: "status_unknown",
    TweakStatus.ONE_SHOT: "status_oneshot",
    TweakStatus.INCOMPATIBLE: "status_incompatible",
}

_CATEGORY_KEYS = {
    "performance": "nav_performance",
    "gaming": "nav_gaming",
    "ssd": "nav_ssd",
    "graphics": "nav_graphics",
    "directx": "nav_directx",
    "opengl": "nav_opengl",
    "network": "nav_network",
    "privacy": "nav_privacy",
    "visual": "nav_visual",
    "system": "nav_system",
    "nvidia": "nav_nvidia",
    "amd": "nav_amd",
    "expert": "nav_expert",
}

_strings: dict[str, str] = {}
_tweak_strings: dict[str, dict[str, str]] = {}
_profile_strings: dict[str, dict[str, str]] = {}
_language: str = DEFAULT_LANGUAGE


def _settings_path() -> Path:
    return get_app_data_dir() / "settings.json"


def load_language() -> str:
    path = _settings_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            lang = str(data.get("language", DEFAULT_LANGUAGE)).lower()
            if lang in SUPPORTED_LANGUAGES:
                return lang
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            pass
    return DEFAULT_LANGUAGE


def save_language(lang: str) -> None:
    lang = lang.lower()
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    path = _settings_path()
    data: dict = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data["language"] = lang
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_tweak_strings(lang: str) -> dict[str, dict[str, str]]:
    if lang == DEFAULT_LANGUAGE:
        return {}
    path = _locales_dir() / "tweaks" / f"{lang}.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _load_profile_strings(lang: str) -> dict[str, dict[str, str]]:
    if lang == DEFAULT_LANGUAGE:
        return {}
    path = _locales_dir() / "profiles" / f"{lang}.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _load_strings(lang: str) -> dict[str, str]:
    path = _locales_dir() / f"{lang}.json"
    if not path.exists():
        path = _locales_dir() / f"{DEFAULT_LANGUAGE}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def init_locale(lang: str | None = None) -> str:
    global _strings, _tweak_strings, _profile_strings, _language
    _language = (lang or load_language()).lower()
    if _language not in SUPPORTED_LANGUAGES:
        _language = DEFAULT_LANGUAGE
    _strings = _load_strings(_language)
    _tweak_strings = _load_tweak_strings(_language)
    if _language != DEFAULT_LANGUAGE:
        from tweaks.supplemental_catalog import supplemental_en_strings

        _tweak_strings = {**supplemental_en_strings(), **_tweak_strings}
    _profile_strings = _load_profile_strings(_language)
    return _language


def set_language(lang: str) -> str:
    lang = lang.lower()
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    save_language(lang)
    return init_locale(lang)


def get_language() -> str:
    return _language


def t(key: str, default: str = "", **kwargs) -> str:
    text = _strings.get(key, default or key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError, IndexError):
            return text
    return text


def category_label(category: str) -> str:
    key = _CATEGORY_KEYS.get(category, f"nav_{category}")
    return t(key, default=category)


def risk_label(risk: str) -> str:
    return t(f"risk_{risk}", default=risk)


def status_label(status: TweakStatus) -> str:
    key = _STATUS_KEYS.get(status)
    return t(key, default=status.value) if key else status.value


def nav_label(page_key: str) -> str:
    return t(f"nav_{page_key}", default=page_key)


def localize_meta(meta):
    from dataclasses import replace

    tr = _tweak_strings.get(meta.id)
    if not tr:
        return meta
    return replace(
        meta,
        name=tr.get("name", meta.name),
        description=tr.get("description", meta.description),
        hint=tr.get("hint", meta.hint),
    )


def localize_profile(profile: dict) -> dict:
    pid = str(profile.get("id", ""))
    tr = _profile_strings.get(pid)
    if not tr:
        return profile
    out = dict(profile)
    if tr.get("name"):
        out["name"] = tr["name"]
    if tr.get("description"):
        out["description"] = tr["description"]
    return out


def restart_application() -> None:
    import os
    import sys

    from PySide6.QtCore import QProcess
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        os.execv(sys.executable, [sys.executable, *sys.argv[1:]])

    for widget in app.topLevelWidgets():
        widget.close()
    app.processEvents()

    relaunch_args = sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv
    if not QProcess.startDetached(sys.executable, relaunch_args):
        os.execv(sys.executable, [sys.executable, *relaunch_args])
    app.quit()
