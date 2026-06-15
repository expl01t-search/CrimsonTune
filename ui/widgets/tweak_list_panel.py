
from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from core.i18n import category_label, t
from tweaks.base import TweakManager, TweakMeta
from ui.components.tweak_row import TweakRow
from ui.performance import batch_widget_update
from ui.theme import style_scroll_area
from utils.tweak_state_ui import build_admin_blocked_state, build_incompatible_state


class TweakListPanel(QWidget):

    def __init__(
        self,
        manager: TweakManager,
        *,
        is_compatible_fn: Callable,
        on_toggle: Callable[[str, bool], None],
        gpu_vendor: str = "unknown",
        is_admin: bool = True,
        show_category: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("listPanelHost")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.manager = manager
        self._is_compatible = is_compatible_fn
        self._on_toggle = on_toggle
        self._gpu_vendor = gpu_vendor
        self._is_admin = is_admin
        self._show_category = show_category
        self._rows: dict[str, TweakRow] = {}
        self._order: list[str] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        self._summary = QLabel("")
        self._summary.setObjectName("muted")
        outer.addWidget(self._summary)

        self._empty = QLabel("")
        self._empty.setObjectName("emptyState")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.hide()

        panel = QFrame()
        panel.setObjectName("listPanel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(8, 8, 8, 8)
        panel_layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._container = QWidget()
        self._list = QVBoxLayout(self._container)
        self._list.setSpacing(4)
        self._list.setContentsMargins(0, 0, 0, 0)
        self._list.setAlignment(Qt.AlignmentFlag.AlignTop)
        style_scroll_area(self._scroll, self._container)
        self._scroll.setWidget(self._container)
        panel_layout.addWidget(self._scroll)
        outer.addWidget(panel, stretch=1)

    def populate(
        self,
        metas: Iterable[TweakMeta],
        *,
        summary_prefix: str = "",
        empty_message: str = "",
    ) -> None:
        meta_list = list(metas)
        self.setUpdatesEnabled(False)
        try:
            self._populate_impl(meta_list, summary_prefix=summary_prefix, empty_message=empty_message)
        finally:
            self.setUpdatesEnabled(True)

    def _populate_impl(
        self,
        meta_list: list[TweakMeta],
        *,
        summary_prefix: str = "",
        empty_message: str = "",
    ) -> None:
        if not meta_list:
            self._summary.setText(summary_prefix or "")
            self._empty.setText(empty_message or t("list_empty"))
            self._empty.show()
            while self._list.count():
                item = self._list.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self._rows.clear()
            self._order.clear()
            if self._list.indexOf(self._empty) < 0:
                self._list.addWidget(self._empty)
            self._container.adjustSize()
            return

        self._empty.hide()
        if self._list.indexOf(self._empty) >= 0:
            self._list.removeWidget(self._empty)

        compat_map = {m.id: self._is_compatible(m) for m in meta_list}
        ids = [m.id for m in meta_list]

        def _update() -> None:
            counts = self.manager.state_detector.count_active(ids, compat_map)
            prefix = f"{summary_prefix}  ·  " if summary_prefix else ""
            self._summary.setText(
                t(
                    "list_summary",
                    prefix=prefix,
                    active=counts["active"],
                    inactive=counts["inactive"],
                    oneshot=counts["one_shot"],
                )
            )

            new_order = [m.id for m in meta_list]
            new_set = set(new_order)

            for tid in list(self._rows):
                if tid not in new_set:
                    row = self._rows.pop(tid)
                    self._list.removeWidget(row)
                    row.deleteLater()

            for meta in meta_list:
                compatible = compat_map[meta.id]
                if not compatible:
                    state = build_incompatible_state(meta, self._gpu_vendor)
                elif not self._is_admin and meta.requires_admin:
                    state = build_admin_blocked_state(meta)
                else:
                    state = self.manager.get_tweak_state(meta.id, compatible=True)
                if meta.id in self._rows:
                    self._rows[meta.id].update_meta(meta)
                    self._rows[meta.id].apply_state(state, animate_toggle=False)
                else:
                    row = TweakRow(
                        meta,
                        state,
                        on_toggle=self._on_toggle,
                        show_category=self._show_category,
                    )
                    self._rows[meta.id] = row

            while self._list.count():
                self._list.takeAt(0)
            for tid in new_order:
                self._list.addWidget(self._rows[tid])
            self._order = new_order

        batch_widget_update(self._container, _update, repaint=False)
        self._scroll.verticalScrollBar().setValue(0)

    def scroll_to_top(self) -> None:
        self._scroll.verticalScrollBar().setValue(0)
