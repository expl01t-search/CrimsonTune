
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from core.backup import BackupManager
from core.logger import setup_logger
from core.paths import resource_path
from core.tweak_state import ONE_SHOT_TWEAKS, TweakStateDetector, TweakStateInfo

logger = setup_logger(__name__)


class RiskLevel(str, Enum):
    SAFE = "safe"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class TweakMeta:

    id: str
    name: str
    description: str
    category: str
    risk: str = "safe"
    requires_admin: bool = False
    requires_reboot: bool = False
    compatible_os: list[str] = field(default_factory=list)
    gpu_vendor: list[str] = field(default_factory=lambda: ["all"])
    ram_tier_gb: int | None = None
    default: bool = False
    hint: str = ""


@dataclass
class TweakResult:

    success: bool
    message: str
    revert_data: Any = None


class BaseTweak(ABC):

    def __init__(self, meta: TweakMeta) -> None:
        self.meta = meta

    @abstractmethod
    def apply(self) -> TweakResult:
        ...

    @abstractmethod
    def revert(self, revert_data: Any = None) -> TweakResult:
        ...
    def is_compatible(self, os_build: str, gpu_vendor: str) -> bool:
        if self.meta.compatible_os:
            if not any(os_build.startswith(v) for v in self.meta.compatible_os):
                return False
        vendors = self.meta.gpu_vendor
        if vendors and "all" not in vendors:
            if gpu_vendor not in vendors:
                return False
        return True


HandlerFunc = Callable[[], TweakResult]
RevertFunc = Callable[[Any], TweakResult]


class FunctionTweak(BaseTweak):

    def __init__(
        self,
        meta: TweakMeta,
        apply_fn: HandlerFunc,
        revert_fn: RevertFunc,
    ) -> None:
        super().__init__(meta)
        self._apply_fn = apply_fn
        self._revert_fn = revert_fn

    def apply(self) -> TweakResult:
        return self._apply_fn()

    def revert(self, revert_data: Any = None) -> TweakResult:
        return self._revert_fn(revert_data)


