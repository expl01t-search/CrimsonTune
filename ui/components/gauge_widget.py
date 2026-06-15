"""Круговой gauge CPU/RAM в неоновом стиле."""

from __future__ import annotations

import math

from PySide6.QtCore import Property, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QConicalGradient, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.theme import ACCENT_CRIMSON, NEON_CYAN, NEON_MAGENTA, configure_painter_text, resolve_mono_font, resolve_ui_font


class GaugeWidget(QWidget):
    """Анимированный круговой индикатор загрузки."""

    START_DEG = 225
    SPAN_DEG = 270

    def __init__(self, title: str, *, accent: str = "cyan", parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(220, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._title = title
        self._accent = accent
        self._value = 0.0
        self._display = 0.0
        self._anim: QPropertyAnimation | None = None

    def get_display(self) -> float:
        return self._display

    def set_display(self, value: float) -> None:
        self._display = value
        self.update()

    display = Property(float, get_display, set_display)

    def set_value(self, value: float, *, animate: bool = True) -> None:
        self._value = max(0.0, min(100.0, value))
        if animate:
            self._anim = QPropertyAnimation(self, b"display")
            self._anim.setDuration(450)
            self._anim.setStartValue(self._display)
            self._anim.setEndValue(self._value)
            self._anim.start()
        else:
            self.set_display(self._value)

    def _colors(self) -> tuple[QColor, QColor]:
        crimson = QColor(ACCENT_CRIMSON)
        if self._accent in ("magenta", "crimson"):
            return crimson, crimson
        return QColor(NEON_CYAN), QColor(NEON_MAGENTA)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        configure_painter_text(p)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2 - 8
        radius = min(w, h) * 0.34
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        track_pen = QPen(QColor(255, 255, 255, 35), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(track_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(rect, self.START_DEG * 16, -self.SPAN_DEG * 16)

        if self._display > 0.5:
            c1, c2 = self._colors()
            sweep = int(-self.SPAN_DEG * (self._display / 100.0) * 16)
            value_pen = QPen(QColor(c1), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(value_pen)
            p.drawArc(rect, self.START_DEG * 16, sweep)

            angle_rad = math.radians(self.START_DEG - self.SPAN_DEG * (self._display / 100.0))
            nx = cx + radius * math.cos(angle_rad)
            ny = cy - radius * math.sin(angle_rad)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(c2)
            p.drawEllipse(QRectF(nx - 5, ny - 5, 10, 10))

        p.setPen(QColor("#FFFFFF"))
        val_font = resolve_mono_font(point_size=22, bold=True)
        p.setFont(val_font)
        p.drawText(QRectF(0, cy - 28, w, 40), Qt.AlignmentFlag.AlignCenter, f"{self._display:02.0f}%")

        title_pt = 8 if self._accent == "crimson" else 10
        title_font = resolve_ui_font(point_size=title_pt)
        title_font.setBold(True)
        p.setFont(title_font)
        p.setPen(QColor("#f0f4fc"))
        title_rect = QRectF(16, cy + 14, w - 32, 34)
        p.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignTop
            | Qt.TextFlag.TextWordWrap,
            self._title,
        )
        p.end()
