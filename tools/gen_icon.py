"""Генерация icon.ico для CrimsonTune (multi-size, crimson C mark)."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icon.ico"

BG = (10, 10, 15, 255)
CRIMSON = (214, 48, 49, 255)
CRIMSON_GLOW = (139, 30, 30, 180)
HIGHLIGHT = (231, 76, 76, 255)


def _crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = struct.pack(">I", _crc32(chunk_type + data))
    return struct.pack(">I", len(data)) + chunk_type + data + crc


def _rgba_pixel(x: int, y: int, size: int) -> bytes:
    cx, cy = size / 2 - 0.5, size / 2 - 0.5
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    outer = size * 0.46
    if r > outer:
        return bytes(BG)

    # Soft crimson ring
    ring_r = size * 0.36
    ring_w = max(1.2, size * 0.055)
    if abs(r - ring_r) <= ring_w:
        t = 1.0 - abs(r - ring_r) / ring_w
        c = tuple(int(BG[i] + (CRIMSON[i] - BG[i]) * t) for i in range(3)) + (255,)
        return bytes(c)

    # C-shaped arc
    angle = math.atan2(dy, dx)
    inner, outer_c = size * 0.14, size * 0.30
    on_arc = inner < r < outer_c and -2.35 < angle < 2.35
    if on_arc:
        edge = min(r - inner, outer_c - r, abs(angle - (-2.35)), abs(2.35 - angle))
        edge = min(edge, abs(angle - 0.0) * r * 0.35)
        if edge < max(1.0, size * 0.05):
            return bytes(HIGHLIGHT if edge < size * 0.02 else CRIMSON)

    # Inner glow
    if r < inner and -1.6 < angle < 1.6:
        t = max(0.0, 1.0 - r / inner)
        c = tuple(int(BG[i] + (CRIMSON_GLOW[i] - BG[i]) * t * 0.35) for i in range(3)) + (255,)
        return bytes(c)

    return bytes(BG)


def _render_rgba(size: int) -> bytes:
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(_rgba_pixel(x, y, size))
    return bytes(raw)


def _png_bytes(size: int) -> bytes:
    raw = _render_rgba(size)
    compressed = zlib.compress(raw, 9)
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", compressed)
    png += _png_chunk(b"IEND", b"")
    return png


def _build_ico(sizes: tuple[int, ...]) -> bytes:
    images = [(size, _png_bytes(size)) for size in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = bytearray()
    blobs = bytearray()
    for size, png in images:
        w = size if size < 256 else 0
        entries.extend(struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(png), offset))
        blobs.extend(png)
        offset += len(png)
    return header + bytes(entries) + bytes(blobs)


def main() -> None:
    ico = _build_ico((16, 24, 32, 48, 64, 128, 256))
    OUT.write_bytes(ico)
    print(f"written {OUT} ({len(ico)} bytes)")


if __name__ == "__main__":
    main()
