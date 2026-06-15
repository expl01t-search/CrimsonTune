"""Глобальный поиск твиков по всем категориям."""

from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.i18n import t
from tweaks.base import TweakManager
from ui.widgets.tweak_list_panel import TweakListPanel


class SearchPage(QWidget):
    """Результаты поиска из всех категорий."""

    def __init__(
        self,
        manager: TweakManager,
        *,
        is_compatible_fn: Callable,
        on_toggle: Callable[[str, bool], None],
        gpu_vendor: str = "unknown",
        is_admin: bool = True,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appPage")
        self.manager = manager
        self._is_compatible = is_compatible_fn
        self._on_toggle = on_toggle

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        self._hint = QLabel(t("search_prompt"))
        self._hint.setObjectName("pageSubtitle")
        outer.addWidget(self._hint)

        self._panel = TweakListPanel(
            manager,
            is_compatible_fn=is_compatible_fn,
            on_toggle=on_toggle,
            gpu_vendor=gpu_vendor,
            is_admin=is_admin,
            show_category=True,
        )
        outer.addWidget(self._panel, stretch=1)

    def refresh(self, query: str) -> None:
        q = query.strip()
        if not q:
            self._hint.setText(t("search_prompt"))
            self._panel.populate([], summary_prefix="", empty_message="")
            return

        metas = self.manager.search(q)
        if not metas:
            self._hint.setText(t("search_no_results_query", q=q))
            self._panel.populate(
                [],
                summary_prefix=f"«{q}»",
                empty_message=t("search_no_results"),
            )
            return

        self._hint.setText(t("search_found_count", n=len(metas), q=q))
        self._panel.populate(metas, summary_prefix=f"«{q}»")
        self._panel.scroll_to_top()
