from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert
from tweaks.supplemental_catalog import SUPPLEMENTAL_TWEAKS, build_reg_handlers
from utils.nic_reg import active_interface_reg_paths
from utils.subprocess_helper import run_command, run_powershell

_COMMUNITY_REG_IDS = {
    "psched_non_best_effort_limit",
    "mmcss_games_full_priority",
    "wait_to_kill_service_timeout",
    "explorer_separate_process",
    "increase_icon_cache",
    "ntfs_disable_compression",
    "disable_nearby_sharing",
    "disable_autorun_all",
    "disable_edge_startup_boost",
    "verbose_status_messages",
    "disable_phone_link_policy",
}


def disable_nagle_nic_interfaces_apply() -> TweakResult:
    entries = []
    for path in active_interface_reg_paths():
        entries.extend([
            (path, "TcpAckFrequency", 1, 2),
            (path, "TCPNoDelay", 1, 0),
            (path, "TcpDelAckTicks", 0, 2),
        ])
    if not entries:
        return TweakResult(False, "Активные сетевые интерфейсы не найдены")
    return reg_batch_apply(entries, message="Nagle отключён на NIC (TcpAckFrequency/TCPNoDelay/TcpDelAckTicks)")


def disable_nagle_nic_interfaces_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_memory_compression_apply() -> TweakResult:
    code, out, err = run_powershell("Disable-MMACompression -ErrorAction SilentlyContinue")
    if code != 0 and "not recognized" in (err or out or "").lower():
        return TweakResult(False, "Disable-MMACompression недоступен на этой сборке Windows")
    return TweakResult(True, "Сжатие памяти Windows отключено", revert_data={"compressed": True})


def disable_memory_compression_revert(_data) -> TweakResult:
    code, out, err = run_powershell("Enable-MMACompression -ErrorAction SilentlyContinue")
    return TweakResult(code == 0, "Сжатие памяти включено" if code == 0 else err or out)


def tcp_ecn_gaming_apply() -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "ecncapability=enabled"])
    return TweakResult(code == 0, "TCP ECN включён (игровой низкий ping)" if code == 0 else err, revert_data={"ecn": True})


def tcp_ecn_gaming_revert(_data) -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "ecncapability=disabled"])
    return TweakResult(code == 0, out or err)


def tcp_congestion_ctcp_apply() -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "supplemental", "internet", "congestionprovider=ctcp"])
    if code != 0:
        code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "congestionprovider=ctcp"])
    return TweakResult(code == 0, "TCP congestion provider: CTCP" if code == 0 else err, revert_data={"ctcp": True})


def tcp_congestion_ctcp_revert(_data) -> TweakResult:
    code, _, _ = run_command(["netsh", "int", "tcp", "set", "supplemental", "internet", "congestionprovider=default"])
    if code != 0:
        code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "congestionprovider=default"])
    else:
        out, err = "", ""
    return TweakResult(code == 0, "TCP congestion provider сброшен" if code == 0 else err or out)


def disable_tcp_rsc_apply() -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "rsc=disabled"])
    return TweakResult(code == 0, "Receive Segment Coalescing отключён" if code == 0 else err, revert_data={"rsc": True})


def disable_tcp_rsc_revert(_data) -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "rsc=enabled"])
    return TweakResult(code == 0, out or err)


HANDLERS = {
    "disable_nagle_nic_interfaces": (disable_nagle_nic_interfaces_apply, disable_nagle_nic_interfaces_revert),
    "disable_memory_compression": (disable_memory_compression_apply, disable_memory_compression_revert),
    "tcp_ecn_gaming": (tcp_ecn_gaming_apply, tcp_ecn_gaming_revert),
    "tcp_congestion_ctcp": (tcp_congestion_ctcp_apply, tcp_congestion_ctcp_revert),
    "disable_tcp_rsc": (disable_tcp_rsc_apply, disable_tcp_rsc_revert),
}
HANDLERS.update(build_reg_handlers([t for t in SUPPLEMENTAL_TWEAKS if t.id in _COMMUNITY_REG_IDS]))
