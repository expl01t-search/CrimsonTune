"""Фоновые QThread-воркеры с сигналами в UI-поток."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from core.backup import BackupManager
from tweaks.base import TweakManager


class ScanWorker(QThread):
    """Сканирование твиков в фоне — не блокирует UI."""

    progress = Signal(int, int)
    finished_ok = Signal()

    def __init__(self, manager: TweakManager) -> None:
        super().__init__()
        self._manager = manager

    def run(self) -> None:
        self._manager.refresh_states()
        metas = self._manager.get_all_meta()
        ids = [m.id for m in metas]
        total = len(ids)
        for i, tid in enumerate(ids):
            self._manager.get_tweak_state(tid, compatible=True)
            if i % 8 == 0 or i == total - 1:
                self.progress.emit(i + 1, total)
        self.finished_ok.emit()


class RevertWorker(QThread):
    finished_ok = Signal(int)

    def __init__(self, manager: TweakManager) -> None:
        super().__init__()
        self._manager = manager

    def run(self) -> None:
        results = self._manager.revert_all()
        ok = sum(1 for _, r in results if r.success)
        self._manager.refresh_states()
        self._manager.state_detector.invalidate()
        self._manager.state_detector.scan_all([m.id for m in self._manager.get_all_meta()])
        self.finished_ok.emit(ok)


class RestorePointWorker(QThread):
    finished_ok = Signal(bool, str)

    def __init__(self, backup: BackupManager) -> None:
        super().__init__()
        self._backup = backup

    def run(self) -> None:
        ok, msg = self._backup.create_restore_point()
        self.finished_ok.emit(ok, msg)


class DiskCleanupWorker(QThread):
    """Очистка temp/log/bak в фоне."""

    progress = Signal(int, int, str, int)
    finished_ok = Signal(int, int, int)

    def run(self) -> None:
        from core.disk_cleanup import run_disk_cleanup

        def on_progress(current: int, total: int, label: str, freed: int) -> None:
            self.progress.emit(current, total, label, freed)

        result = run_disk_cleanup(on_progress)
        self.finished_ok.emit(result.bytes_freed, result.files_deleted, result.errors)
