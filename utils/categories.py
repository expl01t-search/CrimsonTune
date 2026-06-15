from __future__ import annotations

GRAPHICS_CATEGORIES: tuple[str, ...] = ("nvidia", "amd", "directx", "opengl")
SYSTEM_NAV_CATEGORIES: tuple[str, ...] = ("system", "visual")
SSD_CATEGORIES: tuple[str, ...] = ("ssd",)

TWEAK_CATEGORY_KEYS: tuple[str, ...] = (
    "performance",
    "ssd",
    "gaming",
    *GRAPHICS_CATEGORIES,
    "network",
    "privacy",
    "visual",
    "system",
    "expert",
)

NAV_KEYS: tuple[str, ...] = (
    "dashboard",
    "performance",
    "gaming",
    "graphics",
    "network",
    "privacy",
    "system",
    "expert",
    "profiles",
    "settings",
)

CATEGORY_MAP: dict[str, tuple[str, ...]] = {
    "performance": ("performance", "ssd"),
    "gaming": ("gaming",),
    "graphics": GRAPHICS_CATEGORIES,
    "network": ("network",),
    "privacy": ("privacy",),
    "system": SYSTEM_NAV_CATEGORIES,
    "expert": ("expert",),
}


def nav_categories(nav_key: str) -> tuple[str, ...]:
    return CATEGORY_MAP[nav_key]
