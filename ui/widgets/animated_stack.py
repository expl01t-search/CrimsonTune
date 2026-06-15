from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame, QStackedWidget, QWidget


class _FadeOverlay(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("stackFadeOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self._alpha = 0.0

    def get_alpha(self) -> float:
        return self._alpha

    def set_alpha(self, value: float) -> None:
        clamped = max(0.0, min(1.0, value))
        if abs(clamped - self._alpha) < 0.001:
            return
        self._alpha = clamped
        self.update()

    alpha = Property(float, get_alpha, set_alpha)

    def paintEvent(self, event) -> None:
        if self._alpha <= 0.001:
            return
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(10, 10, 15, int(255 * self._alpha)))


class AnimatedPageStack(QStackedWidget):
    DURATION_MS = 260

    page_shown = Signal(QWidget)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._busy = False
        self._pending: QWidget | None = None
        self._target: QWidget | None = None
        self._anim: QPropertyAnimation | None = None

        self._overlay = _FadeOverlay(self)
        self._overlay.hide()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())

    def set_current_animated(self, widget: QWidget) -> None:
        if widget is self.currentWidget() and not self._busy:
            return
        if self._busy:
            self._pending = widget
            return

        self._target = widget
        if self.currentWidget() is None:
            self.setCurrentWidget(widget)
            self.page_shown.emit(widget)
            return

        self._busy = True
        self._overlay.setGeometry(self.rect())
        self._overlay.show()
        self._overlay.raise_()
        self._run_fade(0.0, 1.0, self._on_cover_complete)

    def _on_cover_complete(self) -> None:
        target = self._target
        if target is not None:
            self.setCurrentWidget(target)
        self._run_fade(1.0, 0.0, self._on_reveal_complete)

    def _on_reveal_complete(self) -> None:
        self._overlay.hide()
        self._overlay.set_alpha(0.0)
        self._busy = False
        shown = self._target
        self._target = None
        if shown is not None:
            self.page_shown.emit(shown)
        pending = self._pending
        self._pending = None
        if pending is not None and pending is not shown:
            self.set_current_animated(pending)

    def _clear_fade_anim(self) -> None:
        self._anim = None

    def _stop_fade_anim(self) -> None:
        anim = self._anim
        self._anim = None
        if anim is None:
            return
        try:
            anim.finished.disconnect()
        except (RuntimeError, TypeError):
            pass
        try:
            anim.stop()
        except RuntimeError:
            pass

    def _run_fade(self, start: float, end: float, on_done) -> None:
        self._stop_fade_anim()

        self._overlay.set_alpha(start)
        anim = QPropertyAnimation(self._overlay, b"alpha", self)
        anim.setDuration(max(80, self.DURATION_MS // 2))
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(on_done)
        self._anim = anim
        anim.start()
