from __future__ import annotations

import pkgutil
from pathlib import Path

KEEP_QT_MODULES = frozenset({"QtCore", "QtGui", "QtWidgets"})

QT_BINARY_SKIP = (
    "Qt6WebEngine",
    "Qt6Multimedia",
    "Qt6Qml",
    "Qt6Quick",
    "Qt6Designer",
    "Qt6Charts",
    "Qt6DataVisualization",
    "Qt6Graphs",
    "Qt6Location",
    "Qt6Bluetooth",
    "Qt6Nfc",
    "Qt6Sensors",
    "Qt6SerialPort",
    "Qt6Sql",
    "Qt6Test",
    "Qt6Pdf",
    "Qt6HttpServer",
    "Qt6RemoteObjects",
    "Qt6Scxml",
    "Qt6StateMachine",
    "Qt6VirtualKeyboard",
    "Qt6WebChannel",
    "Qt6WebSockets",
    "Qt63D",
    "Qt6Ax",
    "Qt6DBus",
    "Qt6Help",
    "Qt6NetworkAuth",
    "Qt6Positioning",
    "Qt6TextToSpeech",
    "Qt6UiTools",
    "Qt6Xml",
    "Qt6Svg",
    "Qt6OpenGLWidgets",
    "Qt6ShaderTools",
    "Qt6SpatialAudio",
    "avcodec",
    "avformat",
    "avutil",
    "swresample",
    "swscale",
)

QT_PLUGIN_SKIP = (
    "/qml/",
    "/webview/",
    "/geoservices/",
    "/mediaservice/",
    "/audio/",
    "/playlistformats/",
    "/renderers/",
    "/sceneparsers/",
    "/geometryloaders/",
    "/position/",
    "/bearer/",
    "/texttospeech/",
    "/virtualkeyboard/",
    "/sqldrivers/",
    "/tls/",
)

IMAGE_PLUGIN_KEEP = frozenset({"qico.dll", "qgif.dll", "qsvg.dll"})

STDLIB_EXCLUDES = (
    "tkinter",
    "customtkinter",
    "unittest",
    "pydoc",
    "doctest",
    "xmlrpc",
    "lib2to3",
    "test",
    "tests",
    "pytest",
    "_pytest",
    "setuptools",
    "pip",
    "distutils",
    "email",
    "html",
    "http",
    "urllib3",
    "certifi",
    "numpy",
    "pandas",
    "matplotlib",
    "scipy",
    "PIL",
    "cv2",
    "IPython",
    "notebook",
    "jinja2",
    "sqlite3",
)


def qt_module_excludes() -> list[str]:
    import PySide6

    excludes: list[str] = []
    for module in pkgutil.iter_modules(PySide6.__path__):
        name = module.name
        if name.startswith("Qt") and name not in KEEP_QT_MODULES:
            excludes.append(f"PySide6.{name}")
    return excludes


def all_excludes() -> list[str]:
    return [*STDLIB_EXCLUDES, *qt_module_excludes()]


def _path_key(path: str | Path) -> str:
    return str(path).replace("\\", "/").lower()


def filter_binaries(binaries: list) -> list:
    kept: list = []
    for entry in binaries:
        name = entry[0] if entry else ""
        if any(token.lower() in name.lower() for token in QT_BINARY_SKIP):
            continue
        kept.append(entry)
    return kept


def filter_datas(datas: list) -> list:
    kept: list = []
    for entry in datas:
        dest = _path_key(entry[0])
        if any(token in dest for token in QT_PLUGIN_SKIP):
            continue
        if "/imageformats/" in dest:
            name = Path(dest).name
            if name not in IMAGE_PLUGIN_KEEP:
                continue
        kept.append(entry)
    return kept
