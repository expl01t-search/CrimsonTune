from __future__ import annotations

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak, service_revert, service_tweak
from utils.subprocess_helper import run_command, run_powershell


def ssd_enable_trim_apply() -> TweakResult:
    code, out, err = run_powershell(
        "Get-Volume | Where-Object { $_.DriveType -eq 'Fixed' -and $_.DriveLetter } | "
        "ForEach-Object { fsutil behavior set DisableDeleteNotify $_.DriveLetter`: 0 }"
    )
    msg = "TRIM включён на фиксированных томах" if code == 0 else (err or out)
    return TweakResult(code == 0, msg, revert_data={"trim": True})


def ssd_enable_trim_revert(_data) -> TweakResult:
    code, out, err = run_powershell(
        "Get-Volume | Where-Object { $_.DriveType -eq 'Fixed' -and $_.DriveLetter } | "
        "ForEach-Object { fsutil behavior set DisableDeleteNotify $_.DriveLetter`: 0 }"
    )
    return TweakResult(code == 0, "TRIM оставлен включённым" if code == 0 else err or out)


def ssd_disable_boot_defrag_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SOFTWARE\Microsoft\Dfrg\BootOptimizeFunction",
        "Enable",
        "N",
        "Y",
        value_type=winreg.REG_SZ,
        enabled=True,
    )


def ssd_disable_boot_defrag_revert(data) -> TweakResult:
    return reg_revert(data)


def ssd_disable_layout_ini_apply() -> TweakResult:
    return reg_batch_apply([
        (
            r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OptimalLayout",
            "EnableAutoLayout",
            0,
            1,
        ),
        (
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
            "ScenarioExecutionEnabled",
            0,
            1,
        ),
    ], message="Layout.ini / Prefetch scenario отключены")


def ssd_disable_layout_ini_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def ssd_disable_defrag_service_apply() -> TweakResult:
    return service_tweak("defragsvc", disabled=True)


def ssd_disable_defrag_service_revert(data) -> TweakResult:
    return service_revert(data)


def ssd_disable_system_restore_apply() -> TweakResult:
    run_powershell("Disable-ComputerRestore -Drive $env:SystemDrive -ErrorAction SilentlyContinue")
    return reg_batch_apply([
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows NT\SystemRestore", "DisableSR", 1, 0),
        (r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore", "DisableSR", 1, 0),
    ], message="Защита системы (восстановление) отключена")


def ssd_disable_system_restore_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def ssd_disable_scheduled_defrag_apply() -> TweakResult:
    tasks = (
        r"\Microsoft\Windows\Defrag\ScheduledDefrag",
        r"\Microsoft\Windows\Defrag\ScheduledDefrag\ScheduledDefrag",
    )
    for task in tasks:
        run_command(["schtasks", "/Change", "/TN", task, "/DISABLE"])
    run_powershell(
        "Get-ScheduledTask -TaskPath '\\Microsoft\\Windows\\Defrag\\' -ErrorAction SilentlyContinue | "
        "Disable-ScheduledTask -ErrorAction SilentlyContinue | Out-Null"
    )
    return TweakResult(True, "Плановая дефрагментация отключена", revert_data={"defrag_tasks": True})


def ssd_disable_scheduled_defrag_revert(_data) -> TweakResult:
    run_powershell(
        "Get-ScheduledTask -TaskPath '\\Microsoft\\Windows\\Defrag\\' -ErrorAction SilentlyContinue | "
        "Enable-ScheduledTask -ErrorAction SilentlyContinue | Out-Null"
    )
    return TweakResult(True, "Плановая дефрагментация включена")


def ssd_disable_superfetch_prefetch_apply() -> TweakResult:
    return reg_batch_apply([
        (
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
            "EnablePrefetcher",
            0,
            3,
        ),
        (
            r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
            "EnableSuperfetch",
            0,
            3,
        ),
    ], message="Prefetch и Superfetch отключены (SSD)")


def ssd_disable_superfetch_prefetch_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def ssd_disable_volume_indexing_apply() -> TweakResult:
    code, out, err = run_powershell(
        "Get-CimInstance -ClassName Win32_Volume -Filter \"DriveType=3\" | "
        "ForEach-Object { $_.IndexingEnabled = $false; Set-CimInstance $_ }"
    )
    if code != 0:
        code, out, err = run_powershell(
            "Get-WmiObject Win32_Volume -Filter 'DriveType=3' | "
            "ForEach-Object { $_.IndexingEnabled = $false; $_.Put() | Out-Null }"
        )
    return TweakResult(
        code == 0,
        "Индексирование содержимого на дисках отключено" if code == 0 else err or out,
        revert_data={"indexing": True},
    )


def ssd_disable_volume_indexing_revert(_data) -> TweakResult:
    return TweakResult(True, "Включите индексирование в свойствах диска при необходимости")


HANDLERS = {
    "ssd_enable_trim": (ssd_enable_trim_apply, ssd_enable_trim_revert),
    "ssd_disable_boot_defrag": (ssd_disable_boot_defrag_apply, ssd_disable_boot_defrag_revert),
    "ssd_disable_layout_ini": (ssd_disable_layout_ini_apply, ssd_disable_layout_ini_revert),
    "ssd_disable_defrag_service": (ssd_disable_defrag_service_apply, ssd_disable_defrag_service_revert),
    "ssd_disable_system_restore": (ssd_disable_system_restore_apply, ssd_disable_system_restore_revert),
    "ssd_disable_scheduled_defrag": (ssd_disable_scheduled_defrag_apply, ssd_disable_scheduled_defrag_revert),
    "ssd_disable_superfetch_prefetch": (ssd_disable_superfetch_prefetch_apply, ssd_disable_superfetch_prefetch_revert),
    "ssd_disable_volume_indexing": (ssd_disable_volume_indexing_apply, ssd_disable_volume_indexing_revert),
}
