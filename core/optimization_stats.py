from __future__ import annotations

from typing import Callable

from core.tweak_groups import collapse_to_slots, members_for_slot
from core.tweak_state import ONE_SHOT_TWEAKS, SYSTEM_CHECKS, TweakStatus, _register_supplemental_checks
from tweaks.base import TweakManager
from utils.compatibility import is_tweak_visible

RISK_WEIGHT: dict[str, float] = {
    "safe": 1.0,
    "medium": 1.25,
    "high": 1.5,
}


def _is_trackable(meta, *, has_check: bool, state) -> bool:
    if not has_check:
        return False
    if state.status in (TweakStatus.ONE_SHOT, TweakStatus.UNKNOWN, TweakStatus.INCOMPATIBLE):
        return False
    return True


def _slot_weight(metas_in_slot: list) -> float:
    return max(RISK_WEIGHT.get(meta.risk, 1.0) for meta in metas_in_slot)


def compute_optimization_stats(
    manager: TweakManager,
    is_compatible_fn: Callable,
) -> dict[str, int | float]:
    _register_supplemental_checks()

    metas = manager.get_all_meta()
    compat = {m.id: is_compatible_fn(m) for m in metas}
    meta_by_id = {m.id: m for m in metas}

    trackable_ids: list[str] = []
    for meta in metas:
        if not compat.get(meta.id, False):
            continue
        if not is_tweak_visible(meta, is_compatible_fn):
            continue
        has_check = meta.id in SYSTEM_CHECKS and meta.id not in ONE_SHOT_TWEAKS
        state = manager.get_tweak_state(meta.id, compatible=True)
        if not _is_trackable(meta, has_check=has_check, state=state):
            continue
        trackable_ids.append(meta.id)

    slots = collapse_to_slots(trackable_ids)
    active_sys = 0
    available = 0
    applied_app = 0
    pending_verify = 0
    pending_reboot = 0
    weight_total = 0.0
    weight_active = 0.0
    total = len(slots)

    for slot in slots:
        member_ids = members_for_slot(slot, trackable_ids)
        member_metas = [meta_by_id[tid] for tid in member_ids if tid in meta_by_id]
        if not member_metas:
            continue

        states = [manager.get_tweak_state(tid, compatible=True) for tid in member_ids]
        weight = _slot_weight(member_metas)
        weight_total += weight

        any_active_sys = any(s.active_in_system for s in states)
        any_applied = any(s.applied_by_app for s in states)
        any_active = any(s.is_active for s in states)
        any_pending_reboot = any(
            s.applied_by_app and not s.active_in_system and meta_by_id[s.tweak_id].requires_reboot
            for s in states
            if s.tweak_id in meta_by_id
        )

        if any_active_sys:
            active_sys += 1
            weight_active += weight
        elif any_applied:
            applied_app += 1
            pending_verify += 1
            if any_pending_reboot:
                pending_reboot += 1
            weight_active += weight
        else:
            available += 1

    percent_simple = round(((active_sys + applied_app) / total) * 100) if total else 0
    percent_weighted = round((weight_active / weight_total) * 100) if weight_total else 0.0

    return {
        "percent": percent_weighted,
        "percent_simple": percent_simple,
        "percent_honest": percent_weighted,
        "active": active_sys + applied_app,
        "total": total,
        "total_raw": len(trackable_ids),
        "available": available,
        "applied_app": applied_app,
        "pending_verify": pending_verify,
        "pending_reboot": pending_reboot,
        "one_shot": 0,
    }
