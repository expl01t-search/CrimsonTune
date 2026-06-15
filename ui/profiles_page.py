"""Страница профилей."""

from __future__ import annotations

import json
from core.paths import resource_path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from core.i18n import localize_profile, t
from tweaks.base import TweakManager
from ui.theme import style_scroll_area
from utils.tweak_ids import dedupe_preserve_order


class ProfilesPage(QWidget):
    """Готовые пресеты с прогрессом."""

    def __init__(
        self,
        manager: TweakManager,
        *,
        filter_fn: Callable[[list[str]], tuple[list[str], list[str]]],
        on_apply: Callable[[dict], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appPage")
        self.manager = manager
        self._filter = filter_fn
        self._on_apply = on_apply

        outer = QVBoxLayout(self)
        outer.setSpacing(10)
        title = QLabel(t("nav_profiles"))
        title.setObjectName("pageTitle")
        sub = QLabel(t("profiles_subtitle"))
        sub.setObjectName("pageSubtitle")
        outer.addWidget(title)
        outer.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setSpacing(12)
        style_scroll_area(scroll, container)

        profiles_dir = resource_path("config", "profiles")
        for pf in sorted(profiles_dir.glob("*.json")):
            with open(pf, encoding="utf-8") as f:
                profile = localize_profile(json.load(f))
            self._layout.addWidget(self._make_card(profile))

        self._layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _make_card(self, profile: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("profileCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        name = QLabel(profile.get("name", ""))
        name.setObjectName("profileName")
        layout.addWidget(name)

        desc = QLabel(profile.get("description", ""))
        desc.setWordWrap(True)
        desc.setObjectName("muted")
        layout.addWidget(desc)

        tweak_ids = dedupe_preserve_order(profile.get("tweaks", []))
        applicable, skipped = self._filter(tweak_ids)
        progress = QLabel(
            t("profile_apply_count", applicable=len(applicable), total=len(tweak_ids))
            + (
                f"  ·  {t('profile_skipped_active', n=len(skipped))}"
                if skipped
                else ""
            )
        )
        progress.setObjectName("profileProgress")
        layout.addWidget(progress)

        btn = QPushButton(
            t("profile_apply_remaining") if skipped else t("profile_apply")
        )
        btn.setObjectName("applyBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumWidth(200)
        btn.clicked.connect(lambda: self._on_apply(profile))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)
        return card
