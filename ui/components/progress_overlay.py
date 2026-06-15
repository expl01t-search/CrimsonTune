"""Overlay прогресса."""

from __future__ import annotations

from core.i18n import t
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget


class ProgressOverlay(QFrame):
    """Полноэкранный overlay с прогресс-баром."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("overlay")
        self.hide()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        card = QWidget()
        card.setObjectName("overlayCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._title = QLabel(t("applying_tweaks"))
        self._title.setObjectName("overlayTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status = QLabel("")
        self._status.setObjectName("overlayStatus")
        self._status.setWordWrap(True)
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bar = QProgressBar()
        self._bar.setObjectName("overlayProgress")
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setMinimumWidth(280)
        self._bar.setMaximumWidth(520)

        card_layout.addWidget(self._title)
        card_layout.addWidget(self._status)
        card_layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def show_progress(self, current: int, total: int, tweak_name: str = "") -> None:
        if self.parent():
            self.setGeometry(self.parent().rect())
            bar_w = max(280, min(520, int(self.parent().width() * 0.42)))
            self._bar.setFixedWidth(bar_w)
        if not self.isVisible():
            self.show()
            self.raise_()
        pct = int((current / max(total, 1)) * 100)
        self._bar.setValue(pct)
        self._status.setText(f"{current} / {total}: {tweak_name}")

    def hide_overlay(self) -> None:
        self.hide()

    def resizeEvent(self, event) -> None:
        if self.parent():
            self.setGeometry(self.parent().rect())
            bar_w = max(280, min(520, int(self.parent().width() * 0.42)))
            self._bar.setFixedWidth(bar_w)
        super().resizeEvent(event)
