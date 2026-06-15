"""Безопасные анимации без QGraphicsOpacityEffect на сложных виджетах."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PySide6.QtWidgets import QWidget


class AnimationHelper:
    """Помощник анимаций — только windowOpacity и geometry (без graphics effects)."""

    _animations: list = []

    @classmethod
    def _keep(cls, anim) -> QPropertyAnimation:
        cls._animations.append(anim)
        anim.finished.connect(lambda: cls._animations.remove(anim) if anim in cls._animations else None)
        return anim

    @classmethod
    def fade_window_in(cls, window: QWidget, duration: int = 350) -> None:
        """Fade-in только для top-level окон через windowOpacity."""
        if not window.isWindow():
            return
        window.setWindowOpacity(0.0)
        anim = QPropertyAnimation(window, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        cls._keep(anim)

    @classmethod
    def fade_window_out(cls, window: QWidget, duration: int = 250, on_finished: Optional[Callable[[], None]] = None) -> None:
        if not window.isWindow():
            if on_finished:
                on_finished()
            return
        anim = QPropertyAnimation(window, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(window.windowOpacity())
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        if on_finished:
            anim.finished.connect(on_finished)
        anim.start()
        cls._keep(anim)

    @classmethod
    def slide_in_widget(cls, widget: QWidget, offset: int = 30, duration: int = 280) -> None:
        """Сдвиг виджета без opacity effect."""
        end_pos = widget.pos()
        start_pos = end_pos
        widget.move(start_pos.x() + offset, start_pos.y())
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(end_pos)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        cls._keep(anim)

    @classmethod
    def stagger_reveal(cls, widgets: list[QWidget], delay: int = 35) -> None:
        """Появление карточек с задержкой (без сдвига — совместимо с layout)."""
        for i, w in enumerate(widgets):
            w.setVisible(False)
            QTimer.singleShot(i * delay, w.show)

    @classmethod
    def pulse_property(cls, widget: QWidget, prop: bytes, start, end, duration: int = 800) -> QPropertyAnimation:
        anim = QPropertyAnimation(widget, prop)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.start()
        return cls._keep(anim)
