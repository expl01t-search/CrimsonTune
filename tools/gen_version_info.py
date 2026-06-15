from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _parse_version(text: str) -> tuple[int, int, int, int]:
    match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', text)
    raw = match.group(1) if match else "1.0.0"
    parts = [int(p) for p in re.findall(r"\d+", raw)]
    while len(parts) < 4:
        parts.append(0)
    return parts[0], parts[1], parts[2], parts[3]


def main() -> int:
    brand_path = ROOT / "core" / "brand.py"
    major, minor, patch, build = _parse_version(brand_path.read_text(encoding="utf-8"))
    dotted = f"{major}.{minor}.{patch}.{build}"
    short = f"{major}.{minor}.{patch}"

    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'CrimsonTune'),
            StringStruct(u'FileDescription', u'CrimsonTune - Precise Windows tuning'),
            StringStruct(u'FileVersion', u'{dotted}'),
            StringStruct(u'InternalName', u'CrimsonTune'),
            StringStruct(u'LegalCopyright', u'Copyright (C) 2026 CrimsonTune'),
            StringStruct(u'OriginalFilename', u'CrimsonTune.exe'),
            StringStruct(u'ProductName', u'CrimsonTune'),
            StringStruct(u'ProductVersion', u'{short}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    out = ROOT / "version_info.txt"
    out.write_text(content, encoding="utf-8")
    print(f"Wrote {out} ({short})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
