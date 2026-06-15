"""Экспорт .reg бэкапа активных твиков в системе."""

from __future__ import annotations

import json
import re
import winreg
from datetime import datetime
from pathlib import Path
from typing import Any

from core.logger import get_app_data_dir, setup_logger
from tweaks.base import TweakManager
from utils import registry as reg

logger = setup_logger(__name__)

ROOT = Path(__file__).resolve().parent.parent
_HIVE_EXPORT = {
    "HKCU": "HKEY_CURRENT_USER",
    "HKLM": "HKEY_LOCAL_MACHINE",
}


def _parse_check_paths() -> dict[str, list[str]]:
    """Извлекает пути реестра из SYSTEM_CHECKS в tweak_state.py."""
    text = (ROOT / "core" / "tweak_state.py").read_text(encoding="utf-8")
    marker = "SYSTEM_CHECKS"
    if marker not in text:
        return {}
    block = text.split(marker, 1)[-1].split("= {", 1)[-1].split("\n}\n", 1)[0]
    paths: dict[str, list[str]] = {}
    current_id: str | None = None
    for line in block.splitlines():
        m_id = re.match(r'\s+"([a-z0-9_]+)":\s*(?:lambda|_)', line)
        if m_id:
            current_id = m_id.group(1)
            paths.setdefault(current_id, [])
        if current_id:
            for p in re.findall(r'r"(HK(?:CU|LM)\\[^"]+)"', line):
                if p not in paths[current_id]:
                    paths[current_id].append(p)
    return paths


def _format_value(name: str, value: Any, reg_type: int) -> str:
    if reg_type == winreg.REG_DWORD:
        if isinstance(value, bool):
            value = 1 if value else 0
        return f'"{name}"=dword:{int(value):08x}'
    if reg_type == winreg.REG_SZ:
        escaped = str(value).replace("\\", "\\\\")
        return f'"{name}"="{escaped}"'
    if reg_type in (winreg.REG_MULTI_SZ, winreg.REG_EXPAND_SZ):
        raw = str(value).encode("utf-16-le") + b"\x00\x00"
        hexpart = ",".join(f"{b:02x}" for b in raw)
        return f'"{name}"=hex(7):{hexpart}'
    return f'"{name}"=dword:{int(value):08x}'


def _export_path_lines(path: str) -> list[str]:
    hive_key = _HIVE_EXPORT.get(path.split("\\", 1)[0])
    if not hive_key:
        return []
    sub = path.split("\\", 1)[1]
    export_path = f"{hive_key}\\{sub}"
    lines = [f"[{export_path}]"]
    try:
        data = reg.export_key(path)
    except ValueError:
        return []
    if not data:
        return []
    for name, item in sorted(data.items()):
        lines.append(_format_value(name, item["value"], item["type"]))
    lines.append("")
    return lines


def export_active_baseline(manager: TweakManager) -> tuple[Path | None, str]:
    """
    Экспортирует .reg для твиков, активных в системе (is_active).
    Возвращает (путь, сообщение).
    """
    check_paths = _parse_check_paths()
    metas = manager.get_all_meta()
    compat = {m.id: True for m in metas}
    ids = [m.id for m in metas]

    active_ids: list[str] = []
    for tid in ids:
        state = manager.get_tweak_state(tid, compatible=compat.get(tid, True))
        if state.is_active:
            active_ids.append(tid)

    if not active_ids:
        return None, "Нет активных твиков для бэкапа"

    seen_paths: set[str] = set()
    reg_lines = ["Windows Registry Editor Version 5.00", ""]
    exported_tweaks: list[str] = []

    for tid in active_ids:
        for path in check_paths.get(tid, []):
            if path in seen_paths:
                continue
            chunk = _export_path_lines(path)
            if len(chunk) > 2:
                reg_lines.extend(chunk)
                seen_paths.add(path)
                exported_tweaks.append(tid)

    if not seen_paths:
        return None, "Активные твики не используют отслеживаемые ключи реестра"

    backup_dir = get_app_data_dir() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reg_path = backup_dir / f"baseline_{stamp}.reg"
    reg_path.write_text("\r\n".join(reg_lines), encoding="utf-16-le")

    meta_path = backup_dir / f"baseline_{stamp}.json"
    meta_path.write_text(
        json.dumps(
            {
                "timestamp": stamp,
                "active_tweak_ids": active_ids,
                "exported_paths": sorted(seen_paths),
                "tweak_count": len(active_ids),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("Baseline .reg: %s (%s paths)", reg_path, len(seen_paths))
    return reg_path, f"Сохранено: {reg_path.name} ({len(active_ids)} твиков, {len(seen_paths)} ключей)"
