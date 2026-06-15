
from __future__ import annotations

from pathlib import Path

from core.brand import ICON_FILE
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPainter, QPalette
from PySide6.QtWidgets import QScrollArea, QWidget

BG_DEEP = "#0a0a0f"
BG_SURFACE = "#121218"
BG_ELEVATED = "#181820"
ACCENT_CRIMSON = "#d63031"
ACCENT_CRIMSON_HOVER = "#e74c4c"
ACCENT_CRIMSON_DARK = "#a82828"
ACCENT_SECONDARY = "#8b1e1e"
NEON_CYAN = ACCENT_CRIMSON  # legacy alias for components
NEON_MAGENTA = ACCENT_CRIMSON_HOVER
NEON_PURPLE = ACCENT_CRIMSON_DARK
ACCENT_FORGE = ACCENT_CRIMSON
ACCENT_CYAN = ACCENT_CRIMSON
SUCCESS = "#00c896"
WARNING = "#ffd740"
ERROR = "#ff4444"
TEXT_PRIMARY = "#e8ecf4"
TEXT_MUTED = "#8b95b8"
BORDER = "rgba(214, 48, 49, 0.28)"
ACTIVE_BORDER = ACCENT_CRIMSON

FONT_UI_CANDIDATES = ("Segoe UI", "Segoe UI Variable Text", "Tahoma", "Arial")
FONT_MONO_CANDIDATES = ("Cascadia Mono", "Cascadia Code", "Consolas", "Lucida Console")
FONT_UI = "Segoe UI"
FONT_MONO = "Consolas"
BASE_UI_POINT_SIZE = 11

SIDEBAR_WIDTH = 220

_CATEGORY_KEYS = (
    "performance",
    "gaming",
    "graphics",
    "directx",
    "opengl",
    "network",
    "privacy",
    "visual",
    "system",
    "nvidia",
    "amd",
    "expert",
)
_RISK_KEYS = ("safe", "medium", "high")


class _I18nDict(dict):

    def __init__(self, resolver) -> None:
        self._resolver = resolver

    def get(self, key, default=None):  # noqa: ANN001
        try:
            return self._resolver(key)
        except Exception:
            return default if default is not None else key

    def __getitem__(self, key):  # noqa: ANN001
        return self.get(key)


def _category_label(key: str) -> str:
    from core.i18n import category_label

    return category_label(key)


def _risk_label(key: str) -> str:
    from core.i18n import risk_label

    return risk_label(key)


CATEGORY_LABELS = _I18nDict(_category_label)
RISK_LABELS = _I18nDict(_risk_label)

STAT_ACCENTS = ("crimson", "forge", "green", "violet")


def icon_path() -> Path:
    return ICON_FILE


def _pick_family(candidates: tuple[str, ...], fallback: str) -> str:
    available = set(QFontDatabase.families())
    for name in candidates:
        if name in available:
            return name
    return fallback


def setup_high_dpi() -> None:
    from PySide6.QtGui import QGuiApplication

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )


def _apply_font_rendering(font: QFont) -> QFont:
    font.setStyleStrategy(
        QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality
    )
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return font


def resolve_ui_font(*, point_size: int = BASE_UI_POINT_SIZE) -> QFont:
    font = QFont(_pick_family(FONT_UI_CANDIDATES, FONT_UI), point_size)
    return _apply_font_rendering(font)


def resolve_mono_font(*, point_size: int = 14, bold: bool = True) -> QFont:
    family = _pick_family(FONT_MONO_CANDIDATES, FONT_MONO)
    weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
    font = QFont(family, point_size, weight)
    return _apply_font_rendering(font)


def configure_painter_text(painter: QPainter) -> None:
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)


def setup_palette(app) -> None:
    bg = QColor(BG_DEEP)
    surface = QColor(BG_SURFACE)
    elevated = QColor(BG_ELEVATED)
    text = QColor(TEXT_PRIMARY)
    muted = QColor(TEXT_MUTED)

    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, bg)
    p.setColor(QPalette.ColorRole.WindowText, text)
    p.setColor(QPalette.ColorRole.Base, surface)
    p.setColor(QPalette.ColorRole.AlternateBase, elevated)
    p.setColor(QPalette.ColorRole.Text, text)
    p.setColor(QPalette.ColorRole.Button, elevated)
    p.setColor(QPalette.ColorRole.ButtonText, text)
    p.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.ToolTipBase, surface)
    p.setColor(QPalette.ColorRole.ToolTipText, text)
    p.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT_CRIMSON))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.PlaceholderText, muted)
    p.setColor(QPalette.ColorRole.Link, QColor(ACCENT_CRIMSON))
    p.setColor(QPalette.ColorRole.Mid, bg)
    p.setColor(QPalette.ColorRole.Dark, bg.darker(115))
    p.setColor(QPalette.ColorRole.Light, elevated)
    app.setPalette(p)


def setup_fonts(app) -> None:
    global FONT_UI, FONT_MONO
    FONT_UI = _pick_family(FONT_UI_CANDIDATES, FONT_UI)
    FONT_MONO = _pick_family(FONT_MONO_CANDIDATES, FONT_MONO)
    from ui.window_utils import scaled_point_size

    app.setFont(resolve_ui_font(point_size=scaled_point_size(BASE_UI_POINT_SIZE, app)))


def style_scroll_area(scroll: QScrollArea, container: QWidget | None = None) -> None:
    scroll.setObjectName("appScroll")
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    scroll.setAutoFillBackground(True)

    viewport = scroll.viewport()
    viewport.setObjectName("scrollViewport")
    viewport.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    viewport.setAutoFillBackground(True)

    if container is not None:
        container.setObjectName("listContainer")
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        container.setAutoFillBackground(True)


def qss_path() -> Path:
    return Path(__file__).resolve().parent / "assets" / "styles" / "cyber_forge.qss"


def _apply_accent_colors(template: str) -> str:
    r, g, b = int(ACCENT_CRIMSON[1:3], 16), int(ACCENT_CRIMSON[3:5], 16), int(ACCENT_CRIMSON[5:7], 16)
    replacements = {
        "#ff2d55": ACCENT_CRIMSON,
        "#ff5c77": ACCENT_CRIMSON_HOVER,
        "#e63946": ACCENT_CRIMSON_DARK,
        "rgba(255, 45, 85,": f"rgba({r}, {g}, {b},",
    }
    for old, new in replacements.items():
        template = template.replace(old, new)
    return template


def load_stylesheet() -> str:
    path = qss_path()
    if path.exists():
        template = path.read_text(encoding="utf-8")
        template = (
            template.replace("{{FONT_UI}}", FONT_UI)
            .replace("{{FONT_MONO}}", FONT_MONO)
            .replace("{{BG_DEEP}}", BG_DEEP)
            .replace("{{BG_SURFACE}}", BG_SURFACE)
            .replace("{{BG_ELEVATED}}", BG_ELEVATED)
        )
        return _apply_accent_colors(template)
    return f"QMainWindow {{ background: {BG_DEEP}; }}"


def apply_theme(app) -> None:
    from ui.window_utils import scaled_point_size

    app.setStyle("Fusion")
    setup_palette(app)
    setup_fonts(app)
    app.setStyleSheet(load_stylesheet())
    app.setFont(resolve_ui_font(point_size=scaled_point_size(BASE_UI_POINT_SIZE, app)))
