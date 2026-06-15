
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
from core.i18n import get_language, set_language, t
from ui.theme import style_scroll_area


class SettingsPage(QWidget):

    def __init__(
        self,
        backup: BackupManager,
        *,
        on_restore_point: Callable[[], None],
        on_export_restore: Callable[[], None],
        on_reg_backup: Callable[[], None],
        on_open_backups: Callable[[], None],
        on_language_changed: Callable[[str], None] | None = None,
        on_check_update: Callable[[], None] | None = None,
        on_install_update: Callable[[], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appPage")
        self._backup = backup
        self._on_language_changed = on_language_changed
        self._on_check_update = on_check_update
        self._on_install_update = on_install_update
        self._pending_release = None

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
        self._page_title = title
        layout.addWidget(title)

        lang_card = QFrame()
        lang_card.setObjectName("settingsCard")
        lang_layout = QVBoxLayout(lang_card)
        lang_layout.setContentsMargins(20, 18, 20, 18)
        lang_layout.setSpacing(10)

        lang_title = QLabel(t("settings_language_title"))
        lang_title.setObjectName("sectionTitle")
        self._lang_title = lang_title
        lang_layout.addWidget(lang_title)

        lang_hint = QLabel(t("settings_language_hint"))
        lang_hint.setObjectName("muted")
        lang_hint.setWordWrap(True)
        self._lang_hint = lang_hint
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
        self._lang_btn = lang_btn
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

        update_card = QFrame()
        update_card.setObjectName("settingsCard")
        update_layout = QVBoxLayout(update_card)
        update_layout.setContentsMargins(20, 18, 20, 18)
        update_layout.setSpacing(10)

        update_title = QLabel(t("settings_update_title"))
        update_title.setObjectName("sectionTitle")
        self._update_title = update_title
        update_layout.addWidget(update_title)

        update_hint = QLabel(t("settings_update_hint"))
        update_hint.setObjectName("muted")
        update_hint.setWordWrap(True)
        self._update_hint = update_hint
        update_layout.addWidget(update_hint)

        self._update_status = QLabel(t("update_check_idle"))
        self._update_status.setObjectName("muted")
        self._update_status.setWordWrap(True)
        self._update_status.setOpenExternalLinks(True)
        update_layout.addWidget(self._update_status)

        update_btn = QPushButton(t("settings_update_check_btn"))
        update_btn.setObjectName("secondaryBtn")
        update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        update_btn.setMaximumWidth(360)
        update_btn.clicked.connect(self._check_update)
        self._update_btn = update_btn
        update_layout.addWidget(update_btn)

        self._install_update_btn = QPushButton(t("settings_update_install_btn"))
        self._install_update_btn.setObjectName("applyBtn")
        self._install_update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._install_update_btn.setMaximumWidth(360)
        self._install_update_btn.hide()
        self._install_update_btn.clicked.connect(self._install_update)
        update_layout.addWidget(self._install_update_btn)
        layout.addWidget(update_card)

        self.refresh_stats()

        backup_card = QFrame()
        backup_card.setObjectName("settingsCard")
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(20, 18, 20, 18)
        backup_layout.setSpacing(10)

        backup_title = QLabel(t("settings_backup_title"))
        backup_title.setObjectName("sectionTitle")
        self._backup_title = backup_title
        backup_layout.addWidget(backup_title)

        backup_hint = QLabel(t("settings_backup_hint"))
        backup_hint.setObjectName("muted")
        backup_hint.setWordWrap(True)
        self._backup_hint = backup_hint
        backup_layout.addWidget(backup_hint)

        reg_btn = QPushButton(t("settings_reg_backup_btn"))
        reg_btn.setObjectName("secondaryBtn")
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setMaximumWidth(360)
        reg_btn.clicked.connect(on_reg_backup)
        self._reg_btn = reg_btn
        backup_layout.addWidget(reg_btn)

        open_btn = QPushButton(t("settings_open_backups_btn"))
        open_btn.setObjectName("secondaryBtn")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setMaximumWidth(360)
        open_btn.clicked.connect(on_open_backups)
        self._open_backups_btn = open_btn
        backup_layout.addWidget(open_btn)

        layout.addWidget(backup_card)

        rp_btn = QPushButton(t("create_restore_point"))
        rp_btn.setObjectName("secondaryBtn")
        rp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rp_btn.setMaximumWidth(360)
        rp_btn.clicked.connect(on_restore_point)
        self._restore_point_btn = rp_btn
        layout.addWidget(rp_btn)

        exp_btn = QPushButton(t("settings_export_restore_btn"))
        exp_btn.setObjectName("secondaryBtn")
        exp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exp_btn.setMaximumWidth(360)
        exp_btn.clicked.connect(on_export_restore)
        self._export_restore_btn = exp_btn
        layout.addWidget(exp_btn)

        layout.addStretch()

        style_scroll_area(scroll, content)
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _apply_language(self) -> None:
        lang = self._lang_combo.currentData()
        if not lang or lang == get_language():
            return
        if self._on_language_changed:
            self._on_language_changed(str(lang))
            self.retranslate_ui()
            return
        set_language(str(lang))

    def retranslate_ui(self) -> None:
        self._page_title.setText(t("nav_settings"))
        self._lang_title.setText(t("settings_language_title"))
        self._lang_hint.setText(t("settings_language_hint"))
        self._lang_btn.setText(t("settings_language_apply"))
        self._backup_title.setText(t("settings_backup_title"))
        self._backup_hint.setText(t("settings_backup_hint"))
        self._reg_btn.setText(t("settings_reg_backup_btn"))
        self._open_backups_btn.setText(t("settings_open_backups_btn"))
        self._restore_point_btn.setText(t("create_restore_point"))
        self._export_restore_btn.setText(t("settings_export_restore_btn"))
        self._update_title.setText(t("settings_update_title"))
        self._update_hint.setText(t("settings_update_hint"))
        self._update_btn.setText(t("settings_update_check_btn"))
        self._install_update_btn.setText(t("settings_update_install_btn"))
        current = get_language()
        self._lang_combo.blockSignals(True)
        self._lang_combo.clear()
        self._lang_combo.addItem(t("language_ru"), "ru")
        self._lang_combo.addItem(t("language_en"), "en")
        for i in range(self._lang_combo.count()):
            if self._lang_combo.itemData(i) == current:
                self._lang_combo.setCurrentIndex(i)
                break
        self._lang_combo.blockSignals(False)
        self.refresh_stats()

    def refresh_stats(self) -> None:
        n = len(self._backup.get_all_applied())
        self._applied_lbl.setText(t("settings_applied_count", n=n))

    def _check_update(self) -> None:
        if self._on_check_update:
            self.set_update_checking(True)
            self._on_check_update()

    def set_update_checking(self, checking: bool) -> None:
        self._update_btn.setEnabled(not checking)
        if checking:
            self._update_status.setText(t("update_checking"))

    def set_update_status(self, message: str, *, url: str = "", release=None) -> None:
        self._update_btn.setEnabled(True)
        self._pending_release = release
        if release is not None:
            self._install_update_btn.show()
        else:
            self._install_update_btn.hide()
        if url:
            self._update_status.setText(f'<a href="{url}">{message}</a>')
        else:
            self._update_status.setText(message)

    def _install_update(self) -> None:
        if self._on_install_update and self._pending_release is not None:
            self._on_install_update()
