
from __future__ import annotations

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QWidget


class UiDebouncer(QObject):

    def __init__(self, delay_ms: int = 280, parent=None) -> None:
        super().__init__(parent)
        self._delay = delay_ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._callback = None
        self._timer.timeout.connect(self._on_timeout)

    def trigger(self, callback) -> None:
        self._callback = callback
        self._timer.stop()
        self._timer.start(self._delay)

    def flush(self) -> None:
        if self._callback:
            self._timer.stop()
            self._on_timeout()

    def _on_timeout(self) -> None:
        if self._callback:
            cb = self._callback
            self._callback = None
            cb()


def batch_widget_update(widget: QWidget, fn, *, repaint: bool = True) -> None:
    widget.setUpdatesEnabled(False)
    try:
        fn()
    finally:
        widget.setUpdatesEnabled(True)
        if repaint:
            widget.adjustSize()
            widget.updateGeometry()
