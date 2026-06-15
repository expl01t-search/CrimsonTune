from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TweakGroup:
    key: str
    tweak_ids: tuple[str, ...]
    label_key: str


TWEAK_GROUPS: tuple[TweakGroup, ...] = (
    TweakGroup(
        "prefetch_superfetch",
        ("disable_sysmain", "disable_prefetch", "ssd_disable_superfetch_prefetch"),
        "group_prefetch_superfetch",
    ),
    TweakGroup(
        "search_indexing",
        ("disable_search_indexing", "ssd_disable_volume_indexing"),
        "group_search_indexing",
    ),
    TweakGroup(
        "nagle",
        ("disable_nagle", "disable_nagle_nic_interfaces"),
        "group_nagle",
    ),
    TweakGroup(
        "game_dvr",
        ("disable_game_dvr", "disable_fullscreen_optimizations", "disable_game_bar_presence"),
        "group_game_dvr",
    ),
    TweakGroup(
        "telemetry",
        (
            "disable_telemetry",
            "disable_edge_telemetry",
            "disable_defender_samples",
            "disable_tailored_experiences",
        ),
        "group_telemetry",
    ),
    TweakGroup(
        "power_plan",
        ("high_performance_power", "ultimate_performance_power"),
        "group_power_plan",
    ),
)

_ID_TO_GROUP: dict[str, str] = {}
_GROUP_BY_KEY: dict[str, TweakGroup] = {}
for _group in TWEAK_GROUPS:
    _GROUP_BY_KEY[_group.key] = _group
    for _tid in _group.tweak_ids:
        _ID_TO_GROUP[_tid] = _group.key


def group_for(tweak_id: str) -> str | None:
    return _ID_TO_GROUP.get(tweak_id)


def group_members(group_key: str) -> tuple[str, ...]:
    return _GROUP_BY_KEY[group_key].tweak_ids


def collapse_to_slots(tweak_ids: list[str]) -> list[str]:
    slots: list[str] = []
    seen_groups: set[str] = set()
    for tid in tweak_ids:
        gk = group_for(tid)
        if gk:
            if gk not in seen_groups:
                seen_groups.add(gk)
                slots.append(f"group:{gk}")
        else:
            slots.append(tid)
    return slots


def members_for_slot(slot: str, tweak_ids: list[str]) -> list[str]:
    if slot.startswith("group:"):
        group_key = slot[6:]
        allowed = set(group_members(group_key))
        return [tid for tid in tweak_ids if tid in allowed]
    if slot in tweak_ids:
        return [slot]
    return []


def overlapping_in_selection(tweak_ids: list[str]) -> list[tuple[str, list[str]]]:
    from utils.tweak_ids import dedupe_preserve_order

    hits: list[tuple[str, list[str]]] = []
    for group in TWEAK_GROUPS:
        present = [tid for tid in dedupe_preserve_order(tweak_ids) if tid in group.tweak_ids]
        if len(present) > 1:
            hits.append((group.key, present))
    return hits
