"""Отдельное окно splash — инициализация до главного окна."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget

from core.brand import APP_NAME, APP_VERSION
from core.i18n import t
from core.detector import detect_system
from tweaks.base import TweakManager
from ui.workers import ScanWorker


class SplashWindow(QWidget):
    """Frameless splash: каталог → сканирование → сигнал finished."""

    finished = Signal()

    WIDTH = 520
    HEIGHT = 340

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("splashWindow")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        self._manager: Optional[TweakManager] = None
        self._worker: Optional[ScanWorker] = None
        self._ready = False
        self._fade: Optional[QPropertyAnimation] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("splashCard")
        card.setFixedWidth(420)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(10)

        title = QLabel(APP_NAME)
        title.setObjectName("splashTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tagline = QLabel(t("app_subtitle"))
        tagline.setObjectName("pageSubtitle")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version = QLabel(f"v{APP_VERSION}")
        version.setObjectName("muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status = QLabel(t("splash_starting"))
        self._status.setObjectName("overlayStatus")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._bar = QProgressBar()
        self._bar.setObjectName("startupProgress")
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(6)
        self._bar.setFixedWidth(320)

        self._percent = QLabel("0%")
        self._percent.setObjectName("startupPercent")
        self._percent.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(14)
        layout.addWidget(self._status, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(8)
        layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._percent, alignment=Qt.AlignmentFlag.AlignCenter)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        self.move(
            geo.x() + (geo.width() - self.width()) // 2,
            geo.y() + (geo.height() - self.height()) // 2,
        )

    def begin(self, manager: TweakManager) -> None:
        self._manager = manager
        self._set_progress(0, t("splash_preparing_catalog"))
        QTimer.singleShot(120, self._phase_detect)

    def _phase_detect(self) -> None:
        info = detect_system()
        gpu = info.gpu_name or "GPU"
        self._set_progress(8, t("splash_system_detected", build=info.os_build, gpu=gpu))
        QTimer.singleShot(80, self._phase_scan)

    def _phase_scan(self) -> None:
        if not self._manager:
            return
        self._set_progress(12, t("splash_scanning_state"))
        worker = ScanWorker(self._manager)
        worker.progress.connect(self._on_scan_progress)
        worker.finished_ok.connect(self._on_scan_done)
        worker.finished.connect(self._on_worker_finished)
        worker.start()
        self._worker = worker

    def _on_worker_finished(self) -> None:
        worker = self.sender()
        if worker is self._worker:
            self._worker = None

    def shutdown_worker(self) -> None:
        """Дожидается завершения фонового скана перед уничтожением splash."""
        worker = self._worker
        self._worker = None
        if worker is None:
            return
        try:
            from shiboken6 import isValid

            if not isValid(worker):
                return
            if worker.isRunning():
                worker.wait(5000)
            worker.deleteLater()
        except RuntimeError:
            pass

    def _on_scan_progress(self, current: int, total: int) -> None:
        pct = 12 + int((current / max(total, 1)) * 86)
        self._set_progress(pct, t("splash_scan_progress", current=current, total=total))

    def _on_scan_done(self) -> None:
        self._ready = True
        self._set_progress(100, t("splash_ready", app=APP_NAME))
        QTimer.singleShot(450, self._emit_finished)

    def _set_progress(self, pct: int, text: str) -> None:
        self._bar.setValue(max(0, min(100, pct)))
        self._percent.setText(f"{pct}%")
        self._status.setText(text)

    def _emit_finished(self) -> None:
        self.finished.emit()

    def prepare_for_handoff(self) -> None:
        """Снимает always-on-top перед передачей управления MainWindow."""
        flags = self.windowFlags()
        self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def set_handoff_message(self, text: str) -> None:
        self._set_progress(100, text)

    def closeEvent(self, event) -> None:
        if not self._ready:
            event.ignore()
            return
        self.shutdown_worker()
        super().closeEvent(event)

    def fade_out_and_close(self, on_done) -> None:
        self.setWindowOpacity(1.0)
        self._fade = QPropertyAnimation(self, b"windowOpacity")
        self._fade.setDuration(220)
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade.finished.connect(on_done)
        self._fade.start()
