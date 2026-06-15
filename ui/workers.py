
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QThread, Signal

from core.backup import BackupManager
from tweaks.base import TweakManager, TweakMeta


class UpdateCheckWorker(QThread):
    finished_ok = Signal(object)

    def run(self) -> None:
        try:
            from core.updater import check_for_update

            release, status = check_for_update()
        except Exception:
            release, status = None, "error"
        self.finished_ok.emit((release, status))


class ScanWorker(QThread):

    progress = Signal(int, int)
    finished_ok = Signal()

    def __init__(
        self,
        manager: TweakManager,
        *,
        compat_fn: Callable[[TweakMeta], bool] | None = None,
    ) -> None:
        super().__init__()
        self._manager = manager
        self._compat_fn = compat_fn

    def run(self) -> None:
        self._manager.refresh_states()
        detector = self._manager.state_detector
        detector.invalidate()
        detector.begin_batch_scan()
        try:
            metas = self._manager.get_all_meta()
            compat_map = (
                {m.id: self._compat_fn(m) for m in metas}
                if self._compat_fn
                else {m.id: True for m in metas}
            )
            ids = [m.id for m in metas]
            total = len(ids)
            for i, tid in enumerate(ids):
                detector.get_state(tid, compatible=compat_map.get(tid, True))
                if i % 12 == 0 or i == total - 1:
                    self.progress.emit(i + 1, total)
        finally:
            detector.end_batch_scan()
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
        detector = self._manager.state_detector
        detector.invalidate()
        detector.begin_batch_scan()
        try:
            detector.scan_all([m.id for m in self._manager.get_all_meta()])
        finally:
            detector.end_batch_scan()
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

    progress = Signal(int, int, str, int)
    finished_ok = Signal(int, int, int)

    def run(self) -> None:
        from core.disk_cleanup import run_disk_cleanup

        def on_progress(current: int, total: int, label: str, freed: int) -> None:
            self.progress.emit(current, total, label, freed)

        result = run_disk_cleanup(on_progress)
        self.finished_ok.emit(result.bytes_freed, result.files_deleted, result.errors)


class DiskLoadWorker(QThread):
    finished_ok = Signal(object)

    def run(self) -> None:
        from ui.dashboard import _list_system_disks

        self.finished_ok.emit(_list_system_disks())


class ApplyWorker(QThread):
    progress = Signal(int, int, str)
    finished_apply = Signal(int, int, int)

    def __init__(self, manager: TweakManager, tweak_ids: list[str]) -> None:
        super().__init__()
        self.manager = manager
        self.tweak_ids = tweak_ids

    def run(self) -> None:
        ok, fail = 0, 0
        total = len(self.tweak_ids)
        for i, tid in enumerate(self.tweak_ids):
            meta = self.manager.get_meta(tid)
            name = meta.name if meta else tid
            self.progress.emit(i + 1, total, name)
            result = self.manager.apply_tweak(tid)
            if result.success:
                ok += 1
            else:
                fail += 1
        self.finished_apply.emit(ok, fail, total)
