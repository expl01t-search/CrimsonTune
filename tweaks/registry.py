from __future__ import annotations

from tweaks import (
    amd,
    directx,
    expert,
    exploit_extras,
    extended,
    gaming,
    network,
    nvidia,
    opengl,
    opensource,
    optimize_pack,
    performance,
    privacy,
    system,
    visual,
)
from tweaks.base import TweakManager

HANDLER_MODULES: tuple = (
    performance,
    gaming,
    nvidia,
    amd,
    directx,
    exploit_extras,
    opengl,
    network,
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
