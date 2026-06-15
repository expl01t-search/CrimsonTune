"""Запуск GUI CrimsonTune."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.brand import APP_NAME
from core.i18n import init_locale, load_language, t
from core.logger import setup_logger
from tweaks import create_manager
from ui.main_window import MainWindow
from ui.splash import SplashWindow
from ui.theme import apply_theme, icon_path

logger = setup_logger(__name__)


def run_app() -> None:
    """Splash → сканирование → одно главное окно."""
    init_locale(load_language())
    logger.info("Starting %s", APP_NAME)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    ico = icon_path()
    if ico.exists():
        app.setWindowIcon(QIcon(str(ico)))
    apply_theme(app)

    splash = SplashWindow()
    splash.center_on_screen()
    splash.show()
    app.processEvents()

    manager = create_manager()
    main_window: MainWindow | None = None

    def open_main_window() -> None:
        nonlocal main_window
        splash.prepare_for_handoff()
        splash.set_handoff_message(t("splash_handoff_ui"))
        app.processEvents()

        main_window = MainWindow(manager)
        app.processEvents()

        splash.shutdown_worker()
        app.processEvents()

        splash.hide()
        splash.close()
        splash.deleteLater()

        main_window.show()
        main_window.setWindowState(Qt.WindowState.WindowNoState)
        main_window.raise_()
        main_window.activateWindow()

    splash.finished.connect(open_main_window)
    splash.begin(manager)

    sys.exit(app.exec())


def restore_all() -> None:
    manager = create_manager()
    results = manager.revert_all()
    for tid, result in results:
        status = "OK" if result.success else "FAIL"
        print(f"[{status}] {tid}: {result.message}")
