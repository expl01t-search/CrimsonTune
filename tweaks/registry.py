from __future__ import annotations

from tweaks import (
    amd,
    community,
    directx,
    expert,
    exploit_extras,
    extended,
    gaming,
    msi_mode,
    network,
    nvidia,
    opengl,
    opensource,
    optimize_pack,
    performance,
    privacy,
    ssd,
    system,
    visual,
)
from tweaks.base import TweakManager

HANDLER_MODULES: tuple = (
    performance,
    ssd,
    gaming,
    msi_mode,
    nvidia,
    amd,
    directx,
    exploit_extras,
    opengl,
    network,
    community,
    privacy,
    visual,
    system,
    expert,
    extended,
    optimize_pack,
    opensource,
)


def register_all_handlers(manager: TweakManager) -> None:
    for module in HANDLER_MODULES:
        handlers = getattr(module, "HANDLERS", {})
        for tweak_id, (apply_fn, revert_fn) in handlers.items():
            manager.register_handler(tweak_id, apply_fn, revert_fn)
