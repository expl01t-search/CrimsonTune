from __future__ import annotations

GPU_CLASS_GUID = r"{4d36e968-e325-11ce-bfc1-08002be10318}"


def gpu_adapter_path(index: int = 0, *, current_control_set: bool = True) -> str:
    root = "CurrentControlSet" if current_control_set else "ControlSet001"
    return rf"HKLM\SYSTEM\{root}\Control\Class\{GPU_CLASS_GUID}\000{index}"


def gpu_adapter_paths(*, count: int = 2, current_control_set: bool = True) -> list[str]:
    return [gpu_adapter_path(i, current_control_set=current_control_set) for i in range(count)]


def microsoft_wow_pair(subpath: str, name: str, enable_value, disable_value=0, value_type=None):
    from tweaks.helpers import RegEntry

    base = rf"HKLM\SOFTWARE\Microsoft\{subpath}"
    wow = rf"HKLM\SOFTWARE\Wow6432Node\Microsoft\{subpath}"
    if value_type is None:
        return [
            (base, name, enable_value, disable_value),
            (wow, name, enable_value, disable_value),
        ]
    return [
        (base, name, enable_value, disable_value, value_type),
        (wow, name, enable_value, disable_value, value_type),
    ]
