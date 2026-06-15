"""Константы бренда CrimsonTune."""

from pathlib import Path

APP_NAME = "CrimsonTune"
APP_TAGLINE = "Точная настройка Windows"
APP_VERSION = "1.2.0"
APP_DATA_DIR = "CrimsonTune"
LEGACY_DATA_DIRS = ("VeloForge", "WinTweaker")
APP_ROOT = Path(__file__).resolve().parent.parent
ICON_FILE = APP_ROOT / "icon.ico"
