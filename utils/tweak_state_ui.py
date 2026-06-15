
from __future__ import annotations

from core.i18n import t
from core.tweak_state import TweakStateInfo, TweakStatus
from tweaks.base import TweakMeta
from utils.compatibility import incompatible_detail


def build_incompatible_state(meta: TweakMeta, gpu_vendor: str) -> TweakStateInfo:
    return TweakStateInfo(
        tweak_id=meta.id,
        status=TweakStatus.INCOMPATIBLE,
        is_active=False,
        can_apply=False,
        applied_by_app=False,
        active_in_system=False,
        detail=incompatible_detail(meta, gpu_vendor),
    )


def build_admin_blocked_state(meta: TweakMeta) -> TweakStateInfo:
    return TweakStateInfo(
        tweak_id=meta.id,
        status=TweakStatus.INCOMPATIBLE,
        is_active=False,
        can_apply=False,
        applied_by_app=False,
        active_in_system=False,
        detail=t("restricted"),
    )
