"""Плоская карточка-поверхность — Modern Clarity."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget


class SurfaceCard(QFrame):
    """Минималистичная панель без glow и custom paint."""

    def __init__(self, *, variant: str = "default", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("surfaceCard")
        if variant != "default":
            self.setProperty("variant", variant)
            self.style().unpolish(self)
            self.style().polish(self)
        self._inner = QWidget(self)
        self._inner.setObjectName("surfaceInner")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(0)
        outer.addWidget(self._inner)
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(8)

    def content_layout(self) -> QVBoxLayout:
        return self._inner_layout
