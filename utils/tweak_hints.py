"""Краткие подсказки для твиков — диалог «?»."""

from __future__ import annotations

from core.i18n import risk_label, t
from core.tweak_state import ONE_SHOT_TWEAKS
from tweaks.base import TweakMeta

_GPU_LABELS = {"nvidia": "NVIDIA", "amd": "AMD", "intel": "Intel"}

_CATEGORY_TIP_KEYS = {
    "performance": "hint_cat_performance",
    "gaming": "hint_cat_gaming",
    "network": "hint_cat_network",
    "directx": "hint_cat_directx",
    "opengl": "hint_cat_opengl",
    "visual": "hint_cat_visual",
    "privacy": "hint_cat_privacy",
    "system": "hint_cat_system",
}


def _truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return f"{cut}…"


def _collect_tags(meta: TweakMeta) -> list[str]:
    tags: list[str] = []
    if meta.id in ONE_SHOT_TWEAKS:
        tags.append(t("status_oneshot"))
    if meta.requires_reboot:
        tags.append(t("reboot_required"))
    risk = risk_label(meta.risk)
    if meta.risk == "high":
        tags.append(t("hint_high_risk_restore", risk=risk))
    elif meta.risk == "medium":
        tags.append(risk)
    vendors = [v for v in meta.gpu_vendor if v != "all"]
    if vendors:
        names = "/".join(_GPU_LABELS.get(v, v.upper()) for v in vendors)
        tags.append(t("hint_gpu_only", names=names))
    return tags


def generate_hint_text(meta: TweakMeta) -> str:
    """Генерирует hint для отображения в UI."""
    if meta.hint.strip():
        return meta.hint.strip()

    parts = [meta.description.strip()]
    tip_key = _CATEGORY_TIP_KEYS.get(meta.category, "")
    if tip_key:
        tip = t(tip_key)
        if tip and tip not in parts[0]:
            parts.append(tip)

    tags = _collect_tags(meta)
    if tags:
        parts.append(" · ".join(tags))

    return _truncate(" ".join(parts), 200)


def build_display_hint(meta: TweakMeta) -> str:
    """Текст для диалога «?» — компактно, без дублирования описания в строке."""
    body = meta.hint.strip() if meta.hint.strip() else generate_hint_text(meta)
    body = _truncate(body, 220)

    tags = _collect_tags(meta)
    if not tags:
        return body

    tag_line = " · ".join(tags)
    if tag_line in body:
        return body
    return f"{body}\n\n{tag_line}"
