
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.backup import BackupManager
from core.paths import resource_path
from core.brand import APP_NAME
from core.i18n import category_label, t
from core.detector import detect_system
from core.tweak_state import TweakStatus
from tweaks.base import TweakManager
from ui.components.modal import ApplyConfirmModal, ConfirmModal
from ui.components.onboarding import WelcomeOverlay, is_onboarding_done
from ui.components.progress_overlay import ProgressOverlay
from ui.components.toast import ToastManager
from ui.dashboard import DashboardPage
from ui.performance import UiDebouncer
from ui.profiles_page import ProfilesPage
from ui.search_page import SearchPage
from ui.settings_page import SettingsPage
from ui.sidebar import Sidebar
from ui.theme import icon_path
from ui.tweak_page import TweakPage
from ui.widgets.animated_stack import AnimatedPageStack
from ui.workers import RevertWorker, RestorePointWorker, ScanWorker
from utils.categories import CATEGORY_MAP, nav_categories
from utils.compatibility import is_tweak_compatible
from utils.tweak_ids import dedupe_preserve_order


class ApplyWorker(QThread):
    progress = Signal(int, int, str)
    finished_apply = Signal(int, int, int)

    def __init__(self, manager: TweakManager, tweak_ids: list[str]) -> None:
        super().__init__()
        self.manager = manager
        self.tweak_ids = tweak_ids

    def run(self) -> None:
        ok, fail = 0, 0
        total = len(self.tweak_ids)
        for i, tid in enumerate(self.tweak_ids):
            meta = self.manager.get_meta(tid)
            name = meta.name if meta else tid
            self.progress.emit(i + 1, total, name)
            result = self.manager.apply_tweak(tid)
            if result.success:
                ok += 1
            else:
                fail += 1
        self.finished_apply.emit(ok, fail, total)


