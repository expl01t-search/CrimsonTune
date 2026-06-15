
from __future__ import annotations

import re
from pathlib import Path

import winreg

from tweaks.base import TweakResult
from tweaks.helpers import reg_batch_apply, reg_batch_revert, reg_revert, reg_tweak, services_batch_apply, services_batch_revert
from utils.subprocess_helper import run_command, run_powershell

_AUTO_DISABLE_SERVICES = [
    "PeerDistSvc", "diagsvc", "Dnscache", "GraphicsPerfSvc", "AppVClient", "shpamsvc", "smphost",
    "SysMain", "UsoSvc", "WSearch", "WaaSMedicSvc", "cbdhsvc", "XboxGipSvc", "tzautoupdate",
    "WwanSvc", "CscService", "wmiApSrv", "WbioSrvc", "mpssvc", "WebClient", "iphlpsvc", "p2psvc",
    "RasAuto", "Spooler", "SEMgrSvc", "RasMan", "XblAuthManager", "MapsBroker", "hidserv", "pla",
    "DusmSvc", "TrkWks", "SNMPTRAP", "RpcLocator", "RemoteAccess", "lmhosts", "SessionEnv",
    "SharedAccess", "defragsvc", "DoSvc", "UmRdpService", "wercplsupport", "SCPolicySvc",
    "BcastDVRUserService", "WpnUserService", "wlidsvc", "NcaSvc", "NcbService", "SDRSVC", "swprv",
    "FDResPub", "LanmanWorkstation", "PrintNotify", "WpcMonSvc", "Wecsvc", "LanmanServer",
    "FrameServer", "XboxNetApiSvc", "Netlogon", "AssignedAccessManagerSvc", "vmicvmsession",
    "NgcSvc", "PushToInstall", "LicenseManager", "icssvc", "UevAgentService", "vmicrdv", "spectrum",
    "lfsvc", "UserDataSvc", "vmicshutdown", "stisvc", "vmicvss", "MSiSCSI", "fhsvc",
    "PimIndexMaintenanceSvc", "WalletService", "FontCache", "ClipSVC", "SmsRouter", "dmwappushservice",
    "wbengine", "irmon", "SensrSvc", "vmickvpexchange", "ScDeviceEnum", "WPDBusEnum", "PcaSvc",
    "wisvc", "vmicheartbeat", "TabletInputService", "vmictimesync", "WpnService", "SENS", "WinRM",
    "WEPHOSTSVC", "RmSvc", "InstallService", "BDESVC", "ALG", "TermService", "SCardSvr", "WiaRpc",
    "XblGameSave", "diagnosticshub.standardcollector.service", "TapiSrv", "PhoneSvc", "VSS",
    "RemoteRegistry", "AppIDSvc", "vmicguestinterface", "Fax", "BITS", "DiagTrack", "PerfHost",
    "wscsvc", "wuauserv", "PolicyAgent", "IKEEXT", "Themes", "SensorDataService", "SensorService",
    "WerSvc", "Ndu",
]


def disable_defender_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer", "SmartScreenEnabled", "off", "on", winreg.REG_SZ),
        (r"HKLM\SOFTWARE\Policies\Microsoft\MicrosoftEdge\PhishingFilter", "EnabledV9", 0, 1),
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "EnableSmartScreen", 0, 1),
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\SecurityHealthService", "Start", 4, 3),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\wscsvc", "Start", 4, 3),
        (r"HKCU\Software\Microsoft\Windows\CurrentVersion\AppHost", "EnableWebContentEvaluation", 0, 1),
    ], message="Windows Defender и SmartScreen отключены")


def disable_defender_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_firewall_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Services\mpssvc",
        "Start", 4, 3, enabled=True,
    )


def disable_firewall_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_dns_cache_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Services\Dnscache",
        "Start", 4, 2, enabled=True,
    )


def disable_dns_cache_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_windows_update_completely_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU", "NoAutoUpdate", 1, 0),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\wuauserv", "Start", 4, 3),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\UsoSvc", "Start", 4, 3),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\WaaSMedicSvc", "Start", 4, 3),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\DoSvc", "Start", 4, 3),
    ], message="Windows Update отключён")


def disable_windows_update_completely_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def disable_all_services_apply() -> TweakResult:
    return services_batch_apply(_AUTO_DISABLE_SERVICES, disabled=True, message="Массовое отключение служб применено")


def disable_all_services_revert(data) -> TweakResult:
    return services_batch_revert(data)


def disable_documents_tracking_apply() -> TweakResult:
    return reg_tweak(
        r"HKLM\SYSTEM\CurrentControlSet\Services\CDPUserSvc",
        "Start", 4, 3, enabled=True,
    )


def disable_documents_tracking_revert(data) -> TweakResult:
    return reg_revert(data)


def disable_delivery_optimization_full_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization", "DOUploadMode", 0, 1),
        (r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization", "DODownloadMode", 0, 1),
        (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization", "SystemSettingsDownloadMode", 0, 1),
        (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization", "DownloadMode", 0, 1),
        (r"HKLM\SYSTEM\CurrentControlSet\Services\DoSvc", "Start", 4, 3),
    ], message="Delivery Optimization полностью отключён")


def disable_delivery_optimization_full_revert(data) -> TweakResult:
    return reg_batch_revert(data)


def gray_selection_color_apply() -> TweakResult:
    return reg_batch_apply([
        (r"HKCU\Control Panel\Colors", "Hilight", "128 128 128", "0 120 215", winreg.REG_SZ),
        (r"HKCU\Control Panel\Colors", "HilightText", "255 255 255", "255 255 255", winreg.REG_SZ),
    ], message="Серый цвет выделения применён")


def gray_selection_color_revert(data) -> TweakResult:
    return reg_batch_revert(data)


HANDLERS = {
    "disable_defender": (disable_defender_apply, disable_defender_revert),
    "disable_firewall": (disable_firewall_apply, disable_firewall_revert),
    "disable_dns_cache": (disable_dns_cache_apply, disable_dns_cache_revert),
    "disable_windows_update_completely": (disable_windows_update_completely_apply, disable_windows_update_completely_revert),
    "disable_all_services": (disable_all_services_apply, disable_all_services_revert),
    "disable_documents_tracking": (disable_documents_tracking_apply, disable_documents_tracking_revert),
    "disable_delivery_optimization_full": (disable_delivery_optimization_full_apply, disable_delivery_optimization_full_revert),
    "gray_selection_color": (gray_selection_color_apply, gray_selection_color_revert),
}
