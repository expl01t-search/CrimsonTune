
from __future__ import annotations

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ui.theme import ACCENT_CRIMSON, BG_ELEVATED

MODE_OFF = "off"
MODE_SELECTED = "selected"
MODE_ACTIVE = "active"
MODE_DISABLED = "disabled"


class ForgeToggle(QWidget):

    toggled = Signal(bool)

    _TRACK_W = 44
    _TRACK_H = 20
    _THUMB = 16
    _OFF_X = 3
    _ON_X = _TRACK_W - _THUMB - 3

    def __init__(self, parent=None, *, checked: bool = False, enabled: bool = True) -> None:
        super().__init__(parent)
        self.setFixedSize(self._TRACK_W, 24)
        self._checked = checked
        self._thumb_pos = float(self._ON_X if checked else self._OFF_X)
        self._enabled = enabled
        self._locked = False
        self._visual_mode = MODE_ACTIVE if checked else MODE_OFF
        self._anim: QPropertyAnimation | None = None
        self._update_cursor()

    def get_thumb_pos(self) -> float:
        return self._thumb_pos

    def set_thumb_pos(self, pos: float) -> None:
        self._thumb_pos = pos
        self.update()

    thumb_pos = Property(float, get_thumb_pos, set_thumb_pos)

    def visual_mode(self) -> str:
        return self._visual_mode

    def set_visual_mode(self, mode: str) -> None:
        if mode not in (MODE_OFF, MODE_SELECTED, MODE_ACTIVE, MODE_DISABLED):
            mode = MODE_OFF
        self._visual_mode = mode
        self.update()

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool, animate: bool = True) -> None:
        self._checked = checked
        target = float(self._ON_X if checked else self._OFF_X)
        if animate and self._enabled and not self._locked:
            self._anim = QPropertyAnimation(self, b"thumb_pos")
            self._anim.setDuration(120)
            self._anim.setStartValue(self._thumb_pos)
            self._anim.setEndValue(target)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.start()
        else:
            self._thumb_pos = target
            self.update()

    def isLocked(self) -> bool:
        return self._locked

    def setLocked(self, locked: bool) -> None:
        self._locked = locked
        self._update_cursor()
        self.update()

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._enabled = enabled
        self._update_cursor()
        self.update()

    def _update_cursor(self) -> None:
        if self._enabled and not self._locked:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event) -> None:
        if not self._enabled or self._locked:
            return
        self.setChecked(not self._checked)
        self.set_visual_mode(MODE_SELECTED if self._checked else MODE_OFF)
        self.toggled.emit(self._checked)
        super().mousePressEvent(event)

    def _track_color(self) -> QColor:
        if self._checked:
            color = QColor(ACCENT_CRIMSON)
            if self._locked or not self._enabled:
                return color.darker(115)
            return color
        if self._visual_mode == MODE_DISABLED:
            return QColor("#252830")
        return QColor(BG_ELEVATED)

    def _thumb_color(self) -> QColor:
        if self._checked:
            return QColor("#ffffff")
        if self._visual_mode == MODE_DISABLED:
            return QColor("#5c6478")
        return QColor("#9aa3b8")

    def paintEvent(self, event) -> None:
        with QPainter(self) as p:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            track = self._track_color()

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(track)
            p.drawRoundedRect(0, 2, self._TRACK_W, self._TRACK_H, 10, 10)

            p.setBrush(self._thumb_color())
            y = 2 + (self._TRACK_H - self._THUMB) // 2
            p.drawEllipse(int(self._thumb_pos), y, self._THUMB, self._THUMB)