class MainWindow(QMainWindow):

    def __init__(self, manager: TweakManager) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self.manager = manager
        self.system_info = detect_system()
        self.backup = BackupManager()
        self._selected: set[str] = set()
        self._current_page = "dashboard"
        self._page_before_search = "dashboard"
        self._tweak_pages: dict[str, TweakPage] = {}
        self._workers: list[QThread] = []
        self._tweak_count = len(manager.get_all_meta())
        self._search_debouncer = UiDebouncer(280, self)

        self.setWindowTitle(f"{APP_NAME} — {t('app_subtitle')}")
        ico = icon_path()
        if ico.exists():
            self.setWindowIcon(QIcon(str(ico)))

        from ui.window_utils import place_main_window

        place_main_window(self)

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        self._root_layout = root

        shell = QFrame()
        shell.setObjectName("appShell")
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self._sidebar = Sidebar(
            on_navigate=self.show_page,
            tweak_count=self._tweak_count,
        )
        shell_layout.addWidget(self._sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(18, 16, 18, 16)
        right.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        top = QHBoxLayout(toolbar)
        top.setContentsMargins(12, 10, 12, 10)
        top.setSpacing(10)

        self._search = QLineEdit()
        self._search.setObjectName("searchBar")
        self._search.setPlaceholderText(t("search_placeholder"))
        self._search.setMinimumWidth(150)
        self._search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._search.textChanged.connect(self._on_search)
        top.addWidget(self._search, stretch=2)

        self._selected_badge = QLabel(t("selected_count", n=0))
        self._selected_badge.setObjectName("selectedBadge")
        self._selected_badge.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        top.addWidget(self._selected_badge)

        self._scan_btn = QPushButton(t("rescan"))
        self._scan_btn.setObjectName("secondaryBtn")
        self._scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._scan_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self._scan_btn.clicked.connect(self._rescan)
        top.addWidget(self._scan_btn)

        self._revert_btn = QPushButton(t("revert_all"))
        self._revert_btn.setObjectName("dangerBtn")
        self._revert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._revert_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self._revert_btn.clicked.connect(self._revert_all)
        top.addWidget(self._revert_btn)

        self._apply_btn = QPushButton(t("apply_selected"))
        self._apply_btn.setObjectName("applyBtn")
        self._apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self._apply_btn.clicked.connect(self._apply_selected)
        top.addWidget(self._apply_btn)

        right.addWidget(toolbar)

        content = QFrame()
        content.setObjectName("contentPanel")
        content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        content.setAutoFillBackground(True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._stack = AnimatedPageStack()
        self._stack.setObjectName("pageStack")
        self._stack.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._stack.setAutoFillBackground(True)
        self._pages: dict[str, QWidget] = {}

        self._pages["dashboard"] = DashboardPage(
            self.system_info,
            manager,
            is_compatible_fn=self._is_compatible,
            on_quick_action=self._quick_action,
            tweak_count=self._tweak_count,
            applied_count=len(self.backup.get_all_applied()),
        )
        self._stack.addWidget(self._pages["dashboard"])

        self._search_page = SearchPage(
            manager,
            is_compatible_fn=self._is_compatible,
            on_toggle=self._on_toggle,
            gpu_vendor=self.system_info.gpu_vendor,
            is_admin=self.system_info.is_admin,
        )
        self._pages["search"] = self._search_page
        self._stack.addWidget(self._search_page)

        self._pages["profiles"] = ProfilesPage(
            manager,
            filter_fn=self._filter_tweaks,
            on_apply=self._apply_profile,
        )
        self._stack.addWidget(self._pages["profiles"])

        self._pages["settings"] = SettingsPage(
            self.backup,
            on_restore_point=self._create_restore_point,
            on_export_restore=self._export_restore,
            on_reg_backup=self._export_reg_baseline,
            on_open_backups=self._open_backups_folder,
            on_language_changed=self.apply_language,
        )
        self._stack.addWidget(self._pages["settings"])

        right.addWidget(content)
        content_layout.addWidget(self._stack)
        shell_layout.addLayout(right, stretch=1)
        root.addWidget(shell, stretch=1)

        self._toast = ToastManager(self)
        self._overlay = ProgressOverlay(central)
        self._onboarding = WelcomeOverlay(central)
        self._apply_worker: Optional[ApplyWorker] = None

        self._stack.page_shown.connect(self._on_page_shown)
        self._stack.setCurrentWidget(self._pages["dashboard"])
        self._current_page = "dashboard"
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, False)
        QTimer.singleShot(250, self._maybe_show_onboarding)

    def _ensure_tweak_page(self, key: str) -> TweakPage:
        if key in self._tweak_pages:
            return self._tweak_pages[key]
        cats = nav_categories(key)
        page = TweakPage(
            self.manager,
            key,
            categories=cats,
            is_compatible_fn=self._is_compatible,
            on_toggle=self._on_toggle,
            on_apply_category=self._apply_category,
            gpu_vendor=self.system_info.gpu_vendor,
            is_admin=self.system_info.is_admin,
            autoload=False,
        )
        self._tweak_pages[key] = page
        self._pages[key] = page
        self._stack.addWidget(page)
        page.refresh("")
        return page

    def _prune_selected(self) -> None:
        drop: set[str] = set()
        for tid in self._selected:
            meta = self.manager.get_meta(tid)
            if not meta or not self._is_compatible(meta):
                drop.add(tid)
            elif meta.requires_admin and not self.system_info.is_admin:
                drop.add(tid)
        if drop:
            self._selected -= drop
            self._update_selected_badge()

    def _maybe_show_onboarding(self) -> None:
        if not is_onboarding_done():
            self._onboarding.show_overlay()

    def apply_language(self, lang: str) -> None:
        from core.i18n import set_language
        from PySide6.QtWidgets import QApplication

        set_language(lang)
        self.manager.reload_translations()

        ico = icon_path()
        if ico.exists():
            qicon = QIcon(str(ico))
            app = QApplication.instance()
            if app:
                app.setWindowIcon(qicon)
            self.setWindowIcon(qicon)

        self.setWindowTitle(f"{APP_NAME} — {t('app_subtitle')}")
        self._sidebar.retranslate_ui(tweak_count=self._tweak_count)
        self._search.setPlaceholderText(t("search_placeholder"))
        if self._scan_btn.isEnabled():
            self._scan_btn.setText(t("rescan"))
        else:
            self._scan_btn.setText(t("scanning"))
        self._revert_btn.setText(t("revert_all"))
        self._apply_btn.setText(t("apply_selected"))
        self._update_selected_badge()

        if hasattr(self._overlay, "retranslate_ui"):
            self._overlay.retranslate_ui()
        if hasattr(self._onboarding, "retranslate_ui") and self._onboarding.isVisible():
            self._onboarding.retranslate_ui()

        dashboard = self._pages.get("dashboard")
        if hasattr(dashboard, "retranslate_ui"):
            dashboard.retranslate_ui()

        profiles = self._pages.get("profiles")
        if hasattr(profiles, "retranslate_ui"):
            profiles.retranslate_ui()

        if self._current_page in self._tweak_pages:
            page = self._tweak_pages[self._current_page]
            if hasattr(page, "retranslate_ui"):
                page.retranslate_ui()
        elif self._current_page == "search" and hasattr(self._search_page, "retranslate_ui"):
            self._search_page.retranslate_ui(self._search.text())

        settings = self._pages.get("settings")
        if hasattr(settings, "retranslate_ui"):
            settings.retranslate_ui()

    def _update_dashboard_status(self) -> None:
        dashboard = self._pages.get("dashboard")
        if hasattr(dashboard, "update_status"):
            dashboard.update_status(
                applied_count=len(self.backup.get_all_applied()),
                manager=self.manager,
            )

    def _on_page_shown(self, widget: QWidget) -> None:
        for key, page in self._pages.items():
            if page is widget:
                self._current_page = key
                break

    def show_page(self, key: str) -> None:
        if key == "search":
            return
        if key in CATEGORY_MAP:
            page = self._ensure_tweak_page(key)
        elif key not in self._pages:
            return
        else:
            page = self._pages[key]
        if self._search.text().strip():
            self._search.clear()
        self._current_page = key
        page.updateGeometry()
        self._stack.set_current_animated(page)
        self._sidebar.set_active(key)

    def _is_compatible(self, meta) -> bool:
        if not meta:
            return False
        return is_tweak_compatible(
            meta,
            os_build=self.system_info.os_build,
            gpu_vendor=self.system_info.gpu_vendor,
            ram_total_gb=self.system_info.ram_total_gb,
        )

    def _update_selected_badge(self) -> None:
        n = len(self._selected)
        self._selected_badge.setText(t("selected_count", n=n))
        self._selected_badge.setVisible(n > 0)

    def _on_toggle(self, tweak_id: str, selected: bool) -> None:
        meta = self.manager.get_meta(tweak_id)
        compatible = self._is_compatible(meta) if meta else False
        state = self.manager.get_tweak_state(tweak_id, compatible=compatible)
        if state.status == TweakStatus.INCOMPATIBLE:
            self._toast.show(
                state.detail or t("incompatible_tweak"),
                "warning",
            )
            return
        if meta and meta.requires_admin and not self.system_info.is_admin:
            return
        if state.is_active and selected:
            self._toast.show(t("already_active"), "info")
            return
        if selected:
            self._selected.add(tweak_id)
        else:
            self._selected.discard(tweak_id)
        self._update_selected_badge()

    def _on_search(self, text: str) -> None:
        self._search_debouncer.trigger(lambda: self._do_search(text))

    def _do_search(self, text: str) -> None:
        q = text.strip()
        if q:
            if self._current_page != "search":
                self._page_before_search = self._current_page
            self._search_page.refresh(q)
            self._current_page = "search"
            self._stack.set_current_animated(self._search_page)
        elif self._current_page == "search":
            self.show_page(self._page_before_search)
        elif self._current_page in CATEGORY_MAP:
            self._ensure_tweak_page(self._current_page).refresh("")

    def _filter_tweaks(self, ids: list[str]) -> tuple[list[str], list[str]]:
        unique_ids = dedupe_preserve_order(ids)
        compat: dict[str, bool] = {}
        for tid in unique_ids:
            meta = self.manager.get_meta(tid)
            compat[tid] = self._is_compatible(meta) if meta else False
        applicable, skipped = self.manager.filter_applicable(unique_ids, compat)
        applicable = dedupe_preserve_order(applicable)
        skipped = dedupe_preserve_order(skipped)

        if not self.system_info.is_admin:
            no_admin: list[str] = []
            kept: list[str] = []
            for tid in applicable:
                meta = self.manager.get_meta(tid)
                if meta and meta.requires_admin:
                    no_admin.append(tid)
                else:
                    kept.append(tid)
            applicable = kept
            skipped = dedupe_preserve_order(skipped + no_admin)
        return applicable, skipped

    def _build_apply_notes(self, applicable: list[str], skipped: list[str]) -> list[str]:
        notes: list[str] = []
        if skipped:
            notes.append(t("apply_notes_skipped", n=len(skipped)))
        conflicts = self.manager.get_conflicts(applicable)
        if conflicts:
            notes.append(t("apply_notes_conflicts", list="\n".join(conflicts)))
        high_risk = [
            self.manager.get_meta(tid).name
            for tid in applicable
            if (m := self.manager.get_meta(tid)) and m.risk == "high"
        ]
        if high_risk:
            notes.append(t("apply_notes_high_risk", list="\n".join(high_risk)))
        return notes

    def _show_apply_confirm(self, title: str, applicable: list[str], skipped: list[str]) -> None:
        ApplyConfirmModal(
            self,
            title,
            tweak_names=self.manager.resolve_tweak_names(applicable),
            notes=self._build_apply_notes(applicable, skipped),
            on_confirm=lambda: self._run_apply(applicable),
        ).exec()

    def _apply_category(self, nav_key: str) -> None:
        metas = self.manager.get_by_categories(nav_categories(nav_key))
        ids = [m.id for m in metas]
        applicable, skipped = self._filter_tweaks(ids)
        if not applicable:
            self._toast.show(t("nothing_to_apply"), "info")
            return
        title = category_label(nav_key)
        self._show_apply_confirm(t("apply_all_category", category=title), applicable, skipped)

    def _apply_selected(self) -> None:
        if not self._selected:
            self._toast.show(t("no_tweaks_selected"), "warning")
            return
        applicable, skipped = self._filter_tweaks(list(self._selected))
        if not applicable:
            self._toast.show(t("all_already_active"), "info")
            return
        self._show_apply_confirm(t("confirm_title"), applicable, skipped)

    def _run_apply(self, tweak_ids: list[str]) -> None:
        unique_ids = dedupe_preserve_order(tweak_ids)
        self._overlay.show_progress(0, len(unique_ids), t("overlay_starting"))
        self._apply_worker = ApplyWorker(self.manager, unique_ids)
        self._apply_worker.progress.connect(self._overlay.show_progress)
        self._apply_worker.finished_apply.connect(self._on_apply_done)
        self._apply_worker.finished.connect(self._cleanup_worker)
        self._apply_worker.start()
        self._workers.append(self._apply_worker)

    def _cleanup_worker(self) -> None:
        sender = self.sender()
        if sender in self._workers:
            self._workers.remove(sender)
        if isinstance(sender, QThread):
            sender.deleteLater()

    def _on_apply_done(self, ok: int, fail: int, total: int) -> None:
        self._overlay.hide_overlay()
        self._selected.clear()
        self._update_selected_badge()
        level = "success" if fail == 0 else "warning"
        self._toast.show(t("apply_done", ok=ok, fail=fail), level)
        self._refresh_current_page()
        self._start_background_scan()
        settings = self._pages.get("settings")
        if hasattr(settings, "refresh_stats"):
            settings.refresh_stats()

    def _start_background_scan(self) -> None:
        worker = ScanWorker(self.manager)
        worker.finished_ok.connect(self._refresh_current_page)
        worker.finished.connect(self._cleanup_worker)
        worker.start()
        self._workers.append(worker)

    def _apply_profile(self, profile: dict) -> None:
        ids = dedupe_preserve_order(profile.get("tweaks", []))
        applicable, skipped = self._filter_tweaks(ids)
        if not applicable:
            self._toast.show(t("profile_all_active"), "info")
            return
        self._show_apply_confirm(profile.get("name", t("profile_fallback")), applicable, skipped)

    def _revert_all(self) -> None:
        ConfirmModal(self, t("revert_title"), t("confirm_revert"), on_confirm=self._do_revert).exec()

    def _do_revert(self) -> None:
        worker = RevertWorker(self.manager)
        worker.finished_ok.connect(lambda ok: self._toast.show(t("reverted_count", n=ok), "success"))
        worker.finished_ok.connect(self._refresh_current_page)
        worker.finished.connect(self._cleanup_worker)
        worker.start()
        self._workers.append(worker)

    def _quick_action(self, action: str) -> None:
        if action == "revert_all":
            self._revert_all()
            return
        if action == "clear_temp_files":
            meta = self.manager.get_meta("clear_temp_files")
            name = meta.name if meta else t("cleanup_temp_fallback")
            ConfirmModal(
                self,
                t("cleanup_title"),
                t("cleanup_confirm", name=name),
                on_confirm=lambda: self._run_apply(["clear_temp_files"]),
            ).exec()
            return
        path = resource_path("config", "profiles", f"{action}.json")
        if ".." in action or "/" in action or "\\" in action:
            return
        if path.exists() and path.resolve().parent == resource_path("config", "profiles").resolve():
            from core.i18n import localize_profile

            with open(path, encoding="utf-8") as f:
                self._apply_profile(localize_profile(json.load(f)))

    def _rescan(self) -> None:
        self._scan_btn.setEnabled(False)
        self._scan_btn.setText(t("scanning"))
        worker = ScanWorker(self.manager)
        worker.finished_ok.connect(self._on_rescan_done)
        worker.finished.connect(self._cleanup_worker)
        worker.start()
        self._workers.append(worker)

    def _on_rescan_done(self) -> None:
        self._scan_btn.setEnabled(True)
        self._scan_btn.setText(t("rescan"))
        self._toast.show(t("scan_done"), "success")
        self._prune_selected()
        self._refresh_current_page()

    def _refresh_current_page(self) -> None:
        if self._current_page == "search":
            self._search_page.refresh(self._search.text())
        elif self._current_page in CATEGORY_MAP:
            self._ensure_tweak_page(self._current_page).refresh(self._search.text())
        self._update_dashboard_status()

    def _create_restore_point(self) -> None:
        worker = RestorePointWorker(self.backup)
        worker.finished_ok.connect(lambda ok, msg: self._toast.show(msg, "success" if ok else "error"))
        worker.finished.connect(self._cleanup_worker)
        worker.start()
        self._workers.append(worker)

    def _export_restore(self) -> None:
        path = self.backup.export_restore_script()
        self._toast.show(t("saved_to", path=path), "success")

    def _export_reg_baseline(self) -> None:
        from core.reg_backup import export_active_baseline

        path, msg = export_active_baseline(self.manager)
        level = "success" if path else "warning"
        self._toast.show(msg, level)

    def _open_backups_folder(self) -> None:
        import subprocess

        from core.logger import get_app_data_dir

        folder = get_app_data_dir() / "backups"
        folder.mkdir(parents=True, exist_ok=True)
        subprocess.run(["explorer", str(folder)], check=False)

    def closeEvent(self, event) -> None:
        for w in list(self._workers):
            if w.isRunning():
                w.wait(3000)
            w.deleteLater()
        self._workers.clear()
        super().closeEvent(event)

    def resizeEvent(self, event) -> None:
        w = self.width()
        if w < 980:
            margin = 10
        elif w < 1180:
            margin = 14
        else:
            margin = 20
        if hasattr(self, "_root_layout"):
            self._root_layout.setContentsMargins(margin, margin, margin, margin)
        super().resizeEvent(event)
