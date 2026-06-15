"""Toast-уведомления."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, QPoint
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class ToastManager:
    """Менеджер toast — только slide, без graphics effects."""

    def __init__(self, parent) -> None:
        self._parent = parent
        self._anims: list = []

    def show(self, message: str, level: str = "info", duration: int = 4000) -> None:
        toast = QFrame(self._parent)
        toast.setObjectName("toast")
        toast.setProperty("level", level if level in ("success", "error", "info", "warning") else "info")
        toast.style().unpolish(toast)
        toast.style().polish(toast)
        toast.setFixedWidth(400)

        lbl = QLabel(message, toast)
        lbl.setWordWrap(True)
        lbl.setObjectName("toastText")
        layout = QVBoxLayout(toast)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(lbl)
        toast.adjustSize()

        pr = self._parent.rect()
        x = pr.width() - toast.width() - 20
        y = pr.height() - toast.height() - 20
        toast.move(x + 50, y)
        toast.show()
        toast.raise_()

        slide = QPropertyAnimation(toast, b"pos", toast)
        slide.setDuration(280)
        slide.setStartValue(QPoint(x + 50, y))
        slide.setEndValue(QPoint(x, y))
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        slide.start()
        self._anims.append(slide)

        def dismiss():
            out = QPropertyAnimation(toast, b"pos", toast)
            out.setDuration(200)
            out.setStartValue(toast.pos())
            out.setEndValue(QPoint(x + 50, y))
            out.finished.connect(toast.deleteLater)
            out.start()
            self._anims.append(out)

        QTimer.singleShot(duration, dismiss)