class TweakManager:

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.config_path = config_path or resource_path("config", "tweaks.json")
        self.backup = BackupManager()
        self.state_detector = TweakStateDetector(set(self.backup.get_all_applied()))
        self._tweaks: dict[str, BaseTweak] = {}
        self._meta: dict[str, TweakMeta] = {}
        self._handlers: dict[str, tuple[HandlerFunc, RevertFunc]] = {}
        self._source_items: dict[str, dict[str, Any]] = {}

    def register_handler(
        self,
        tweak_id: str,
        apply_fn: HandlerFunc,
        revert_fn: RevertFunc,
    ) -> None:
        self._handlers[tweak_id] = (apply_fn, revert_fn)

    def load_config(self) -> list[TweakMeta]:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Не найден {self.config_path}. Переустановите CrimsonTune или соберите EXE с config/."
            )
        with open(self.config_path, encoding="utf-8") as f:
            data = json.load(f)

        known = {f.name for f in TweakMeta.__dataclass_fields__.values()}
        metas: list[TweakMeta] = []
        seen_ids: set[str] = set()
        for item in data.get("tweaks", []):
            tid = item.get("id")
            if not tid:
                continue
            if tid in seen_ids:
                logger.warning("Дубликат id в tweaks.json, пропущен: %s", tid)
                continue
            seen_ids.add(tid)
            filtered = {k: v for k, v in item.items() if k in known}
            self._source_items[tid] = filtered
            meta = TweakMeta(**filtered)
            from core.i18n import localize_meta

            meta = localize_meta(meta)
            self._meta[meta.id] = meta

            if meta.id in self._handlers:
                apply_fn, revert_fn = self._handlers[meta.id]
                self._tweaks[meta.id] = FunctionTweak(meta, apply_fn, revert_fn)
            metas.append(meta)

        from tweaks.supplemental_catalog import supplemental_meta_items

        for item in supplemental_meta_items():
            tid = item.get("id")
            if not tid or tid in seen_ids:
                continue
            seen_ids.add(tid)
            filtered = {k: v for k, v in item.items() if k in known}
            self._source_items[tid] = filtered
            meta = TweakMeta(**filtered)
            from core.i18n import localize_meta

            meta = localize_meta(meta)
            self._meta[meta.id] = meta
            if meta.id in self._handlers:
                apply_fn, revert_fn = self._handlers[meta.id]
                self._tweaks[meta.id] = FunctionTweak(meta, apply_fn, revert_fn)
            metas.append(meta)

        self._handlers = {tid: self._handlers[tid] for tid in self._meta if tid in self._handlers}
        logger.info("Загружено %d твиков, %d с обработчиками", len(metas), len(self._tweaks))
        return metas

    def reload_translations(self) -> None:
        from core.i18n import localize_meta

        for tid, raw in self._source_items.items():
            if tid not in self._meta:
                continue
            meta = localize_meta(TweakMeta(**raw))
            self._meta[tid] = meta
            if tid in self._tweaks:
                self._tweaks[tid].meta = meta

    def get_meta(self, tweak_id: str) -> Optional[TweakMeta]:
        return self._meta.get(tweak_id)

    def get_by_category(self, category: str) -> list[TweakMeta]:
        return [m for m in self._meta.values() if m.category == category]

    def get_by_categories(self, categories: tuple[str, ...]) -> list[TweakMeta]:
        allowed = set(categories)
        return [m for m in self._meta.values() if m.category in allowed]

    def get_all_meta(self) -> list[TweakMeta]:
        return list(self._meta.values())

    def apply_tweak(self, tweak_id: str, session_dir: Optional[Path] = None) -> TweakResult:
        tweak = self._tweaks.get(tweak_id)
        if not tweak:
            return TweakResult(False, f"Обработчик для '{tweak_id}' не реализован")

        try:
            result = tweak.apply()
            if result.success and tweak_id not in ONE_SHOT_TWEAKS:
                self.backup.record_applied(tweak_id, result.revert_data)
                self.state_detector.set_applied_by_app(set(self.backup.get_all_applied()))
                self.state_detector.invalidate([tweak_id])
            elif result.success:
                self.state_detector.invalidate([tweak_id])
            if result.success:
                logger.info("Твик применён: %s — %s", tweak_id, result.message)
            else:
                logger.warning("Ошибка твика %s: %s", tweak_id, result.message)
            return result
        except Exception as exc:
            logger.exception("Исключение при применении %s", tweak_id)
            return TweakResult(False, str(exc))

    def revert_tweak(self, tweak_id: str) -> TweakResult:
        tweak = self._tweaks.get(tweak_id)
        if not tweak:
            return TweakResult(False, f"Обработчик для '{tweak_id}' не реализован")

        revert_data = self.backup.get_revert_data(tweak_id)
        try:
            result = tweak.revert(revert_data)
            if result.success:
                self.backup.remove_applied(tweak_id)
                self.state_detector.set_applied_by_app(set(self.backup.get_all_applied()))
                self.state_detector.invalidate([tweak_id])
                logger.info("Твик откачен: %s", tweak_id)
            return result
        except Exception as exc:
            logger.exception("Исключение при откате %s", tweak_id)
            return TweakResult(False, str(exc))

    def apply_multiple(self, tweak_ids: list[str]) -> list[tuple[str, TweakResult]]:
        session = self.backup.create_session_backup(tweak_ids)
        results: list[tuple[str, TweakResult]] = []
        for tid in tweak_ids:
            result = self.apply_tweak(tid, session)
            results.append((tid, result))
        return results

    def revert_all(self) -> list[tuple[str, TweakResult]]:
        applied = [tid for tid in self.backup.get_all_applied() if tid not in ONE_SHOT_TWEAKS]
        results: list[tuple[str, TweakResult]] = []
        for tid in reversed(applied):
            result = self.revert_tweak(tid)
            results.append((tid, result))
        return results

    def get_conflicts(self, tweak_ids: list[str]) -> list[str]:
        return []

    def get_tweak_state(self, tweak_id: str, *, compatible: bool = True) -> TweakStateInfo:
        return self.state_detector.get_state(tweak_id, compatible=compatible)

    def filter_applicable(
        self, tweak_ids: list[str], compatible_map: dict[str, bool]
    ) -> tuple[list[str], list[str]]:
        return self.state_detector.filter_applicable(tweak_ids, compatible_map)

    def resolve_tweak_names(self, tweak_ids: list[str]) -> list[str]:
        from utils.tweak_ids import dedupe_preserve_order

        names: list[str] = []
        for tid in dedupe_preserve_order(tweak_ids):
            meta = self.get_meta(tid)
            names.append(meta.name if meta else tid)
        return names

    def refresh_states(self) -> None:
        self.state_detector.set_applied_by_app(set(self.backup.get_all_applied()))

    def search(self, query: str) -> list[TweakMeta]:
        q = query.lower().strip()
        if not q:
            return self.get_all_meta()
        return [
            m for m in self._meta.values()
            if q in m.name.lower() or q in m.description.lower() or q in m.id.lower()
        ]
