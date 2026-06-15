"""Работа с реестром Windows."""

from __future__ import annotations

import winreg
from typing import Any, Optional


HKEY_MAP = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKU": winreg.HKEY_USERS,
}


def _parse_path(path: str) -> tuple[int, str]:
    """Разбирает путь вида HKCU\\Software\\..."""
    parts = path.split("\\", 1)
    if len(parts) != 2 or parts[0] not in HKEY_MAP:
        raise ValueError(f"Некорректный путь реестра: {path}")
    return HKEY_MAP[parts[0]], parts[1]


def read_value(path: str, name: str, default: Any = None) -> Any:
    """Читает значение из реестра."""
    root, subkey = _parse_path(path)
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except FileNotFoundError:
        return default
    except OSError:
        return default


def write_value(path: str, name: str, value: Any, value_type: int = winreg.REG_DWORD) -> None:
    """Записывает значение в реестр, создавая ключ при необходимости."""
    root, subkey = _parse_path(path)
    with winreg.CreateKeyEx(root, subkey, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, value_type, value)


def delete_value(path: str, name: str) -> bool:
    """Удаляет значение из реестра. Возвращает True если удалено."""
    root, subkey = _parse_path(path)
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
            return True
    except (FileNotFoundError, OSError):
        return False


def key_exists(path: str) -> bool:
    """Проверяет существование ключа реестра."""
    root, subkey = _parse_path(path)
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ):
            return True
    except OSError:
        return False


def export_key(path: str) -> dict[str, Any]:
    """Экспортирует все значения ключа для бэкапа."""
    root, subkey = _parse_path(path)
    result: dict[str, Any] = {}
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ) as key:
            index = 0
            while True:
                try:
                    name, value, reg_type = winreg.EnumValue(key, index)
                    result[name] = {"value": value, "type": reg_type}
                    index += 1
                except OSError:
                    break
    except OSError:
        pass
    return result
