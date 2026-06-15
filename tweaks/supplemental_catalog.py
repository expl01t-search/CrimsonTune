from __future__ import annotations

import winreg
from dataclasses import dataclass, field
from typing import Any, Callable

from utils.gpu_reg import gpu_adapter_path, microsoft_wow_pair

_DX = r"HKLM\SOFTWARE\Microsoft\DirectX"
_D3D = r"HKLM\SOFTWARE\Microsoft\Direct3D"
_D3D_DRV = r"HKLM\SOFTWARE\Microsoft\Direct3D\Drivers"
_DD = r"HKLM\SOFTWARE\Microsoft\DirectDraw"
_DX_GFX = r"HKCU\Software\Microsoft\DirectX\GraphicsSettings"
_HKCU_DX = r"HKCU\Software\DirectX"


@dataclass(frozen=True)
class SupplementalTweak:
    id: str
    name: str
    description: str
    category: str
    risk: str = "medium"
    requires_admin: bool = True
    requires_reboot: bool = True
    hint: str = ""
    source: str = "Custom-DirectX"
    gpu_vendor: list[str] = field(default_factory=lambda: ["all"])
    entries: list[tuple] = field(default_factory=list)
    en_name: str = ""
    en_description: str = ""
    en_hint: str = ""


def _meta(item: SupplementalTweak) -> dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "category": item.category,
        "risk": item.risk,
        "requires_admin": item.requires_admin,
        "requires_reboot": item.requires_reboot,
        "compatible_os": ["10.0"],
        "gpu_vendor": item.gpu_vendor,
        "source": item.source,
        "default": False,
        "hint": item.hint,
    }


def supplemental_meta_items() -> list[dict[str, Any]]:
    return [_meta(t) for t in SUPPLEMENTAL_TWEAKS]


def supplemental_en_strings() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for t in SUPPLEMENTAL_TWEAKS:
        if t.en_name:
            out[t.id] = {
                "name": t.en_name,
                "description": t.en_description or t.description,
                "hint": t.en_hint or t.hint,
            }
    return out


def build_reg_handlers(catalog: list[SupplementalTweak]) -> dict[str, tuple[Callable, Callable]]:
    from tweaks.helpers import reg_batch_apply, reg_batch_revert

    handlers: dict[str, tuple[Callable, Callable]] = {}
    for item in catalog:
        entries = item.entries
        if not entries:
            continue

        def make_apply(batch=entries, msg=item.name):
            def apply_fn():
                return reg_batch_apply(batch, message=f"Применено: {msg}")

            return apply_fn

        def make_revert():
            return reg_batch_revert

        handlers[item.id] = (make_apply(), make_revert())
    return handlers


def _gpu_entries(name: str, value, disable=0) -> list[tuple]:
    return [
        (gpu_adapter_path(0), name, value, disable),
        (gpu_adapter_path(1), name, value, disable),
    ]


def _d3d_pair(name: str, value, disable=0, value_type=None) -> list[tuple]:
    return microsoft_wow_pair("Direct3D", name, value, disable, value_type)


def _dd_pair(name: str, value, disable=0, value_type=None) -> list[tuple]:
    return microsoft_wow_pair("DirectDraw", name, value, disable, value_type)


def _d3d_drv_pair(name: str, value, disable=0, value_type=None) -> list[tuple]:
    return microsoft_wow_pair("Direct3D\\Drivers", name, value, disable, value_type)


