"""Боковая панель — Modern Clarity навигация."""

from __future__ import annotations

import getpass
import os
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from core.brand import APP_NAME, APP_VERSION
from core.i18n import nav_label, t
from ui.theme import SIDEBAR_WIDTH

NAV_KEYS = [
    "dashboard",
    "performance",
    "gaming",
    "directx",
    "opengl",
    "network",
    "privacy",
    "visual",
    "system",
    "profiles",
    "settings",
]


def _current_username() -> str:
    return (
        os.environ.get("USERNAME")
        or os.environ.get("USER")
        or getpass.getuser()
        or t("sidebar_user_fallback")
    )


class Sidebar(QFrame):
    """Боковое меню — плоский тёмный стиль."""

    def __init__(
        self,
        on_navigate: Callable[[str], None],
        *,
        tweak_count: int = 0,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self._on_navigate = on_navigate
        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 12, 16)
        layout.setSpacing(4)

        logo = QLabel(APP_NAME)
        logo.setObjectName("brandLogo")
        tagline = QLabel(t("app_subtitle"))
        tagline.setObjectName("brandTagline")
        stats = QLabel(t("sidebar_stats", version=APP_VERSION, count=tweak_count))
        stats.setObjectName("brandStats")
        layout.addWidget(logo)
        layout.addWidget(tagline)
        layout.addWidget(stats)
        layout.addSpacing(12)

        for key in NAV_KEYS:
            btn = QPushButton(nav_label(key))
            btn.setObjectName("navBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self._navigate(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch()

        footer = QFrame()
        footer.setObjectName("sidebarFooter")
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(8, 6, 8, 6)
        fl.setSpacing(4)

        user_title = QLabel(t("sidebar_username_title"))
        user_title.setObjectName("sidebarUserTitle")
        username = _current_username()
        user_lbl = QLabel()
        user_lbl.setObjectName("sidebarUserName")
        metrics = QFontMetrics(user_lbl.font())
        user_lbl.setText(
            metrics.elidedText(username, Qt.TextElideMode.ElideRight, SIDEBAR_WIDTH - 32)
        )
        user_lbl.setToolTip(username)
        fl.addWidget(user_title)
        fl.addWidget(user_lbl)
        layout.addWidget(footer)

        self._highlight("dashboard")

    def set_active(self, key: str) -> None:
        self._highlight(key)

    def _navigate(self, key: str) -> None:
        self._highlight(key)
        self._on_navigate(key)

    def _highlight(self, key: str) -> None:
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
