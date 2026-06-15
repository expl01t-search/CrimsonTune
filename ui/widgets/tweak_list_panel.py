
from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from core.i18n import t
from tweaks.base import TweakManager, TweakMeta
from ui.components.tweak_row import TweakRow
from ui.performance import batch_widget_update
from ui.theme import style_scroll_area
from utils.tweak_state_ui import build_admin_blocked_state, build_incompatible_state, enrich_state_for_display

_BATCH_SIZE = 24
_BATCH_THRESHOLD = 36


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
        self._batch_token = 0
        self._batch_pending: list[TweakMeta] = []
        self._batch_compat: dict[str, bool] = {}
        self._batch_states: dict = {}
        self._batch_summary_prefix = ""
        self._batch_index = 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        self._summary = QLabel("")
        self._summary.setObjectName("muted")
        outer.addWidget(self._summary)

        self._loading = QLabel("")
        self._loading.setObjectName("loadingState")
        self._loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading.hide()

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

    def _cancel_batch(self) -> None:
        self._batch_token += 1
        self._batch_pending.clear()
        self._loading.hide()

    def populate(
        self,
        metas: Iterable[TweakMeta],
        *,
        summary_prefix: str = "",
        empty_message: str = "",
        reload_applied: bool = False,
    ) -> None:
        if reload_applied:
            self.manager.refresh_states()
        meta_list = list(metas)
        self._cancel_batch()
        if len(meta_list) >= _BATCH_THRESHOLD:
            self._start_batched_populate(meta_list, summary_prefix=summary_prefix, empty_message=empty_message)
            return
        self.setUpdatesEnabled(False)
        try:
            self._populate_impl(meta_list, summary_prefix=summary_prefix, empty_message=empty_message)
        finally:
            self.setUpdatesEnabled(True)

    def _start_batched_populate(
        self,
        meta_list: list[TweakMeta],
        *,
        summary_prefix: str,
        empty_message: str,
    ) -> None:
        if not meta_list:
            self._populate_impl([], summary_prefix=summary_prefix, empty_message=empty_message)
            return

        self._batch_token += 1
        token = self._batch_token
        self._batch_pending = meta_list
        self._batch_compat = {m.id: self._is_compatible(m) for m in meta_list}
        self._batch_states = {}
        self._batch_summary_prefix = summary_prefix
        self._batch_index = 0

        self._empty.hide()
        self._loading.setText(t("list_loading"))
        self._loading.show()
        if self._list.indexOf(self._loading) < 0:
            self._list.addWidget(self._loading)

        while self._list.count():
            item = self._list.takeAt(0)
            if item.widget() and item.widget() not in (self._loading, self._empty):
                item.widget().deleteLater()
        self._rows.clear()
        self._order.clear()

        prefix = f"{summary_prefix}  ·  " if summary_prefix else ""
        self._summary.setText(prefix + t("list_loading"))
        QTimer.singleShot(0, lambda: self._run_batch_step(token))

    def _run_batch_step(self, token: int) -> None:
        if token != self._batch_token:
            return

        start = self._batch_index
        end = min(start + _BATCH_SIZE, len(self._batch_pending))
        chunk = self._batch_pending[start:end]
        chunk_compat = {m.id: self._batch_compat[m.id] for m in chunk}
        chunk_states = self.manager.state_detector.get_all_states(
            [m.id for m in chunk],
            chunk_compat,
        )
        self._batch_states.update(chunk_states)

        self._container.setUpdatesEnabled(False)
        try:
            if self._loading.isVisible() and self._list.indexOf(self._loading) >= 0:
                self._list.removeWidget(self._loading)
                self._loading.hide()

            for meta in chunk:
                state = self._resolve_row_state(meta, chunk_states)
                row = TweakRow(
                    meta,
                    state,
                    on_toggle=self._on_toggle,
                    show_category=self._show_category,
                )
                self._rows[meta.id] = row
                self._list.addWidget(row)
        finally:
            self._container.setUpdatesEnabled(True)

        self._batch_index = end
        if end < len(self._batch_pending):
            QTimer.singleShot(0, lambda: self._run_batch_step(token))
            return

        self._order = [m.id for m in self._batch_pending]
        counts = self.manager.state_detector.count_active(
            self._order,
            self._batch_compat,
        )
        prefix = f"{self._batch_summary_prefix}  ·  " if self._batch_summary_prefix else ""
        self._summary.setText(
            t(
                "list_summary",
                prefix=prefix,
                active=counts["active"],
                inactive=counts["inactive"],
                oneshot=counts["one_shot"],
            )
        )
        self._scroll.verticalScrollBar().setValue(0)
        self._batch_pending.clear()

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
            self._loading.hide()
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
        self._loading.hide()
        if self._list.indexOf(self._empty) >= 0:
            self._list.removeWidget(self._empty)
        if self._list.indexOf(self._loading) >= 0:
            self._list.removeWidget(self._loading)

        compat_map = {m.id: self._is_compatible(m) for m in meta_list}
        ids = [m.id for m in meta_list]
        states = self.manager.state_detector.get_all_states(ids, compat_map)

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
                if meta.id in self._rows:
                    self._rows[meta.id].update_meta(meta)
                    self._rows[meta.id].apply_state(
                        self._resolve_row_state(meta, states),
                        animate_toggle=False,
                    )
                else:
                    row = TweakRow(
                        meta,
                        self._resolve_row_state(meta, states),
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

    def _resolve_row_state(self, meta: TweakMeta, states: dict) -> TweakStateInfo:
        compatible = self._is_compatible(meta)
        if not compatible:
            return build_incompatible_state(meta, self._gpu_vendor)
        if not self._is_admin and meta.requires_admin and not self.manager.backup.is_applied(meta.id):
            return build_admin_blocked_state(meta)
        return enrich_state_for_display(states[meta.id], meta)

    def refresh_visible_states(self) -> None:
        if not self._rows:
            return
        self.manager.refresh_states()
        ids = list(self._order)
        self.manager.state_detector.invalidate(ids)
        compat_map = {tid: self._is_compatible(m) for tid in ids if (m := self.manager.get_meta(tid))}
        states = self.manager.state_detector.get_all_states(ids, compat_map)
        for tid in ids:
            row = self._rows.get(tid)
            meta = self.manager.get_meta(tid)
            if not row or not meta:
                continue
            row.apply_state(self._resolve_row_state(meta, states), animate_toggle=True)
        counts = self.manager.state_detector.count_active(ids, compat_map)
        prefix_parts = self._summary.text().split("  ·  ", 1)
        prefix = prefix_parts[0] + "  ·  " if len(prefix_parts) > 1 and prefix_parts[0] else ""
        self._summary.setText(
            t(
                "list_summary",
                prefix=prefix,
                active=counts["active"],
                inactive=counts["inactive"],
                oneshot=counts["one_shot"],
            )
        )
