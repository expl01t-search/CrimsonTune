"""Настройка логирования."""

from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from core.brand import APP_DATA_DIR, APP_NAME, LEGACY_DATA_DIRS


def get_app_data_dir() -> Path:
    """Папка данных с миграцией из VeloForge / WinTweaker."""
    base = Path(os.environ.get("APPDATA", os.path.expanduser("~")))
    path = base / APP_DATA_DIR

    if not path.exists():
        for legacy_name in LEGACY_DATA_DIRS:
            legacy = base / legacy_name
            if legacy.exists():
                try:
                    shutil.copytree(legacy, path)
                    break
                except OSError:
                    pass

    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_logger(name: str = APP_NAME) -> logging.Logger:
    """Инициализирует логгер с записью в файл и консоль."""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{datetime.now():%Y-%m-%d}.log"
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
