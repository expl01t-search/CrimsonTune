from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def extract_section(changelog_text: str, version: str) -> str:
    header = f"## [{version}]"
    if header not in changelog_text:
        raise ValueError(f"Section {header} not found in CHANGELOG.md")

    start = changelog_text.index(header)
    rest = changelog_text[start + len(header) :]
    match = re.search(r"\n## \[", rest)
    end = start + len(header) + (match.start() if match else len(rest))
    body = changelog_text[start:end].strip()
    return body + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: extract_release_notes.py <version> [output_path]", file=sys.stderr)
        return 1

    version = sys.argv[1].lstrip("vV")
    changelog_path = ROOT / "CHANGELOG.md"
    text = changelog_path.read_text(encoding="utf-8")
    section = extract_section(text, version)

    if len(sys.argv) >= 3:
        out = Path(sys.argv[2])
        out.write_text(section, encoding="utf-8")
    else:
        print(section, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
