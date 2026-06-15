
from __future__ import annotations

import math

from PySide6.QtCore import Property, QPropertyAnimation, QRectF, Qt, QSize
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.theme import ACCENT_CRIMSON, NEON_CYAN, NEON_MAGENTA, configure_painter_text, resolve_mono_font, resolve_ui_font


class GaugeWidget(QWidget):

    START_DEG = 225
    SPAN_DEG = 270
    MIN_SIDE = 132
    MAX_SIDE = 248

    def __init__(self, title: str, *, accent: str = "cyan", parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(self.MIN_SIDE, int(self.MIN_SIDE * 0.88))
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._title = title.strip()
        self._accent = accent
        self._value = 0.0
        self._display = 0.0
        self._anim: QPropertyAnimation | None = None

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        side = max(self.MIN_SIDE, min(width, self.MAX_SIDE))
        return max(118, int(side * 0.88))

    def sizeHint(self) -> QSize:
        return QSize(200, self.heightForWidth(200))

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

    def apply_side(self, side: int) -> None:
        side = max(self.MIN_SIDE, min(side, self.MAX_SIDE))
        height = self.heightForWidth(side)
        if self.width() != side or self.height() != height:
            self.setFixedSize(side, height)
            self.update()

    def _colors(self) -> tuple[QColor, QColor]:
        crimson = QColor(ACCENT_CRIMSON)
        if self._accent in ("magenta", "crimson"):
            return crimson, crimson
        return QColor(NEON_CYAN), QColor(NEON_MAGENTA)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setClipRect(self.rect())
        configure_painter_text(p)

        w, h = self.width(), self.height()
        side = min(w, h)
        scale = max(0.72, min(1.0, side / 200.0))
        cx, cy = w / 2, h * 0.42
        radius = min(w, h) * 0.26
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        track_pen = QPen(QColor(255, 255, 255, 35), max(4, int(6 * scale)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(track_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(rect, self.START_DEG * 16, -self.SPAN_DEG * 16)

        if self._display > 0.5:
            c1, c2 = self._colors()
            sweep = int(-self.SPAN_DEG * (self._display / 100.0) * 16)
            value_pen = QPen(QColor(c1), max(5, int(7 * scale)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(value_pen)
            p.drawArc(rect, self.START_DEG * 16, sweep)

            angle_rad = math.radians(self.START_DEG - self.SPAN_DEG * (self._display / 100.0))
            nx = cx + radius * math.cos(angle_rad)
            ny = cy - radius * math.sin(angle_rad)
            dot = max(4, int(5 * scale))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(c2)
            p.drawEllipse(QRectF(nx - dot, ny - dot, dot * 2, dot * 2))

        p.setPen(QColor("#FFFFFF"))
        val_font = resolve_mono_font(point_size=max(15, int(22 * scale)), bold=True)
        p.setFont(val_font)
        val_h = max(28, int(36 * scale))
        val_top = cy - val_h * 0.45
        p.drawText(QRectF(0, val_top, w, val_h), Qt.AlignmentFlag.AlignCenter, f"{self._display:02.0f}%")

        if not self._title:
            p.end()
            return

        title_pt = max(7, int((8 if self._accent == "crimson" else 10) * scale))
        title_font = resolve_ui_font(point_size=title_pt)
        title_font.setBold(True)
        p.setFont(title_font)
        p.setPen(QColor("#f0f4fc"))
        title_rect = QRectF(8, cy + radius * 0.35, w - 16, h - (cy + radius * 0.35) - 4)
        p.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignTop
            | Qt.TextFlag.TextWordWrap,
            self._title,
        )
        p.end()
