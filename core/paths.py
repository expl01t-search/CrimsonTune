from __future__ import annotations

import shutil
import sys
from pathlib import Path


def _dev_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _appdata_cache_root() -> Path:
    from core.brand import APP_VERSION
    from core.logger import get_app_data_dir

    return get_app_data_dir() / "runtime" / APP_VERSION


def _meipass_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", ""))


def _bundle_stamp(meipass: Path) -> str:
    src = meipass / "config" / "tweaks.json"
    if not src.is_file():
        return ""
    return f"{src.stat().st_mtime_ns}:{src.stat().st_size}"


def _cache_is_fresh(cache: Path, meipass: Path) -> bool:
    stamp_file = cache / ".bundle_stamp"
    tweaks = cache / "config" / "tweaks.json"
    locales = cache / "locales" / "ru.json"
    if not stamp_file.is_file() or not tweaks.is_file() or not locales.is_file():
        return False
    try:
        return stamp_file.read_text(encoding="utf-8").strip() == _bundle_stamp(meipass)
    except OSError:
        return False


def _write_cache_stamp(cache: Path, meipass: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    (cache / ".bundle_stamp").write_text(_bundle_stamp(meipass), encoding="utf-8")


def _seed_frozen_cache() -> Path:
    meipass = _meipass_root()
    cache = _appdata_cache_root()
    src_tweaks = meipass / "config" / "tweaks.json"
    if not src_tweaks.is_file():
        raise FileNotFoundError(
            f"Не найден {src_tweaks}. Переустановите CrimsonTune или соберите EXE с config/."
        )
    if cache.exists():
        shutil.rmtree(cache, ignore_errors=True)
    cache.mkdir(parents=True, exist_ok=True)
    for folder in ("config", "locales"):
        src = meipass / folder
        if src.is_dir():
            shutil.copytree(src, cache / folder)
    icon_src = meipass / "icon.ico"
    if icon_src.is_file():
        shutil.copy2(icon_src, cache / "icon.ico")
    _write_cache_stamp(cache, meipass)
    return cache


def bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        meipass = _meipass_root()
        cache = _appdata_cache_root()
        if _cache_is_fresh(cache, meipass):
            return cache
        return _seed_frozen_cache()
    return _dev_root()


def resource_path(*parts: str) -> Path:
    return bundle_root().joinpath(*parts)
