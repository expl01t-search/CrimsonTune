"""Проверка и запрос прав администратора."""

from __future__ import annotations

import ctypes
import sys


def is_admin() -> bool:
    """Проверяет, запущено ли приложение с правами администратора."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def request_admin_restart() -> bool:
    """Перезапускает приложение с правами администратора."""
    if is_admin():
        return True
    try:
        params = " ".join(f'"{arg}"' for arg in sys.argv)
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        return True
    except OSError:
        return False
