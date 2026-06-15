"""Система резервного копирования и отката."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from core.brand import APP_NAME
from core.logger import get_app_data_dir, setup_logger

logger = setup_logger(__name__)


class BackupManager:
    """Управляет бэкапами состояния твиков."""

    def __init__(self) -> None:
        self.backup_dir = get_app_data_dir() / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = get_app_data_dir() / "applied_tweaks.json"
        self._applied: dict[str, Any] = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save_state(self) -> None:
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self._applied, f, ensure_ascii=False, indent=2)

    def create_session_backup(self, tweak_ids: list[str]) -> Path:
        """Создаёт бэкап-сессию перед применением твиков."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.backup_dir / f"session_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "timestamp": timestamp,
            "tweak_ids": tweak_ids,
            "registry_snapshots": {},
        }
        meta_path = session_dir / "meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        logger.info("Создан бэкап-сессия: %s", session_dir)
        return session_dir

    def save_registry_snapshot(
        self,
        session_dir: Path,
        tweak_id: str,
        path: str,
        snapshot: dict[str, Any],
    ) -> None:
        """Сохраняет снимок реестра для твика."""
        meta_path = session_dir / "meta.json"
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        meta["registry_snapshots"][tweak_id] = {
            "path": path,
            "values": snapshot,
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def record_applied(self, tweak_id: str, revert_data: Any) -> None:
        """Записывает применённый твик для отката."""
        self._applied[tweak_id] = {
            "applied_at": datetime.now().isoformat(),
            "revert_data": revert_data,
        }
        self._save_state()

    def remove_applied(self, tweak_id: str) -> None:
        """Удаляет запись о применённом твике."""
        self._applied.pop(tweak_id, None)
        self._save_state()

    def get_revert_data(self, tweak_id: str) -> Optional[Any]:
        """Возвращает данные для отката твика."""
        entry = self._applied.get(tweak_id)
        if entry:
            return entry.get("revert_data")
        return None

    def is_applied(self, tweak_id: str) -> bool:
        """Проверяет, применён ли твик."""
        return tweak_id in self._applied

    def get_all_applied(self) -> list[str]:
        """Возвращает список применённых твиков."""
        return list(self._applied.keys())

    def create_restore_point(self) -> tuple[bool, str]:
        """Создаёт точку восстановления Windows."""
        try:
            import subprocess

            desc = f"{APP_NAME}_{datetime.now():%Y%m%d_%H%M%S}"
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"Checkpoint-Computer -Description '{desc}' -RestorePointType 'MODIFY_SETTINGS'",
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=120,
            )
            if result.returncode == 0:
                return True, "Точка восстановления создана"
            return False, result.stderr or "Не удалось создать точку восстановления"
        except Exception as exc:
            return False, str(exc)

    def export_restore_script(self) -> Path:
        """Генерирует RESTORE.bat для экстренного отката."""
        script_path = Path(__file__).resolve().parent.parent / "RESTORE.bat"
        content = f"""@echo off
chcp 65001 >nul
echo {APP_NAME} - Экстренный откат
echo ================================
echo Запуск отката всех применённых твиков...
python "%~dp0main.py" --restore-all
pause
"""
        script_path.write_text(content, encoding="utf-8")
        return script_path
