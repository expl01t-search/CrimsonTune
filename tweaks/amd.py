
from __future__ import annotations

from tweaks.base import TweakResult


def amd_anti_lag_apply() -> TweakResult:
    return TweakResult(True, "AMD: Radeon Software → Графика → Anti-Lag → Включить", revert_data=None)


def amd_anti_lag_revert(_data) -> TweakResult:
    return TweakResult(True, "Настройте вручную в Radeon Software")


HANDLERS = {
    "amd_anti_lag": (amd_anti_lag_apply, amd_anti_lag_revert),
}
