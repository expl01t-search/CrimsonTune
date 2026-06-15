
from __future__ import annotations

from dataclasses import replace

from core.i18n import t
from core.tweak_state import TweakStateInfo, TweakStatus
from tweaks.base import TweakMeta
from utils.compatibility import incompatible_detail


def enrich_state_for_display(state: TweakStateInfo, meta: TweakMeta) -> TweakStateInfo:
    if (
        state.applied_by_app
        and not state.active_in_system
        and meta.requires_reboot
        and state.status in (TweakStatus.APPLIED_APP, TweakStatus.ACTIVE_BOTH)
    ):
        return replace(state, status=TweakStatus.APPLIED_PENDING_REBOOT)
    return state


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
