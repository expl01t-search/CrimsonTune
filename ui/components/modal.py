
from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.i18n import t
from ui.theme import style_scroll_area
from ui.window_utils import place_modal


class ConfirmModal(QDialog):

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        confirm_text: str | None = None,
        cancel_text: str | None = None,
    ) -> None:
        super().__init__(parent)
        confirm_text = confirm_text or t("btn_confirm")
        cancel_text = cancel_text or t("btn_cancel")
        self.setObjectName("confirmDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._on_confirm = on_confirm
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("modalTitle")
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setObjectName("modalMessage")
        layout.addWidget(msg_lbl)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setObjectName("applyBtn")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self._confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

    def showEvent(self, event) -> None:
        place_modal(self, self.parentWidget())
        super().showEvent(event)

    def _confirm(self) -> None:
        self._on_confirm()
        self.accept()


class ApplyConfirmModal(QDialog):

    def __init__(
        self,
        parent,
        title: str,
        *,
        tweak_names: Iterable[str],
        notes: Iterable[str] = (),
        on_confirm: Callable[[], None],
        confirm_text: str | None = None,
        cancel_text: str | None = None,
    ) -> None:
        super().__init__(parent)
        confirm_text = confirm_text or t("btn_confirm")
        cancel_text = cancel_text or t("btn_cancel")
        self.setObjectName("applyConfirmDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        names = list(tweak_names)
        note_lines = [n.strip() for n in notes if n and n.strip()]
        self._on_confirm = on_confirm

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("modalTitle")
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        summary = QLabel(t("apply_summary", n=len(names)))
        summary.setObjectName("modalSummary")
        layout.addWidget(summary)

        list_panel = QFrame()
        list_panel.setObjectName("modalListPanel")
        list_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        panel_layout = QVBoxLayout(list_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        container = QWidget()
        list_layout = QVBoxLayout(container)
        list_layout.setContentsMargins(2, 2, 2, 2)
        list_layout.setSpacing(4)
        list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for index, name in enumerate(names, start=1):
            item = QLabel(f"{index}. {name}")
            item.setObjectName("modalListItem")
            item.setWordWrap(True)
            item.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            list_layout.addWidget(item)

        style_scroll_area(scroll, container)
        scroll.setWidget(container)
        panel_layout.addWidget(scroll)
        layout.addWidget(list_panel, stretch=1)

        if note_lines:
            notes_panel = QFrame()
            notes_panel.setObjectName("modalNotesPanel")
            notes_layout = QVBoxLayout(notes_panel)
            notes_layout.setContentsMargins(10, 8, 10, 8)
            notes_layout.setSpacing(4)

            notes_title = QLabel(t("modal_notes_title"))
            notes_title.setObjectName("modalNotesTitle")
            notes_layout.addWidget(notes_title)

            notes_scroll = QScrollArea()
            notes_scroll.setWidgetResizable(True)
            notes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            notes_scroll.setMaximumHeight(120)

            notes_container = QWidget()
            notes_body = QVBoxLayout(notes_container)
            notes_body.setContentsMargins(0, 0, 0, 0)
            notes_body.setSpacing(6)

            for note in note_lines:
                note_lbl = QLabel(note)
                note_lbl.setWordWrap(True)
                note_lbl.setObjectName("modalNote")
                note_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                notes_body.addWidget(note_lbl)

            style_scroll_area(notes_scroll, notes_container)
            notes_scroll.setWidget(notes_container)
            notes_layout.addWidget(notes_scroll)
            layout.addWidget(notes_panel)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setMinimumWidth(110)
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setObjectName("applyBtn")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setMinimumWidth(130)
        confirm_btn.clicked.connect(self._confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

    def showEvent(self, event) -> None:
        place_modal(self, self.parentWidget())
        super().showEvent(event)

    def _confirm(self) -> None:
        self._on_confirm()
        self.accept()
