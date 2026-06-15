
from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_revert, reg_tweak, service_revert, service_tweak


def disable_telemetry_apply() -> TweakResult:
    r1 = reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
        "AllowTelemetry", 0, 1, enabled=True,
    )
    r2 = service_tweak("DiagTrack", disabled=True)
    r3 = service_tweak("dmwappushservice", disabled=True)
    ok = r1.success or r2.success
    return TweakResult(ok, "Телеметрия отключена", revert_data={"telemetry": True})


def disable_telemetry_revert(_data) -> TweakResult:
    from utils.subprocess_helper import set_service_start_type

    reg_tweak(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 1, 0, enabled=False)
    set_service_start_type("DiagTrack", "auto")
    set_service_start_type("dmwappushservice", "auto")
    return TweakResult(True, "Телеметрия восстановлена")


def disable_advertising_id_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
        "Enabled", 0, 1, enabled=True,
    )


def disable_advertising_id_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_cortana_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search",
        "AllowCortana", 0, 1, enabled=True,
    )


def disable_cortana_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_location_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
        "Value", "Deny", "Allow",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def disable_location_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_feedback_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Siuf\Rules",
        "NumberOfSIUFInPeriod", 0, 1, enabled=True,
    )


def disable_feedback_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_tailored_experiences_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Privacy",
        "TailoredExperiencesWithDiagnosticDataEnabled", 0, 1, enabled=True,
    )


def disable_tailored_experiences_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_app_tracking_apply() -> TweakResult:
    return reg_tweak(
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Privacy",
        "LetAppsAccessAccountInfo", 0, 1, enabled=True,
    )


def disable_app_tracking_revert(data) -> TweakResult:
    return reg_revert(data)


HANDLERS = {
    "disable_telemetry": (disable_telemetry_apply, disable_telemetry_revert),
    "disable_advertising_id": (disable_advertising_id_apply, disable_advertising_id_revert),
    "disable_cortana": (disable_cortana_apply, disable_cortana_revert),
    "disable_location": (disable_location_apply, disable_location_revert),
    "disable_feedback": (disable_feedback_apply, disable_feedback_revert),
    "disable_tailored_experiences": (disable_tailored_experiences_apply, disable_tailored_experiences_revert),
    "disable_app_tracking": (disable_app_tracking_apply, disable_app_tracking_revert),
}