SUPPLEMENTAL_TWEAKS: list[SupplementalTweak] = [
    SupplementalTweak(
        id="dx_game_performance_mode",
        name="DirectX: Game + Performance",
        description="PerformanceMode и GameMode в профиле DirectX",
        category="directx",
        risk="medium",
        requires_reboot=False,
        hint="Custom-DirectX · закройте игры перед применением",
        entries=[
            (_HKCU_DX, "PerformanceMode", 1, 0),
            (_HKCU_DX, "GameMode", 1, 0),
        ],
        en_name="DirectX: Game + Performance Mode",
        en_description="Enables PerformanceMode and GameMode in DirectX profile",
        en_hint="Custom-DirectX · close games before applying",
    ),
    SupplementalTweak(
        id="dx_flip_no_vsync",
        name="DirectX: отключить VSync (FlipNoVsync)",
        description="FlipNoVsync для Direct3D (32/64-bit)",
        category="directx",
        hint="Direct3D · не путать с OpenGL VSync",
        entries=_d3d_pair("FlipNoVsync", 1, 0),
        en_name="DirectX: Disable VSync (FlipNoVsync)",
        en_description="Sets FlipNoVsync for Direct3D (32/64-bit)",
        en_hint="Direct3D · not the same as OpenGL VSync",
    ),
    SupplementalTweak(
        id="dx_few_vertices",
        name="DirectX: Few Vertices",
        description="Оптимизация FewVertices для Direct3D",
        category="directx",
        entries=_d3d_pair("FewVertices", 1, 0),
        en_name="DirectX: Few Vertices",
        en_description="Enables FewVertices optimization for Direct3D",
    ),
    SupplementalTweak(
        id="dx_enable_printscreen",
        name="DirectX: PrintScreen в DirectDraw",
        description="EnablePrintScreen для DirectDraw",
        category="directx",
        requires_reboot=False,
        entries=_dd_pair("EnablePrintScreen", 1, 0),
        en_name="DirectX: Enable PrintScreen (DirectDraw)",
        en_description="Enables PrintScreen capture in DirectDraw",
    ),
    SupplementalTweak(
        id="dx_vulkan_topology",
        name="DirectX/Vulkan: Virtual Topology",
        description="EnableVirtualTopologySupport на GPU-адаптере",
        category="directx",
        entries=_gpu_entries("EnableVirtualTopologySupport", 1, 0),
        en_name="DirectX/Vulkan: Virtual Topology",
        en_description="EnableVirtualTopologySupport on the GPU adapter",
    ),
    SupplementalTweak(
        id="dx_gpu_latency",
        name="DirectX: снизить задержку GPU",
        description="PreferSystemMemoryContiguous=0 на адаптерах GPU",
        category="directx",
        entries=_gpu_entries("PreferSystemMemoryContiguous", 0, 1),
        en_name="DirectX: Reduce GPU Latency",
        en_description="PreferSystemMemoryContiguous=0 on GPU adapters",
    ),
    SupplementalTweak(
        id="dx_directdraw_unlock",
        name="DirectDraw: NoSysLock + ModeX",
        description="ForceNoSysLock=0 и ModeXOnly=0",
        category="directx",
        requires_reboot=False,
        entries=[
            *_dd_pair("ForceNoSysLock", 0, 1),
            *_dd_pair("ModeXOnly", 0, 1),
        ],
        en_name="DirectDraw: NoSysLock + ModeX",
        en_description="Sets ForceNoSysLock=0 and ModeXOnly=0",
    ),
    SupplementalTweak(
        id="dx_mmx_enable",
        name="DirectX: включить MMX",
        description="DisableMMX=0 для DirectDraw и Direct3D",
        category="directx",
        risk="high",
        entries=[
            *_dd_pair("DisableMMX", 0, 1),
            *_d3d_pair("DisableMMX", 0, 1),
        ],
        en_name="DirectX: Enable MMX",
        en_description="Sets DisableMMX=0 for DirectDraw and Direct3D",
    ),
    SupplementalTweak(
        id="dx_mmx_fastpath",
        name="DirectX: MMX Fast Path",
        description="MMX Fast Path и MMXFastPath",
        category="directx",
        risk="high",
        entries=[
            *_d3d_pair("MMX Fast Path", 1, 0, winreg.REG_DWORD),
            *_d3d_pair("MMXFastPath", 1, 0),
        ],
        en_name="DirectX: MMX Fast Path",
        en_description="Enables MMX Fast Path and MMXFastPath",
    ),
    SupplementalTweak(
        id="dx_mmx_rgb",
        name="DirectX: MMX for RGB",
        description="UseMMXForRGB в Direct3D и Drivers",
        category="directx",
        risk="high",
        entries=[
            *_d3d_pair("UseMMXForRGB", 1, 0),
            *_d3d_drv_pair("UseMMXForRGB", 1, 0),
        ],
        en_name="DirectX: MMX for RGB",
        en_description="UseMMXForRGB in Direct3D and Drivers",
    ),
    SupplementalTweak(
        id="dx_enum_separate_mmx",
        name="DirectX: EnumSeparateMMX",
        description="EnumSeparateMMX в Direct3D Drivers",
        category="directx",
        risk="high",
        entries=_d3d_drv_pair("EnumSeparateMMX", 1, 0),
        en_name="DirectX: EnumSeparateMMX",
        en_description="EnumSeparateMMX in Direct3D Drivers",
    ),
    SupplementalTweak(
        id="dx_legacy_vidmem",
        name="DirectX: AGP и VRAM (legacy)",
        description="AGP texturing, UseNonLocalVidMem и VGABuffer",
        category="directx",
        risk="high",
        entries=[
            *_dd_pair("DisableAGPSupport", 0, 1),
            *_dd_pair("UseNonLocalVidMem", 1, 0),
            *_d3d_pair("UseNonLocalVidMem", 1, 0),
            *_dd_pair("VGABuffer", 21181233, 0),
            *_d3d_pair("VGABuffer", 21181233, 0),
            (r"HKLM\SOFTWARE\Microsoft\DirectMusic", "VGABuffer", 21181233, 0),
            (r"HKLM\SOFTWARE\Wow6432Node\Microsoft\DirectMusic", "VGABuffer", 21181233, 0),
        ],
        en_name="DirectX: AGP & VRAM (legacy)",
        en_description="AGP texturing, UseNonLocalVidMem and VGABuffer tweaks",
    ),
    SupplementalTweak(
        id="dx_hardware_acceleration",
        name="DirectX: аппаратное ускорение",
        description="Point sprites, state blocks, rasterizer, DDSCAPS, DirectDraw HW, MIDI HW",
        category="directx",
        entries=[
            *_dd_pair("EmulatePointSprites", 0, 1),
            *_dd_pair("EmulateStateBlocks", 0, 1),
            *_d3d_drv_pair("ForceRgbRasterizer", 0, 1),
            *_dd_pair("DisableDDSCAPSInDDSD", 0, 1),
            *_dd_pair("EmulationOnly", 0, 1),
            (r"HKLM\SOFTWARE\Microsoft\DirectMusic", "DisableHWAcceleration", 0, 1),
            (r"HKLM\SOFTWARE\Wow6432Node\Microsoft\DirectMusic", "DisableHWAcceleration", 0, 1),
        ],
        en_name="DirectX: Hardware Acceleration Pack",
        en_description="Hardware flags for DirectDraw/Direct3D/DirectMusic",
    ),
    SupplementalTweak(
        id="dx_disable_d3d_debug",
        name="DirectX: отключить отладку D3D",
        description="EnableDebugging, FullDebug, DisableDM, MultimonDebugging, LoadDebugRuntime",
        category="directx",
        requires_reboot=False,
        entries=[
            (_D3D, "EnableDebugging", 0, 1),
            (_D3D, "FullDebug", 0, 1),
            (_D3D, "DisableDM", 1, 0),
            (_D3D, "EnableMultimonDebugging", 0, 1),
            (_D3D, "LoadDebugRuntime", 0, 1),
        ],
        en_name="DirectX: Disable D3D Debug",
        en_description="Disables Direct3D debugging and debug runtime",
    ),
    SupplementalTweak(
        id="dx_graphics_settings",
        name="DirectX: Graphics Settings",
        description="SwapEffectUpgradeCache и SpecificGPUOptionApplicable",
        category="directx",
        requires_reboot=False,
        entries=[
            (_DX_GFX, "SwapEffectUpgradeCache", 1, 0),
            (_DX_GFX, "SpecificGPUOptionApplicable", 1, 0),
        ],
        en_name="DirectX: Graphics Settings",
        en_description="SwapEffectUpgradeCache and SpecificGPUOptionApplicable",
    ),
    SupplementalTweak(
        id="dx_d3d12_unsafe_buffer",
        name="D3D12: Unsafe Command Buffer",
        description="D3D12_ENABLE_UNSAFE_COMMAND_BUFFER_REUSE",
        category="directx",
        risk="high",
        entries=[(_DX, "D3D12_ENABLE_UNSAFE_COMMAND_BUFFER_REUSE", 1, 0)],
        en_name="D3D12: Unsafe Command Buffer",
        en_description="D3D12_ENABLE_UNSAFE_COMMAND_BUFFER_REUSE",
    ),
    SupplementalTweak(
        id="dx_d3d12_runtime_opts",
        name="D3D12: Runtime Optimizations",
        description="D3D12_ENABLE_RUNTIME_DRIVER_OPTIMIZATIONS",
        category="directx",
        entries=[(_DX, "D3D12_ENABLE_RUNTIME_DRIVER_OPTIMIZATIONS", 1, 0)],
        en_name="D3D12: Runtime Optimizations",
        en_description="D3D12_ENABLE_RUNTIME_DRIVER_OPTIMIZATIONS",
    ),
    SupplementalTweak(
        id="dx_d3d12_resource_alignment",
        name="D3D12: Resource Alignment",
        description="D3D12_RESOURCE_ALIGNMENT",
        category="directx",
        entries=[(_DX, "D3D12_RESOURCE_ALIGNMENT", 1, 0)],
        en_name="D3D12: Resource Alignment",
        en_description="D3D12_RESOURCE_ALIGNMENT",
    ),
    SupplementalTweak(
        id="dx_d3d11_multithreaded",
        name="D3D11: Multithreaded",
        description="D3D11_MULTITHREADED",
        category="directx",
        entries=[(_DX, "D3D11_MULTITHREADED", 1, 0)],
        en_name="D3D11: Multithreaded",
        en_description="D3D11_MULTITHREADED",
    ),
    SupplementalTweak(
        id="dx_d3d12_multithreaded",
        name="D3D12: Multithreaded",
        description="D3D12_MULTITHREADED",
        category="directx",
        entries=[(_DX, "D3D12_MULTITHREADED", 1, 0)],
        en_name="D3D12: Multithreaded",
        en_description="D3D12_MULTITHREADED",
    ),
    SupplementalTweak(
        id="dx_d3d11_deferred_contexts",
        name="D3D11: Deferred Contexts",
        description="D3D11_DEFERRED_CONTEXTS",
        category="directx",
        entries=[(_DX, "D3D11_DEFERRED_CONTEXTS", 1, 0)],
        en_name="D3D11: Deferred Contexts",
        en_description="D3D11_DEFERRED_CONTEXTS",
    ),
    SupplementalTweak(
        id="dx_d3d12_deferred_contexts",
        name="D3D12: Deferred Contexts",
        description="D3D12_DEFERRED_CONTEXTS",
        category="directx",
        entries=[(_DX, "D3D12_DEFERRED_CONTEXTS", 1, 0)],
        en_name="D3D12: Deferred Contexts",
        en_description="D3D12_DEFERRED_CONTEXTS",
    ),
    SupplementalTweak(
        id="dx_d3d11_allow_tiling",
        name="D3D11: Allow Tiling",
        description="D3D11_ALLOW_TILING",
        category="directx",
        entries=[(_DX, "D3D11_ALLOW_TILING", 1, 0)],
        en_name="D3D11: Allow Tiling",
        en_description="D3D11_ALLOW_TILING",
    ),
    SupplementalTweak(
        id="dx_d3d11_dynamic_codegen",
        name="D3D11: Dynamic Codegen",
        description="D3D11_ENABLE_DYNAMIC_CODEGEN",
        category="directx",
        entries=[(_DX, "D3D11_ENABLE_DYNAMIC_CODEGEN", 1, 0)],
        en_name="D3D11: Dynamic Codegen",
        en_description="D3D11_ENABLE_DYNAMIC_CODEGEN",
    ),
    SupplementalTweak(
        id="dx_d3d12_allow_tiling",
        name="D3D12: Allow Tiling",
        description="D3D12_ALLOW_TILING",
        category="directx",
        entries=[(_DX, "D3D12_ALLOW_TILING", 1, 0)],
        en_name="D3D12: Allow Tiling",
        en_description="D3D12_ALLOW_TILING",
    ),
    SupplementalTweak(
        id="dx_d3d12_cpu_page_table",
        name="D3D12: CPU Page Table",
        description="D3D12_CPU_PAGE_TABLE_ENABLED",
        category="directx",
        entries=[(_DX, "D3D12_CPU_PAGE_TABLE_ENABLED", 1, 0)],
        en_name="D3D12: CPU Page Table",
        en_description="D3D12_CPU_PAGE_TABLE_ENABLED",
    ),
    SupplementalTweak(
        id="dx_d3d12_heap_serialization",
        name="D3D12: Heap Serialization",
        description="D3D12_HEAP_SERIALIZATION_ENABLED",
        category="directx",
        entries=[(_DX, "D3D12_HEAP_SERIALIZATION_ENABLED", 1, 0)],
        en_name="D3D12: Heap Serialization",
        en_description="D3D12_HEAP_SERIALIZATION_ENABLED",
    ),
    SupplementalTweak(
        id="dx_d3d12_map_heap",
        name="D3D12: Map Heap Allocations",
        description="D3D12_MAP_HEAP_ALLOCATIONS",
        category="directx",
        entries=[(_DX, "D3D12_MAP_HEAP_ALLOCATIONS", 1, 0)],
        en_name="D3D12: Map Heap Allocations",
        en_description="D3D12_MAP_HEAP_ALLOCATIONS",
    ),
    SupplementalTweak(
        id="dx_d3d12_residency",
        name="D3D12: Residency Management",
        description="D3D12_RESIDENCY_MANAGEMENT_ENABLED",
        category="directx",
        entries=[(_DX, "D3D12_RESIDENCY_MANAGEMENT_ENABLED", 1, 0)],
        en_name="D3D12: Residency Management",
        en_description="D3D12_RESIDENCY_MANAGEMENT_ENABLED",
    ),
    # --- Optimize #Expl01t · Доп твики ---
    SupplementalTweak(
        id="boost_tcp_stack",
        name="Boost TCP (Optimize #Expl01t)",
        description="Пакет TCP/AFD/Lanman из Boost-TCP.reg",
        category="network",
        risk="medium",
        requires_reboot=True,
        source="Optimize #Expl01t",
        hint="Boost-TCP.reg · при сбоях сети используйте откат",
        entries=[
            (r"HKLM\SYSTEM\CurrentControlSet\services\Tcpip\Parameters", "DefaultTTL", 0x40, 0x80),
            (r"HKLM\SYSTEM\CurrentControlSet\services\Tcpip\Parameters", "EnableDCA", 1, 0),
            (r"HKLM\SYSTEM\CurrentControlSet\services\Tcpip\Parameters", "EnableTCPA", 1, 0),
            (r"HKLM\SYSTEM\CurrentControlSet\services\Tcpip\Parameters", "DisableTaskOffload", 0, 1),
            (r"HKLM\SYSTEM\CurrentControlSet\services\Tcpip\Parameters", "Tcp1323Opts", 1, 0),
            (r"HKLM\SYSTEM\CurrentControlSet\services\Tcpip\Parameters", "TcpTimedWaitDelay", 0x1E, 0x78),
            (r"HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters", "EnableDynamicBacklog", 1, 0),
            (r"HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters", "MinimumDynamicBacklog", 0xC8, 0x10),
            (r"HKLM\SYSTEM\CurrentControlSet\services\LanmanWorkstation\Parameters", "DisableBandwidthThrottling", 1, 0),
            (r"HKLM\SOFTWARE\Microsoft\MSMQ\Parameters", "TCPNoDelay", 1, 0),
            (r"HKLM\System\CurrentControlSet\Services\LanmanServer\Parameters", "SizReqBuf", 0x4410, 0x1104),
        ],
        en_name="Boost TCP Stack",
        en_description="TCP/AFD/Lanman tuning from Boost-TCP.reg",
        en_hint="Optimize #Expl01t · revert if networking issues appear",
    ),
    SupplementalTweak(
        id="disable_cpu_mitigations",
        name="Отключить CPU mitigations",
        description="FeatureSettingsOverride/Mask — снижает защиту Spectre/Meltdown",
        category="expert",
        risk="high",
        source="Optimize #Expl01t",
        hint="Disable Mitigations.reg · высокий риск безопасности",
        entries=[
            (
                r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                "FeatureSettingsOverride",
                3,
                0,
            ),
            (
                r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                "FeatureSettingsOverrideMask",
                3,
                0,
            ),
        ],
        en_name="Disable CPU Mitigations",
        en_description="FeatureSettingsOverride/Mask — reduces Spectre/Meltdown protections",
        en_hint="Disable Mitigations.reg · high security risk",
    ),
    SupplementalTweak(
        id="disable_uac",
        name="Отключить UAC",
        description="Полное отключение контроля учётных записей",
        category="expert",
        risk="high",
        requires_reboot=True,
        source="Optimize #Expl01t",
        hint="UAC OFF · только для опытных пользователей",
        entries=[
            (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "EnableLUA", 0, 1),
            (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "ConsentPromptBehaviorAdmin", 0, 5),
            (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "PromptOnSecureDesktop", 0, 1),
        ],
        en_name="Disable UAC",
        en_description="Fully disables User Account Control",
        en_hint="UAC OFF · advanced users only",
    ),
    SupplementalTweak(
        id="disable_notification_center",
        name="Отключить Центр уведомлений",
        description="DisableNotificationCenter=1",
        category="privacy",
        risk="safe",
        requires_admin=False,
        requires_reboot=False,
        source="Optimize #Expl01t",
        entries=[
            (r"HKCU\Software\Policies\Microsoft\Windows\Explorer", "DisableNotificationCenter", 1, 0),
        ],
        en_name="Disable Notification Center",
        en_description="DisableNotificationCenter=1",
    ),
    SupplementalTweak(
        id="hide_quick_access",
        name="Скрыть «Быстрый доступ»",
        description="HubMode=1 в проводнике",
        category="visual",
        risk="safe",
        requires_admin=True,
        requires_reboot=False,
        source="Optimize #Expl01t",
        entries=[
            (r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer", "HubMode", 1, 0),
        ],
        en_name="Hide Quick Access",
        en_description="HubMode=1 in File Explorer",
    ),
    SupplementalTweak(
        id="disable_diagnostic_collector",
        name="Отключить Diagnostic Data Collector",
        description="Служба diagnosticshub.standardcollector — Start=4",
        category="privacy",
        risk="medium",
        source="Optimize #Expl01t",
        entries=[
            (
                r"HKLM\SYSTEM\CurrentControlSet\Services\diagnosticshub.standardcollector.service",
                "Start",
                4,
                3,
            ),
        ],
        en_name="Disable Diagnostic Data Collector",
        en_description="Sets diagnosticshub.standardcollector service Start=4",
    ),
    SupplementalTweak(
        id="context_take_ownership",
        name="ПКМ: стать владельцем",
        description="Пункт «Стать владельцем» в контекстном меню",
        category="expert",
        risk="medium",
        requires_admin=True,
        requires_reboot=False,
        source="Optimize #Expl01t",
        entries=[
            (r"HKLM\SOFTWARE\Classes\*\shell\runas", "", "Стать владельцем", None, winreg.REG_SZ),
            (
                r"HKLM\SOFTWARE\Classes\*\shell\runas\command",
                "",
                'cmd.exe /c takeown /f "%1" && icacls "%1" /grant administrators:F',
                None,
                winreg.REG_SZ,
            ),
        ],
        en_name="Context Menu: Take Ownership",
        en_description="Adds Take Ownership to the context menu",
    ),
    SupplementalTweak(
        id="context_empty_folder",
        name="ПКМ: удалить содержимое папки",
        description="Пункт для очистки папки через контекстное меню",
        category="expert",
        risk="high",
        requires_admin=True,
        requires_reboot=False,
        source="Optimize #Expl01t",
        hint="Опасно: удаляет все файлы в папке без корзины",
        entries=[
            (r"HKLM\SOFTWARE\Classes\Directory\shell\EmptyThisFolder", "", "Удалить содержимое папки", None, winreg.REG_SZ),
            (
                r"HKLM\SOFTWARE\Classes\Directory\shell\EmptyThisFolder\command",
                "",
                'cmd /c "cd /d %1 && del /s /f /q *.* && rd /s /q ."',
                None,
                winreg.REG_SZ,
            ),
        ],
        en_name="Context Menu: Empty Folder",
        en_description="Adds Empty Folder to the context menu",
        en_hint="Dangerous: deletes folder contents without Recycle Bin",
    ),
    SupplementalTweak(
        id="compact_caption_buttons",
        name="Компактные кнопки окна",
        description="Уменьшенные кнопки Свернуть / Развернуть / Закрыть",
        category="visual",
        risk="safe",
        requires_admin=False,
        requires_reboot=False,
        source="Optimize #Expl01t",
        entries=[
            (r"HKCU\Control Panel\Desktop\WindowMetrics", "CaptionHeight", "-270", "-330", winreg.REG_SZ),
            (r"HKCU\Control Panel\Desktop\WindowMetrics", "CaptionWidth", "-270", "-330", winreg.REG_SZ),
        ],
        en_name="Compact Window Caption Buttons",
        en_description="Smaller Minimize / Maximize / Close buttons",
    ),
    # --- Эксперт (handlers в tweaks/expert.py) ---
    SupplementalTweak(
        id="disable_defender",
        name="Отключить Windows Defender",
        description="Defender, SmartScreen и SecurityHealth — Optimize #Expl01t",
        category="expert",
        risk="high",
        source="Optimize #Expl01t",
        hint="Эксперт · оставляет систему без антивируса",
        gpu_vendor=["all"],
        en_name="Disable Windows Defender",
        en_description="Disables Defender, SmartScreen and SecurityHealth",
        en_hint="Expert · leaves the system without antivirus",
    ),
    SupplementalTweak(
        id="disable_firewall",
        name="Отключить брандмауэр",
        description="Служба Windows Firewall (mpssvc) — Start=4",
        category="expert",
        risk="high",
        source="Optimize #Expl01t",
        hint="Эксперт · открывает систему для сетевых атак",
        en_name="Disable Windows Firewall",
        en_description="Disables Windows Firewall service (mpssvc)",
        en_hint="Expert · exposes the system to network attacks",
    ),
    SupplementalTweak(
        id="disable_dns_cache",
        name="Отключить DNS-кэш",
        description="Служба Dnscache — Start=4",
        category="expert",
        risk="high",
        source="Optimize #Expl01t",
        hint="Эксперт · может замедлить и destabilize сеть",
        en_name="Disable DNS Client Cache",
        en_description="Disables Dnscache service",
        en_hint="Expert · may slow down or destabilize networking",
    ),
    SupplementalTweak(
        id="disable_windows_update_completely",
        name="Полностью отключить Windows Update",
        description="wuauserv, UsoSvc, WaaSMedicSvc, DoSvc",
        category="expert",
        risk="high",
        source="Optimize #Expl01t",
        hint="Эксперт · система без патчей безопасности",
        en_name="Disable Windows Update Completely",
        en_description="Stops wuauserv, UsoSvc, WaaSMedicSvc and DoSvc",
        en_hint="Expert · no security patches",
    ),
    SupplementalTweak(
        id="disable_all_services",
        name="Массовое отключение служб",
        description="AutoDisableservices.reg — пакет из Optimize #Expl01t",
        category="expert",
        risk="high",
        requires_reboot=True,
        source="Optimize #Expl01t",
        hint="Эксперт · может сломать Windows, сеть и печать",
        en_name="Mass Disable Services",
        en_description="AutoDisableservices.reg bundle from Optimize #Expl01t",
        en_hint="Expert · may break Windows, network and printing",
    ),
    SupplementalTweak(
        id="disable_documents_tracking",
        name="Отключить слежку за Documents",
        description="CDPUserSvc — Start=4",
        category="expert",
        risk="medium",
        source="Optimize #Expl01t",
        en_name="Disable Documents Tracking",
        en_description="CDPUserSvc Start=4",
    ),
    SupplementalTweak(
        id="disable_delivery_optimization_full",
        name="Delivery Optimization OFF (полный)",
        description="DOUploadMode, DoSvc и связанные ключи",
        category="expert",
        risk="medium",
        source="Optimize #Expl01t",
        en_name="Delivery Optimization OFF (full)",
        en_description="DOUploadMode, DoSvc and related keys",
    ),
    SupplementalTweak(
        id="gray_selection_color",
        name="Серый цвет выделения",
        description="Hilight=128 128 128 в Control Panel\\Colors",
        category="visual",
        risk="safe",
        requires_admin=False,
        requires_reboot=False,
        source="Optimize #Expl01t",
        en_name="Gray Selection Color",
        en_description="Sets selection highlight to gray",
    ),
    # --- NVIDIA (handlers в tweaks/nvidia.py) ---
    SupplementalTweak(
        id="nvidia_disable_pstate",
        name="NVIDIA: отключить P-State",
        description="DisableDynamicPstate на GPU-адаптерах 0000–0007",
        category="nvidia",
        risk="medium",
        gpu_vendor=["nvidia"],
        source="Optimize #Expl01t",
        hint="NVIDIA-p-state.reg · перезагрузка рекомендуется",
        en_name="NVIDIA: Disable P-State",
        en_description="DisableDynamicPstate on GPU adapters 0000–0007",
        en_hint="NVIDIA-p-state.reg · reboot recommended",
    ),
    SupplementalTweak(
        id="nvidia_disable_telemetry",
        name="NVIDIA: отключить телеметрию",
        description="NvTelemetryContainer, scheduled tasks, OptInOrOutPreference",
        category="nvidia",
        risk="medium",
        requires_reboot=False,
        gpu_vendor=["nvidia"],
        source="Optimize #Expl01t",
        hint="Delete NVIDIA Telemetry.bat",
        en_name="NVIDIA: Disable Telemetry",
        en_description="Stops NvTelemetryContainer and related scheduled tasks",
        en_hint="Delete NVIDIA Telemetry.bat",
    ),
]
