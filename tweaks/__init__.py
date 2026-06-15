"""Регистрация всех обработчиков твиков."""

from __future__ import annotations

from tweaks import (
    directx,
    extended,
    gaming,
    network,
    opengl,
    opensource,
    optimize_pack,
    performance,
    privacy,
    system,
    visual,
)
from tweaks.base import TweakManager


def register_all_handlers(manager: TweakManager) -> None:
    """Регистрирует все обработчики твиков в менеджере."""
    modules = [
        performance,
        gaming,
        directx,
        opengl,
        network,
        privacy,
        visual,
        system,
        extended,
        optimize_pack,
        opensource,
    ]
    for module in modules:
        handlers = getattr(module, "HANDLERS", {})
        for tweak_id, (apply_fn, revert_fn) in handlers.items():
            manager.register_handler(tweak_id, apply_fn, revert_fn)


def create_manager() -> TweakManager:
    """Создаёт и инициализирует менеджер твиков."""
    manager = TweakManager()
    register_all_handlers(manager)
    manager.load_config()
    return manager
