"""Приветственный overlay при первом запуске."""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from core.brand import APP_DATA_DIR, APP_NAME
from core.i18n import t


def _flag_path() -> Path:
    base = Path(os.environ.get("APPDATA", "")) / APP_DATA_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base / ".onboarding_done"


def is_onboarding_done() -> bool:
    return _flag_path().exists()


def mark_onboarding_done() -> None:
    _flag_path().touch()


class WelcomeOverlay(QFrame):
    """Одноразовое приветствие после splash."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("welcomeOverlay")
        self.hide()

        card = QFrame(self)
        card.setObjectName("welcomeCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel(t("onboarding_title", app=APP_NAME))
        title.setObjectName("welcomeTitle")
        layout.addWidget(title)

        for key in ("onboarding_line_1", "onboarding_line_2", "onboarding_line_3"):
            lbl = QLabel(f"·  {t(key)}")
            lbl.setObjectName("welcomeText")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        btn = QPushButton(t("btn_got_it"))
        btn.setObjectName("applyBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._dismiss)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def show_overlay(self) -> None:
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()

    def resizeEvent(self, event) -> None:
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)

    def _dismiss(self) -> None:
        mark_onboarding_done()
        self.hide()
