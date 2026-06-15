"""Генерация icon.ico для CrimsonTune."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icon.ico"


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = struct.pack(">I", _crc32(chunk_type + data))
    return struct.pack(">I", len(data)) + chunk_type + data + crc


def _crc32(data: bytes) -> int:
    import zlib
    return zlib.crc32(data) & 0xFFFFFFFF


def _write_png(path: Path, size: int, rgba_fn) -> None:
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(rgba_fn(x, y, size))
    import zlib
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", compressed)
    png += _png_chunk(b"IEND", b"")
    path.write_bytes(png)


def _rgba_pixel(x: int, y: int, size: int) -> bytes:
    cx, cy = size // 2, size // 2
    r = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    bg = (10, 10, 15, 255)
    if r > size * 0.46:
        return bytes(bg)
    # Letter C stylized arc
    angle = __import__("math").atan2(y - cy, x - cx)
    dist = abs(r - size * 0.22)
    accent = (214, 48, 49, 255)
    if size * 0.12 < r < size * 0.32 and -2.4 < angle < 2.4 and dist < size * 0.07:
        return bytes(accent)
    if dist < size * 0.04 and size * 0.12 < r < size * 0.32:
        return bytes(accent)
    return bytes(bg)


def _ico_from_png(png_data: bytes, size: int) -> bytes:
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack(
        "<BBBBHHII",
        size if size < 256 else 0,
        size if size < 256 else 0,
        0,
        0,
        1,
        32,
        len(png_data),
        22,
    )
    return header + entry + png_data


def main() -> None:
    import io
    import zlib

    size = 256
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(_rgba_pixel(x, y, size))
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", compressed)
    png += _png_chunk(b"IEND", b"")
    ico = _ico_from_png(png, size)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(ico)
    print(f"written {OUT} ({len(ico)} bytes)")


if __name__ == "__main__":
    main()
