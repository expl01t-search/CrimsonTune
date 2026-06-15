
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.theme import NEON_CYAN, NEON_MAGENTA, configure_painter_text, resolve_ui_font


class LineChartWidget(QWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._cpu: list[float] = []
        self._ram: list[float] = []
        self._max_points = 36

    def push_sample(self, cpu: float, ram: float) -> None:
        self._cpu.append(max(0.0, min(100.0, cpu)))
        self._ram.append(max(0.0, min(100.0, ram)))
        if len(self._cpu) > self._max_points:
            self._cpu.pop(0)
            self._ram.pop(0)
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        configure_painter_text(p)
        rect = self.rect().adjusted(16, 12, -16, -28)
        w, h = rect.width(), rect.height()

        for i in range(5):
            y = rect.top() + h * i / 4
            p.setPen(QPen(QColor(255, 255, 255, 18), 1))
            p.drawLine(rect.left(), int(y), rect.right(), int(y))

        if len(self._cpu) < 2:
            p.setPen(QColor(120, 130, 160))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Сбор данных...")
            p.end()
            return

        def _points(data: list[float]) -> list[QPointF]:
            pts: list[QPointF] = []
            n = len(data)
            for i, val in enumerate(data):
                x = rect.left() + (w * i / max(n - 1, 1))
                y = rect.bottom() - (h * val / 100.0)
                pts.append(QPointF(x, y))
            return pts

        def _smooth_path(pts: list[QPointF]) -> QPainterPath:
            path = QPainterPath()
            path.moveTo(pts[0])
            for i in range(1, len(pts)):
                prev = pts[i - 1]
                cur = pts[i]
                cx = (prev.x() + cur.x()) / 2
                path.cubicTo(QPointF(cx, prev.y()), QPointF(cx, cur.y()), cur)
            return path

        cpu_pts = _points(self._cpu)
        ram_pts = _points(self._ram)
        cpu_path = _smooth_path(cpu_pts)
        ram_path = _smooth_path(ram_pts)

        fill_cpu = QPainterPath(cpu_path)
        fill_cpu.lineTo(cpu_pts[-1].x(), rect.bottom())
        fill_cpu.lineTo(cpu_pts[0].x(), rect.bottom())
        fill_cpu.closeSubpath()
        grad = QLinearGradient(0, rect.top(), 0, rect.bottom())
        grad.setColorAt(0.0, QColor(0, 242, 255, 55))
        grad.setColorAt(1.0, QColor(0, 242, 255, 0))
        p.fillPath(fill_cpu, grad)

        fill_ram = QPainterPath(ram_path)
        fill_ram.lineTo(ram_pts[-1].x(), rect.bottom())
        fill_ram.lineTo(ram_pts[0].x(), rect.bottom())
        fill_ram.closeSubpath()
        grad2 = QLinearGradient(0, rect.top(), 0, rect.bottom())
        grad2.setColorAt(0.0, QColor(171, 0, 255, 45))
        grad2.setColorAt(1.0, QColor(171, 0, 255, 0))
        p.fillPath(fill_ram, grad2)

        p.setPen(QPen(QColor(NEON_CYAN), 2.5))
        p.drawPath(cpu_path)
        p.setPen(QPen(QColor(NEON_MAGENTA), 2.5))
        p.drawPath(ram_path)

        p.setPen(QColor(130, 140, 170))
        label_font = resolve_ui_font(point_size=9)
        p.setFont(label_font)
        for label, x_ratio in (("1ч", 0.0), ("6ч", 0.5), ("24ч", 1.0)):
            x = rect.left() + w * x_ratio
            p.drawText(int(x) - 10, self.height() - 8, label)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(NEON_CYAN))
        lp = cpu_pts[-1]
        p.drawEllipse(QRectF(lp.x() - 4, lp.y() - 4, 8, 8))
        p.setBrush(QColor(NEON_MAGENTA))
        lp2 = ram_pts[-1]
        p.drawEllipse(QRectF(lp2.x() - 4, lp2.y() - 4, 8, 8))
        p.end()
