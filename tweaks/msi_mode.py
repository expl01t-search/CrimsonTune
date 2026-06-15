from __future__ import annotations

from tweaks.base import TweakResult
from utils.msi_mode import apply_msi_high_priority, revert_msi_high_priority

_TARGET_CATEGORIES = frozenset({"gpu", "usb", "network"})


def msi_mode_high_priority_apply() -> TweakResult:
    snapshots, labels = apply_msi_high_priority(categories=_TARGET_CATEGORIES)
    if not snapshots:
        return TweakResult(
            False,
            "PCI-устройства (GPU/USB/LAN) не найдены — проверьте драйверы",
        )
    preview = ", ".join(labels[:4])
    if len(labels) > 4:
        preview += f" (+{len(labels) - 4})"
    return TweakResult(
        True,
        f"MSI + High priority: {len(snapshots)} устройств ({preview}). Перезагрузка обязательна",
        revert_data={"snapshots": snapshots},
    )


def msi_mode_high_priority_revert(data) -> TweakResult:
    if not data or not data.get("snapshots"):
        return TweakResult(False, "Нет данных для отката MSI Mode")
    revert_msi_high_priority(data["snapshots"])
    return TweakResult(True, "MSI Mode откачен — перезагрузка рекомендуется")


HANDLERS = {
    "msi_mode_high_priority": (msi_mode_high_priority_apply, msi_mode_high_priority_revert),
}
