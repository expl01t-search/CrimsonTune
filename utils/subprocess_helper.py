
from __future__ import annotations

import subprocess
from typing import Optional


def run_command(
    command: list[str],
    *,
    shell: bool = False,
    timeout: int = 60,
) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=shell,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Таймаут выполнения команды"
    except OSError as exc:
        return -1, "", str(exc)


def run_powershell(script: str, timeout: int = 60) -> tuple[int, str, str]:
    return run_command(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-WindowStyle",
            "Hidden",
            "-Command",
            script,
        ],
        timeout=timeout,
    )


def get_service_start_type(service_name: str) -> Optional[str]:
    code, out, _ = run_command(["sc", "qc", service_name])
    if code != 0:
        return None
    for line in out.splitlines():
        lower = line.lower()
        if "start_type" in lower or "тип запуска" in lower:
            if "auto_start" in lower or "автоматически" in lower:
                return "auto"
            if "demand_start" in lower or "вручную" in lower:
                return "manual"
            if "disabled" in lower or "отключ" in lower:
                return "disabled"
    return None


def set_service_start_type(service_name: str, start_type: str) -> tuple[int, str]:
    type_map = {"auto": "auto", "manual": "demand", "disabled": "disabled"}
    sc_type = type_map.get(start_type, start_type)
    code, out, err = run_command(["sc", "config", service_name, f"start={sc_type}"])
    return code, out or err


def stop_service(service_name: str) -> tuple[int, str]:
    code, out, err = run_command(["sc", "stop", service_name])
    return code, out or err
