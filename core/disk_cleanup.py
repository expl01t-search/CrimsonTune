
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

ProgressFn = Callable[[int, int, str, int], None]

_JUNK_EXTENSIONS = (".log", ".bak", ".gid")


@dataclass
class CleanupResult:
    bytes_freed: int = 0
    files_deleted: int = 0
    steps_done: int = 0
    errors: int = 0


def format_freed_size(num_bytes: int) -> str:
    if num_bytes >= 1024 ** 3:
        return f"{num_bytes / (1024 ** 3):.2f} ГБ"
    if num_bytes >= 1024 ** 2:
        return f"{num_bytes / (1024 ** 2):.1f} МБ"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.0f} КБ"
    return f"{num_bytes} Б"


def _env_paths() -> dict[str, Path]:
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    systemdrive = Path(os.environ.get("SystemDrive", "C:") + "\\")
    temp = Path(os.environ.get("TEMP", os.environ.get("TMP", windir / "Temp")))
    tmp = Path(os.environ.get("TMP", temp))
    local_temp = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp"
    return {
        "windir": windir,
        "systemdrive": systemdrive,
        "temp": temp,
        "tmp": tmp,
        "local_temp": local_temp,
    }


def _unique_existing_dirs(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    for raw in paths:
        try:
            resolved = str(raw.resolve()).lower()
        except OSError:
            resolved = str(raw).lower()
        if resolved in seen:
            continue
        seen.add(resolved)
        if raw.exists() and raw.is_dir():
            out.append(raw)
    return out


def _purge_directory(path: Path) -> tuple[int, int, int]:
    freed = files = errors = 0
    if not path.exists():
        return 0, 0, 0
    try:
        for root, dirs, filenames in os.walk(path, topdown=False, onerror=lambda _e: None):
            for name in filenames:
                fp = Path(root) / name
                try:
                    size = fp.stat().st_size
                    fp.unlink()
                    freed += size
                    files += 1
                except OSError:
                    errors += 1
            for name in dirs:
                dp = Path(root) / name
                try:
                    dp.rmdir()
                except OSError:
                    pass
    except OSError:
        errors += 1
    return freed, files, errors


def _purge_extensions_in_dirs(
    dirs: list[Path],
    extensions: tuple[str, ...],
) -> tuple[int, int, int]:
    freed = files = errors = 0
    ext_set = {e.lower() for e in extensions}
    for base in dirs:
        try:
            for root, _, filenames in os.walk(base, topdown=True, onerror=lambda _e: None):
                for name in filenames:
                    if Path(name).suffix.lower() not in ext_set:
                        continue
                    fp = Path(root) / name
                    try:
                        size = fp.stat().st_size
                        fp.unlink()
                        freed += size
                        files += 1
                    except OSError:
                        errors += 1
        except OSError:
            errors += 1
    return freed, files, errors


def run_disk_cleanup(on_progress: ProgressFn | None = None) -> CleanupResult:
    paths = _env_paths()
    windir = paths["windir"]

    safe_dirs = _unique_existing_dirs(
        [
            windir / "Temp",
            paths["systemdrive"] / "Temp",
            paths["temp"],
            paths["tmp"],
            paths["local_temp"],
            windir / "Prefetch",
        ]
    )

    dir_steps: list[tuple[str, Path]] = [
        ("Windows\\Temp", windir / "Temp"),
        ("Temp на диске", paths["systemdrive"] / "Temp"),
        ("Temp пользователя", paths["temp"]),
        ("Tmp", paths["tmp"]),
        ("Prefetch", windir / "Prefetch"),
    ]

    total_steps = len(dir_steps) + 1
    result = CleanupResult()
    step_idx = 0

    for label, folder in dir_steps:
        if on_progress:
            on_progress(step_idx, total_steps, label, result.bytes_freed)
        freed, files, errs = _purge_directory(folder)
        result.bytes_freed += freed
        result.files_deleted += files
        result.errors += errs
        result.steps_done += 1
        step_idx += 1
        if on_progress:
            on_progress(step_idx, total_steps, label, result.bytes_freed)

    label = "Файлы .log / .bak / .gid"
    if on_progress:
        on_progress(step_idx, total_steps, label, result.bytes_freed)
    freed, files, errs = _purge_extensions_in_dirs(safe_dirs, _JUNK_EXTENSIONS)
    result.bytes_freed += freed
    result.files_deleted += files
    result.errors += errs
    result.steps_done += 1
    step_idx += 1
    if on_progress:
        on_progress(step_idx, total_steps, label, result.bytes_freed)

    return result
