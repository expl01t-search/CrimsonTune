from __future__ import annotations

import getpass
import os
from typing import Callable

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from core.brand import APP_NAME, APP_VERSION
from core.i18n import nav_label, t
from ui.theme import SIDEBAR_WIDTH
from utils.categories import NAV_KEYS


def _current_username() -> str:
    return (
        os.environ.get("USERNAME")
        or os.environ.get("USER")
        or getpass.getuser()
        or t("sidebar_user_fallback")
    )


class Sidebar(QFrame):
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
        self._active_key = "dashboard"
        self._indicator_anim: QPropertyAnimation | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 12, 16)
        layout.setSpacing(4)

        logo = QLabel(APP_NAME)
        logo.setObjectName("brandLogo")
        self._tagline = QLabel(t("app_subtitle"))
        self._tagline.setObjectName("brandTagline")
        self._stats = QLabel(t("sidebar_stats", version=APP_VERSION, count=tweak_count))
        self._stats.setObjectName("brandStats")
        layout.addWidget(logo)
        layout.addWidget(self._tagline)
        layout.addWidget(self._stats)
        layout.addSpacing(12)

        self._nav_host = QWidget()
        self._nav_host.setObjectName("navHost")
        nav_layout = QVBoxLayout(self._nav_host)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(4)

        for key in NAV_KEYS:
            btn = QPushButton(nav_label(key))
            btn.setObjectName("navBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self._navigate(k))
            nav_layout.addWidget(btn)
            self._buttons[key] = btn

        self._indicator = QFrame(self._nav_host)
        self._indicator.setObjectName("navIndicator")
        self._indicator.setFixedWidth(3)
        self._indicator.hide()

        layout.addWidget(self._nav_host)
        layout.addStretch()

        footer = QFrame()
        footer.setObjectName("sidebarFooter")
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(8, 6, 8, 6)
        fl.setSpacing(2)

        user_title = QLabel(t("sidebar_username_title"))
        user_title.setObjectName("sidebarUserTitle")
        self._user_title = user_title
        username = _current_username()
        self._user_lbl = QLabel()
        self._user_lbl.setObjectName("sidebarUserName")
        metrics = QFontMetrics(self._user_lbl.font())
        self._user_lbl.setText(
            metrics.elidedText(username, Qt.TextElideMode.ElideRight, SIDEBAR_WIDTH - 32)
        )
        self._user_lbl.setToolTip(username)
        fl.addWidget(user_title)
        fl.addWidget(self._user_lbl)
        layout.addWidget(footer)

        self._tweak_count = tweak_count
        self._highlight("dashboard", animate=False)

    def retranslate_ui(self, *, tweak_count: int | None = None) -> None:
        if tweak_count is not None:
            self._tweak_count = tweak_count
        self._tagline.setText(t("app_subtitle"))
        self._stats.setText(t("sidebar_stats", version=APP_VERSION, count=self._tweak_count))
        for key, btn in self._buttons.items():
            btn.setText(nav_label(key))
        self._user_title.setText(t("sidebar_username_title"))

    def set_active(self, key: str) -> None:
        if key == self._active_key:
            return
        self._highlight(key)

    def _navigate(self, key: str) -> None:
        if key == self._active_key:
            return
        self._highlight(key)
        self._on_navigate(key)

    def _button_rect(self, key: str) -> QRect:
        btn = self._buttons[key]
        top_left = btn.mapTo(self._nav_host, btn.rect().topLeft())
        return QRect(0, top_left.y(), 3, btn.height())

    def _clear_indicator_anim(self) -> None:
        self._indicator_anim = None

    def _stop_indicator_anim(self) -> None:
        anim = self._indicator_anim
        self._indicator_anim = None
        if anim is None:
            return
        try:
            anim.finished.disconnect(self._clear_indicator_anim)
        except (RuntimeError, TypeError):
            pass
        try:
            anim.stop()
        except RuntimeError:
            pass

    def _highlight(self, key: str, *, animate: bool = True) -> None:
        self._active_key = key
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        target = self._button_rect(key)
        if not self._indicator.isVisible():
            self._indicator.setGeometry(target)
            self._indicator.show()
            return

        if not animate:
            self._stop_indicator_anim()
            self._indicator.setGeometry(target)
            return

        self._stop_indicator_anim()

        anim = QPropertyAnimation(self._indicator, b"geometry", self)
        anim.setDuration(220)
        anim.setStartValue(self._indicator.geometry())
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(self._clear_indicator_anim)
        anim.start()
        self._indicator_anim = anim

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._active_key in self._buttons:
            self._highlight(self._active_key, animate=False)
