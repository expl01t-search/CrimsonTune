"""Минималистичная строка твика."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from core.i18n import category_label, t
from core.tweak_state import TweakStateInfo, TweakStatus
from tweaks.base import TweakMeta
from ui.components.forge_toggle import ForgeToggle, MODE_ACTIVE, MODE_DISABLED, MODE_OFF, MODE_SELECTED
from ui.components.status_badge import StatusBadge


class TweakRow(QFrame):
    """Строка твика: toggle отражает реальное состояние."""

    def __init__(
        self,
        meta: TweakMeta,
        state: TweakStateInfo,
        *,
        on_toggle: Optional[Callable[[str, bool], None]] = None,
        show_category: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.meta = meta
        self.state = state
        self._on_toggle = on_toggle
        self._selected = False
        self.setObjectName("tweakRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._build_ui(show_category)
        self.apply_state(state, animate_toggle=False)

    def _build_ui(self, show_category: bool) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(10)

        self._toggle = ForgeToggle(checked=False, enabled=True)
        self._toggle.toggled.connect(self._on_switch)
        root.addWidget(self._toggle, alignment=Qt.AlignmentFlag.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        self._name = QLabel(self.meta.name)
        self._name.setObjectName("tweakName")
        self._name.setToolTip(self.meta.description or self.meta.name)
        self._name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_row.addWidget(self._name, stretch=1)
        if show_category:
            chip = QLabel(category_label(self.meta.category))
            chip.setObjectName("categoryChip")
            title_row.addWidget(chip, alignment=Qt.AlignmentFlag.AlignVCenter)
        text_col.addLayout(title_row)

        self._desc = QLabel(self.meta.description)
        self._desc.setObjectName("tweakDesc")
        self._desc.setWordWrap(True)
        self._desc.setMaximumHeight(32)
        text_col.addWidget(self._desc)
        root.addLayout(text_col, stretch=1)

        self._badge = StatusBadge(self.state.status, self.state.detail or "")
        self._badge.setMinimumWidth(120)
        root.addWidget(self._badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._hint_btn = QPushButton("?")
        self._hint_btn.setObjectName("hintBtn")
        self._hint_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hint_btn.setToolTip(t("tweak_hint_tooltip"))
        self._hint_btn.clicked.connect(self._open_hint)
        root.addWidget(self._hint_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _sync_row_style(self) -> None:
        active = self.state.is_active
        selected = self._selected and not active
        self.setProperty("active", "true" if active else "false")
        self.setProperty("selected", "true" if selected else "false")
        self._name.setProperty("activeName", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._name.style().unpolish(self._name)
        self._name.style().polish(self._name)

    def apply_state(self, state: TweakStateInfo, *, animate_toggle: bool = False) -> None:
        self.state = state
        active = state.is_active

        self._sync_row_style()

        self._badge.update_status(state.status, state.detail or "")

        self._toggle.blockSignals(True)
        if state.status == TweakStatus.INCOMPATIBLE:
            self.setProperty("incompatible", "true")
            self._toggle.set_visual_mode(MODE_DISABLED)
            self._toggle.setChecked(False, animate=animate_toggle)
            self._toggle.setEnabled(False)
            self._toggle.setLocked(True)
            self._selected = False
        else:
            self.setProperty("incompatible", "false")
            if active:
                self._toggle.set_visual_mode(MODE_ACTIVE)
                self._toggle.setChecked(True, animate=animate_toggle)
                self._toggle.setEnabled(False)
                self._toggle.setLocked(True)
                self._selected = False
            elif state.status == TweakStatus.ONE_SHOT:
                self._toggle.setLocked(False)
                self._toggle.setEnabled(True)
                self._toggle.set_visual_mode(MODE_SELECTED if self._selected else MODE_OFF)
                self._toggle.setChecked(self._selected, animate=animate_toggle)
            else:
                self._toggle.setLocked(False)
                self._toggle.setEnabled(state.can_apply)
                mode = MODE_SELECTED if self._selected else MODE_OFF
                if not state.can_apply:
                    mode = MODE_DISABLED
                self._toggle.set_visual_mode(mode)
                self._toggle.setChecked(self._selected, animate=animate_toggle and not self._selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self._toggle.blockSignals(False)

    def _on_switch(self, checked: bool) -> None:
        if self.state.status == TweakStatus.INCOMPATIBLE:
            self._toggle.blockSignals(True)
            self._toggle.setChecked(False, animate=False)
            self._toggle.blockSignals(False)
            return
        if self.state.is_active or self._toggle.isLocked():
            self._toggle.blockSignals(True)
            self._toggle.setChecked(self.state.is_active, animate=False)
            self._toggle.blockSignals(False)
            return
        self._selected = checked
        self._toggle.set_visual_mode(MODE_SELECTED if checked else MODE_OFF)
        self._sync_row_style()
        if self._on_toggle:
            self._on_toggle(self.meta.id, checked)

    def is_selected(self) -> bool:
        return (
            self._selected
            and self._toggle.isEnabled()
            and not self.state.is_active
            and self.state.status != TweakStatus.INCOMPATIBLE
        )

    def set_selected(self, value: bool) -> None:
        if self.state.is_active or self.state.status == TweakStatus.INCOMPATIBLE:
            return
        if self._toggle.isEnabled():
            self._toggle.blockSignals(True)
            self._toggle.setChecked(value, animate=False)
            self._toggle.blockSignals(False)
            self._selected = value
            self._sync_row_style()

    def _open_hint(self) -> None:
        from ui.components.hint_dialog import show_hint

        show_hint(self, self.meta)
