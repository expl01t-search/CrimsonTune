#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    if "--restore-all" in sys.argv:
        from core.app import restore_all
        restore_all()
        return

    from ui.theme import setup_high_dpi

    setup_high_dpi()
    from core.app import run_app
    run_app()


if __name__ == "__main__":
    main()
