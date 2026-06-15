"""Страница настроек."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.backup import BackupManager
from core.brand import APP_NAME, APP_VERSION
from core.i18n import get_language, restart_application, save_language, t
from ui.theme import style_scroll_area


class SettingsPage(QWidget):
    """Настройки приложения."""

    def __init__(
        self,
        backup: BackupManager,
        *,
        on_restore_point: Callable[[], None],
        on_export_restore: Callable[[], None],
        on_reg_backup: Callable[[], None],
        on_open_backups: Callable[[], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appPage")
        self._backup = backup

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("settingsContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(14)

        title = QLabel(t("nav_settings"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        lang_card = QFrame()
        lang_card.setObjectName("settingsCard")
        lang_layout = QVBoxLayout(lang_card)
        lang_layout.setContentsMargins(20, 18, 20, 18)
        lang_layout.setSpacing(10)

        lang_title = QLabel(t("settings_language_title"))
        lang_title.setObjectName("sectionTitle")
        lang_layout.addWidget(lang_title)

        lang_hint = QLabel(t("settings_language_hint"))
        lang_hint.setObjectName("muted")
        lang_hint.setWordWrap(True)
        lang_layout.addWidget(lang_hint)

        self._lang_combo = QComboBox()
        self._lang_combo.setObjectName("langCombo")
        self._lang_combo.setMinimumWidth(260)
        self._lang_combo.setMinimumHeight(34)
        self._lang_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._lang_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._lang_combo.addItem(t("language_ru"), "ru")
        self._lang_combo.addItem(t("language_en"), "en")
        current = get_language()
        for i in range(self._lang_combo.count()):
            if self._lang_combo.itemData(i) == current:
                self._lang_combo.setCurrentIndex(i)
                break
        lang_layout.addWidget(self._lang_combo)

        lang_btn = QPushButton(t("settings_language_apply"))
        lang_btn.setObjectName("secondaryBtn")
        lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        lang_btn.setMaximumWidth(360)
        lang_btn.clicked.connect(self._apply_language)
        lang_layout.addWidget(lang_btn)
        layout.addWidget(lang_card)

        info_card = QFrame()
        info_card.setObjectName("settingsCard")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 18, 20, 18)
        info_layout.setSpacing(8)

        self._applied_lbl = QLabel()
        self._applied_lbl.setObjectName("sectionTitle")
        info_layout.addWidget(self._applied_lbl)

        ver = QLabel(f"{APP_NAME} v{APP_VERSION}")
        ver.setObjectName("muted")
        info_layout.addWidget(ver)
        layout.addWidget(info_card)
        self.refresh_stats()

        backup_card = QFrame()
        backup_card.setObjectName("settingsCard")
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(20, 18, 20, 18)
        backup_layout.setSpacing(10)

        backup_title = QLabel(t("settings_backup_title"))
        backup_title.setObjectName("sectionTitle")
        backup_layout.addWidget(backup_title)

        backup_hint = QLabel(t("settings_backup_hint"))
        backup_hint.setObjectName("muted")
        backup_hint.setWordWrap(True)
        backup_layout.addWidget(backup_hint)

        reg_btn = QPushButton(t("settings_reg_backup_btn"))
        reg_btn.setObjectName("secondaryBtn")
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setMaximumWidth(360)
        reg_btn.clicked.connect(on_reg_backup)
        backup_layout.addWidget(reg_btn)

        open_btn = QPushButton(t("settings_open_backups_btn"))
        open_btn.setObjectName("secondaryBtn")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setMaximumWidth(360)
        open_btn.clicked.connect(on_open_backups)
        backup_layout.addWidget(open_btn)

        layout.addWidget(backup_card)

        rp_btn = QPushButton(t("create_restore_point"))
        rp_btn.setObjectName("secondaryBtn")
        rp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rp_btn.setMaximumWidth(360)
        rp_btn.clicked.connect(on_restore_point)
        layout.addWidget(rp_btn)

        exp_btn = QPushButton(t("settings_export_restore_btn"))
        exp_btn.setObjectName("secondaryBtn")
        exp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exp_btn.setMaximumWidth(360)
        exp_btn.clicked.connect(on_export_restore)
        layout.addWidget(exp_btn)

        layout.addStretch()

        style_scroll_area(scroll, content)
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _apply_language(self) -> None:
        lang = self._lang_combo.currentData()
        if not lang or lang == get_language():
            return
        save_language(str(lang))
        restart_application()

    def refresh_stats(self) -> None:
        n = len(self._backup.get_all_applied())
        self._applied_lbl.setText(t("settings_applied_count", n=n))
