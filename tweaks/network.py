
from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak
from utils.subprocess_helper import run_command, run_powershell


def set_dns_cloudflare_apply() -> TweakResult:
    script = (
        "Get-NetAdapter | Where-Object Status -eq 'Up' | ForEach-Object { "
        "Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses ('1.1.1.1','1.0.0.1') }"
    )
    code, out, err = run_powershell(script)
    return TweakResult(code == 0, "DNS Cloudflare установлен" if code == 0 else err, revert_data={"dns": "cloudflare"})


def set_dns_cloudflare_revert(_data) -> TweakResult:
    script = (
        "Get-NetAdapter | Where-Object Status -eq 'Up' | ForEach-Object { "
        "Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }"
    )
    code, _, err = run_powershell(script)
    return TweakResult(code == 0, "DNS сброшен на DHCP" if code == 0 else err)


def set_dns_google_apply() -> TweakResult:
    script = (
        "Get-NetAdapter | Where-Object Status -eq 'Up' | ForEach-Object { "
        "Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses ('8.8.8.8','8.8.4.4') }"
    )
    code, out, err = run_powershell(script)
    return TweakResult(code == 0, "DNS Google установлен" if code == 0 else err, revert_data={"dns": "google"})


def set_dns_google_revert(_data) -> TweakResult:
    return set_dns_cloudflare_revert(_data)


def flush_dns_apply() -> TweakResult:
    code, out, err = run_command(["ipconfig", "/flushdns"])
    return TweakResult(code == 0, "DNS кэш очищен" if code == 0 else err)


def flush_dns_revert(_data) -> TweakResult:
    return TweakResult(True, "Не требуется")


def disable_nagle_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpAckFrequency", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TCPNoDelay", 1, 0),
    ], message="Nagle отключён")


def disable_nagle_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def network_throttling_disable_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
        "NetworkThrottlingIndex", 0xFFFFFFFF, 10, enabled=True,
    )


def network_throttling_disable_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_qos_apply() -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "autotuninglevel=disabled"])
    return TweakResult(code == 0, "Auto-tuning отключён" if code == 0 else err, revert_data={"qos": True})


def disable_qos_revert(_data) -> TweakResult:
    code, out, err = run_command(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"])
    return TweakResult(code == 0, out or err)


def reset_winsock_apply() -> TweakResult:
    code, out, err = run_command(["netsh", "winsock", "reset"])
    return TweakResult(
        code == 0,
        "Winsock сброшен. Требуется перезагрузка." if code == 0 else err,
        revert_data=None,
    )


def reset_winsock_revert(_data) -> TweakResult:
    return TweakResult(True, "Сброс Winsock необратим")


HANDLERS = {
    "set_dns_cloudflare": (set_dns_cloudflare_apply, set_dns_cloudflare_revert),
    "set_dns_google": (set_dns_google_apply, set_dns_google_revert),
    "flush_dns": (flush_dns_apply, flush_dns_revert),
    "disable_nagle": (disable_nagle_apply, disable_nagle_revert),
    "network_throttling_disable": (network_throttling_disable_apply, network_throttling_disable_revert),
    "disable_tcp_autotuning": (disable_qos_apply, disable_qos_revert),
    "reset_winsock": (reset_winsock_apply, reset_winsock_revert),
}
