
from __future__ import annotations

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert
from utils.gpu_reg import GPU_CLASS_GUID
from utils.subprocess_helper import run_command, run_powershell


def nvidia_disable_preemption_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler", "EnablePreemption", 0, 1),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "DisablePreemption", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "DisableCudaContextPreemption", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\GpuEnergyDrv", "Start", 4, 2),
    ], message="NVIDIA preemption отключён")


def nvidia_disable_preemption_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def nvidia_disable_pstate_apply() -> TweakResult:
    base = rf"HKLM\SYSTEM\CurrentControlSet\Control\Class\{GPU_CLASS_GUID}"
    entries = [(f"{base}\\000{i}", "DisableDynamicPstate", 1, 0) for i in range(8)]
    return reg_batch_apply(entries, message="NVIDIA P-State отключён (DisableDynamicPstate)")


def nvidia_disable_pstate_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def nvidia_disable_telemetry_apply() -> TweakResult:
    run_command(["sc", "stop", "NvTelemetryContainer"])
    run_command(["sc", "config", "NvTelemetryContainer", "start=", "disabled"])
    for pattern in ("NvTmMon", "NvTmRep", "NvTmRepOnLogon", "NvProfileUpdaterDaily", "NvProfileUpdaterOnLogon"):
        run_powershell(
            f"Get-ScheduledTask | Where-Object {{ $_.TaskName -like '*{pattern}*' }} | "
            "Disable-ScheduledTask -ErrorAction SilentlyContinue | Out-Null"
        )
    reg_batch_apply([
        (r"HKCU\SOFTWARE\NVIDIA Corporation\NVControlPanel2\Client", "OptInOrOutPreference", 0, 1),
    ], message="NVIDIA Telemetry отключена")
    return TweakResult(True, "NVIDIA Telemetry отключена")


def nvidia_disable_telemetry_revert(_data) -> TweakResult:
    run_command(["sc", "config", "NvTelemetryContainer", "start=", "demand"])
    return TweakResult(True, "Включите телеметрию в NVIDIA Control Panel при необходимости")


def nvidia_max_frame_latency_apply() -> TweakResult:
    base = rf"HKLM\SYSTEM\CurrentControlSet\Control\Class\{GPU_CLASS_GUID}"
    entries = [(f"{base}\\000{i}", "MaxFrameLatency", 1, 0) for i in range(8)]
    return reg_batch_apply(entries, message="NVIDIA MaxFrameLatency=1 (меньше input lag)")


def nvidia_max_frame_latency_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def nvidia_disable_runtime_pm_apply() -> TweakResult:
    base = rf"HKLM\SYSTEM\CurrentControlSet\Control\Class\{GPU_CLASS_GUID}"
    entries = [(f"{base}\\000{i}", "EnableRuntimePowerManagement", 0, 1) for i in range(8)]
    return reg_batch_apply(entries, message="NVIDIA runtime power management отключён")


def nvidia_disable_runtime_pm_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def nvidia_driver_perf_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "EnableMClkSlowdown", 0, 1),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "EnableNVClkSlowdown", 0, 1),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\nvlddmkm", "RmGpsEnableGlobalPerfOpt", 1, 0),
        (r"HKLM\SOFTWARE\NVIDIA Corporation\Global\NVTweak", "DisplayPowerSaving", 0, 1),
    ], message="NVIDIA driver perf tweaks применены")


def nvidia_driver_perf_revert(data) -> TweakResult:
    return reg_batch_revert(data)


HANDLERS = {
    "nvidia_disable_preemption": (nvidia_disable_preemption_apply, nvidia_disable_preemption_revert),
    "nvidia_disable_pstate": (nvidia_disable_pstate_apply, nvidia_disable_pstate_revert),
    "nvidia_disable_telemetry": (nvidia_disable_telemetry_apply, nvidia_disable_telemetry_revert),
    "nvidia_max_frame_latency": (nvidia_max_frame_latency_apply, nvidia_max_frame_latency_revert),
    "nvidia_disable_runtime_pm": (nvidia_disable_runtime_pm_apply, nvidia_disable_runtime_pm_revert),
    "nvidia_driver_perf": (nvidia_driver_perf_apply, nvidia_driver_perf_revert),
}
