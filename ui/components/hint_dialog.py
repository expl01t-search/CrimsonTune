"""Компактный диалог подсказки в тёмной теме."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.i18n import t
from tweaks.base import TweakMeta
from utils.tweak_hints import build_display_hint


class HintDialog(QDialog):
    """Подсказка к твику — без системного белого QMessageBox."""

    def __init__(self, parent, meta: TweakMeta) -> None:
        super().__init__(parent)
        self.setObjectName("hintDialog")
        self.setWindowTitle(t("hint_title"))
        self.setModal(True)
        self.setMinimumWidth(360)
        self.setMaximumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(10)
        icon = QLabel("?")
        icon.setObjectName("hintDialogIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel(meta.name)
        title.setObjectName("modalTitle")
        subtitle = QLabel(t("hint_subtitle"))
        subtitle.setObjectName("muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addWidget(icon, alignment=Qt.AlignmentFlag.AlignTop)
        header.addLayout(title_box, stretch=1)
        layout.addLayout(header)

        body = QLabel(build_display_hint(meta))
        body.setObjectName("hintDialogBody")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(body)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton(t("btn_got_it"))
        ok_btn.setObjectName("applyBtn")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setMinimumWidth(110)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)


def show_hint(parent: QWidget, meta: TweakMeta) -> None:
    HintDialog(parent, meta).exec()
