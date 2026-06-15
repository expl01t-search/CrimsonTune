from __future__ import annotations

from tweaks.base import TweakManager
from tweaks.registry import register_all_handlers


def create_manager() -> TweakManager:
    manager = TweakManager()
    register_all_handlers(manager)
    manager.load_config()
    return manager
