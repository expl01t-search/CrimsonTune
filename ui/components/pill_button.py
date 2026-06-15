
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy


class PillButton(QPushButton):

    def __init__(self, text: str, *, variant: str = "primary", parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("pillBtn")
        self.setProperty("variant", variant)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.style().unpolish(self)
        self.style().polish(self)
