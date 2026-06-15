
from __future__ import annotations

import winreg
from typing import Any, Optional

from tweaks.base import TweakResult
from utils import registry as reg
from utils.subprocess_helper import run_command, set_service_start_type, stop_service

RegEntry = tuple[str, str, Any, Any, int] | tuple[str, str, Any, Any] | tuple[str, str, Any]


def reg_tweak(
    path: str,
    name: str,
    enable_value: Any,
    disable_value: Any = 0,
    *,
    value_type: int = winreg.REG_DWORD,
    enabled: bool = True,
) -> TweakResult:
    old = reg.read_value(path, name, default=None)
    new_value = enable_value if enabled else disable_value
    try:
        reg.write_value(path, name, new_value, value_type)
        return TweakResult(
            True,
            "Применено" if enabled else "Отключено",
            revert_data={"path": path, "name": name, "old": old, "type": value_type},
        )
    except OSError as exc:
        return TweakResult(False, str(exc))


def reg_revert(data: Optional[dict]) -> TweakResult:
    if not data:
        return TweakResult(False, "Нет данных для отката")
    if "entries" in data:
        return reg_batch_revert(data)
    path, name = data["path"], data["name"]
    old = data.get("old")
    try:
        if old is None:
            reg.delete_value(path, name)
        else:
            reg.write_value(path, name, old, data.get("type", winreg.REG_DWORD))
        return TweakResult(True, "Откачено")
    except OSError as exc:
        return TweakResult(False, str(exc))


def _parse_reg_entry(entry: RegEntry) -> tuple[str, str, Any, Any, int]:
    path, name, enable_value = entry[0], entry[1], entry[2]
    disable_value = entry[3] if len(entry) > 3 else 0
    value_type = entry[4] if len(entry) > 4 else winreg.REG_DWORD
    return path, name, enable_value, disable_value, value_type


def reg_batch_apply(entries: list[RegEntry], *, message: str = "Применено") -> TweakResult:
    snapshots: list[dict] = []
    try:
        for entry in entries:
            path, name, enable_value, _, value_type = _parse_reg_entry(entry)
            old = reg.read_value(path, name, default=None)
            reg.write_value(path, name, enable_value, value_type)
            snapshots.append({"path": path, "name": name, "old": old, "type": value_type})
        return TweakResult(True, message, revert_data={"entries": snapshots})
    except OSError as exc:
        if snapshots:
            reg_batch_revert({"entries": snapshots})
        return TweakResult(False, str(exc))


def reg_batch_revert(data: Optional[dict]) -> TweakResult:
    entries = (data or {}).get("entries") or []
    if not entries:
        return TweakResult(False, "Нет данных для отката")
    errors: list[str] = []
    for snap in reversed(entries):
        result = reg_revert(snap)
        if not result.success:
            errors.append(result.message)
    if errors:
        return TweakResult(False, "; ".join(errors))
    return TweakResult(True, "Откачено")


def capture_reg_snapshot(path: str, name: str, value_type: int = winreg.REG_DWORD) -> dict:
    return {"path": path, "name": name, "old": reg.read_value(path, name, default=None), "type": value_type}


def service_tweak(service: str, disabled: bool = True) -> TweakResult:
    from utils.subprocess_helper import get_service_start_type

    original = get_service_start_type(service)
    if disabled:
        stop_service(service)
        code, msg = set_service_start_type(service, "disabled")
    else:
        code, msg = set_service_start_type(service, "auto")
    if code == 0:
        return TweakResult(
            True,
            msg,
            revert_data={"service": service, "disabled": disabled, "original": original},
        )
    return TweakResult(False, msg)


def services_batch_apply(services: list[str], *, disabled: bool = True, message: str = "Службы настроены") -> TweakResult:
    snapshots: list[dict] = []
    for service in services:
        result = service_tweak(service, disabled=disabled)
        if result.revert_data:
            snapshots.append(result.revert_data)
    ok = len(snapshots) == len(services)
    return TweakResult(ok, message if ok else "Частично применено", revert_data={"services": snapshots})


def services_batch_revert(data: Optional[dict]) -> TweakResult:
    snapshots = (data or {}).get("services") or []
    if not snapshots:
        return TweakResult(False, "Нет данных")
    for snap in snapshots:
        service = snap["service"]
        original = snap.get("original") or ("auto" if snap.get("disabled") else "disabled")
        set_service_start_type(service, original)
    return TweakResult(True, "Службы восстановлены")


def service_revert(data: Optional[dict]) -> TweakResult:
    if not data:
        return TweakResult(False, "Нет данных")
    if "services" in data:
        return services_batch_revert(data)
    service = data["service"]
    original = data.get("original")
    if original:
        code, msg = set_service_start_type(service, original)
    elif data.get("disabled"):
        code, msg = set_service_start_type(service, "auto")
    else:
        code, msg = set_service_start_type(service, "disabled")
    return TweakResult(code == 0, msg)


def power_plan_tweak(guid: str) -> TweakResult:
    code, out, err = run_command(["powercfg", "/setactive", guid])
    if code == 0:
        return TweakResult(True, "План питания активирован", revert_data={"guid": guid})
    return TweakResult(False, err or out)


def run_cmd_tweak(cmd: list[str], revert_cmd: Optional[list[str]] = None) -> TweakResult:
    code, out, err = run_command(cmd)
    if code == 0:
        return TweakResult(True, out or "Выполнено", revert_data={"revert_cmd": revert_cmd})
    return TweakResult(False, err or out)
