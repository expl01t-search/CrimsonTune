"""Адаптивное размещение и масштабирование окон."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QWidget


def ui_scale_factor(app: QApplication | None = None) -> float:
    app = app or QApplication.instance()
    if not app:
        return 1.0
    screen = app.primaryScreen()
    if not screen:
        return 1.0
    dpi = screen.logicalDotsPerInchX()
    return max(1.0, min(1.35, dpi / 96.0))


def scaled_point_size(base: int, app: QApplication | None = None) -> int:
    return max(base, round(base * ui_scale_factor(app)))


def _screen_geometry(widget: QWidget):
    app = QApplication.instance()
    screen = widget.screen() if widget else None
    if screen is None and app:
        screen = app.primaryScreen()
    return screen.availableGeometry() if screen else None


def place_main_window(window: QMainWindow) -> None:
    """Оконный режим: компактное окно по центру, без полноэкранного старта."""
    geo = _screen_geometry(window)
    if geo is None:
        window.resize(1120, 720)
        window.setMinimumSize(900, 580)
        return

    min_w = max(860, min(960, int(geo.width() * 0.50)))
    min_h = max(520, min(600, int(geo.height() * 0.45)))
    width = max(min_w, min(1180, int(geo.width() * 0.72)))
    height = max(min_h, min(820, int(geo.height() * 0.72)))

    window.setMinimumSize(min_w, min_h)
    window.resize(width, height)
    window.move(
        geo.x() + max(0, (geo.width() - width) // 2),
        geo.y() + max(0, (geo.height() - height) // 2),
    )
    window.setWindowState(Qt.WindowState.WindowNoState)


def place_modal(dialog: QDialog, parent: QWidget | None = None) -> None:
    """Размер модалки относительно родителя/экрана."""
    ref = parent or dialog.parentWidget()
    geo = _screen_geometry(ref or dialog)
    if geo is None:
        dialog.resize(500, 480)
        return

    if ref and ref.isVisible():
        ref_w = max(ref.width(), 720)
        ref_h = max(ref.height(), 520)
    else:
        ref_w = geo.width()
        ref_h = geo.height()

    width = max(440, min(680, int(ref_w * 0.46)))
    height = max(380, min(int(ref_h * 0.78), 720))
    dialog.resize(width, height)

    if ref and ref.isVisible():
        origin = ref.mapToGlobal(ref.rect().topLeft())
        x = origin.x() + max(0, (ref.width() - width) // 2)
        y = origin.y() + max(0, (ref.height() - height) // 2)
    else:
        x = geo.x() + (geo.width() - width) // 2
        y = geo.y() + (geo.height() - height) // 2

    dialog.move(x, y)
