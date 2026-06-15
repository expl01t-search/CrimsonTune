"""Бейдж статуса твика."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from core.i18n import status_label
from core.tweak_state import TweakStatus


class StatusBadge(QLabel):
    """Цветной бейдж состояния твика."""

    def __init__(self, status: TweakStatus, text: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("statusBadge")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setMaximumWidth(176)
        self.setMinimumWidth(112)
        self.update_status(status, text)

    def update_status(self, status: TweakStatus, text: str = "") -> None:
        if status == TweakStatus.INCOMPATIBLE and text:
            label = text
        else:
            label = status_label(status)
        self.setText(label)
        self.setToolTip(label)
        self.setProperty("badgeStatus", status.value)
        self.style().unpolish(self)
        self.style().polish(self)
