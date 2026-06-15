"""Страница твиков по категории."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.i18n import category_label, t
from core.tweak_state import TweakStatus
from tweaks.base import TweakManager
from ui.widgets.tweak_list_panel import TweakListPanel

FILTER_ALL = "all"
FILTER_AVAILABLE = "available"
FILTER_ACTIVE = "active"
FILTER_ONESHOT = "oneshot"

_FILTER_KEYS = [
    ("filter_all", FILTER_ALL),
    ("filter_available", FILTER_AVAILABLE),
    ("filter_active", FILTER_ACTIVE),
    ("filter_oneshot", FILTER_ONESHOT),
]


class TweakPage(QWidget):
    """Страница категории твиков с фильтрами и пулом строк."""

    def __init__(
        self,
        manager: TweakManager,
        category: str,
        *,
        is_compatible_fn: Callable,
        on_toggle: Callable[[str, bool], None],
        on_apply_category: Optional[Callable[[str], None]] = None,
        gpu_vendor: str = "unknown",
        is_admin: bool = True,
        search_query: str = "",
        autoload: bool = True,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appPage")
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self.manager = manager
        self.category = category
        self._is_compatible = is_compatible_fn
        self._on_toggle = on_toggle
        self._on_apply_category = on_apply_category
        self._gpu_vendor = gpu_vendor
        self._is_admin = is_admin
        self._search = search_query
        self._filter = FILTER_ALL

        outer = QVBoxLayout(self)
        outer.setSpacing(10)

        header = QLabel(category_label(category))
        header.setObjectName("pageTitle")
        outer.addWidget(header)

        filter_frame = QFrame()
        filter_frame.setObjectName("filterBar")
        filter_row = QHBoxLayout(filter_frame)
        filter_row.setContentsMargins(10, 6, 10, 6)
        filter_lbl = QLabel(t("filter_label"))
        filter_lbl.setObjectName("muted")
        filter_row.addWidget(filter_lbl)
        self._filter_combo = QComboBox()
        for label_key, _ in _FILTER_KEYS:
            self._filter_combo.addItem(t(label_key))
        self._filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._filter_combo)
        filter_row.addStretch()

        self._apply_cat_btn = QPushButton(t("apply_category_btn"))
        self._apply_cat_btn.setObjectName("applyCategoryBtn")
        self._apply_cat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if on_apply_category:
            self._apply_cat_btn.clicked.connect(lambda: on_apply_category(self.category))
        else:
            self._apply_cat_btn.setEnabled(False)
        filter_row.addWidget(self._apply_cat_btn)
        outer.addWidget(filter_frame)

        self._panel = TweakListPanel(
            manager,
            is_compatible_fn=is_compatible_fn,
            on_toggle=on_toggle,
            gpu_vendor=gpu_vendor,
            is_admin=is_admin,
            show_category=False,
        )
        outer.addWidget(self._panel, stretch=1)

        if autoload:
            self.refresh("")

    def _on_filter_changed(self, index: int) -> None:
        self._filter = _FILTER_KEYS[index][1]
        self.refresh(self._search)

    def _filtered_metas(self, search_query: str):
        if search_query:
            metas = self.manager.search(search_query)
            metas = [m for m in metas if m.category == self.category]
        else:
            metas = self.manager.get_by_category(self.category)

        if self._filter == FILTER_ALL:
            return metas

        compat_map = {m.id: self._is_compatible(m) for m in metas}
        filtered = []
        for meta in metas:
            state = self.manager.get_tweak_state(meta.id, compatible=compat_map[meta.id])
            if self._filter == FILTER_AVAILABLE:
                if state.is_active and state.status != TweakStatus.ONE_SHOT:
                    continue
            elif self._filter == FILTER_ACTIVE and not state.is_active:
                continue
            elif self._filter == FILTER_ONESHOT and state.status != TweakStatus.ONE_SHOT:
                continue
            filtered.append(meta)
        return filtered

    def _empty_message(self, search_query: str) -> str:
        if search_query:
            return t("search_no_results")
        if self._filter != FILTER_ALL:
            return t("filter_no_results")
        all_metas = self.manager.get_by_category(self.category)
        if not all_metas:
            return t("category_empty")
        compat_map = {m.id: self._is_compatible(m) for m in all_metas}
        counts = self.manager.state_detector.count_active(
            [m.id for m in all_metas],
            compat_map,
        )
        if counts["inactive"] == 0 and counts["one_shot"] == 0:
            return t("category_all_applied")
        return t("list_empty")

    def refresh(self, search_query: str = "") -> None:
        self._search = search_query
        metas = self._filtered_metas(search_query)
        title = category_label(self.category)
        empty_message = self._empty_message(search_query) if not metas else ""
        self._panel.populate(metas, summary_prefix=title, empty_message=empty_message)
