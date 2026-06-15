
from __future__ import annotations

from typing import Iterable


def dedupe_preserve_order(ids: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for tid in ids:
        if tid not in seen:
            seen.add(tid)
            result.append(tid)
    return result
