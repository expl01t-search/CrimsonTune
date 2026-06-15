from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from core.updater import ReleaseInfo


def _running_exe() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return Path(sys.argv[0]).resolve()


def download_release_zip(release: ReleaseInfo, dest_dir: Path) -> Path:
    if not release.download_url:
        raise ValueError("No download URL in release info")
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / "update.zip"
    urllib.request.urlretrieve(release.download_url, zip_path)
    return zip_path


def extract_update_exe(zip_path: Path, dest_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(dest_dir)
    candidates = list(dest_dir.rglob("CrimsonTune.exe"))
    if not candidates:
        raise FileNotFoundError("CrimsonTune.exe not found in update archive")
    return candidates[0].resolve()


def create_swap_script(
    new_exe: Path,
    target_exe: Path | None = None,
    work_dir: Path | None = None,
) -> Path:
    target = (target_exe or _running_exe()).resolve()
    script = target.parent / "_crimsontune_update.bat"
    cleanup = f'rmdir /s /q "{work_dir}"' if work_dir else ""
    content = f"""@echo off
chcp 65001 >nul
echo CrimsonTune — установка обновления...
timeout /t 2 /nobreak >nul
copy /Y "{new_exe}" "{target}" >nul
if errorlevel 1 (
  echo Ошибка копирования. Запустите от администратора.
  pause
  exit /b 1
)
{cleanup}
start "" "{target}"
exit
"""
    script.write_text(content, encoding="utf-8")
    return script


def launch_update_swap(release: ReleaseInfo) -> tuple[bool, str]:
    work_dir = Path(tempfile.mkdtemp(prefix="crimsontune_update_"))
    try:
        zip_path = download_release_zip(release, work_dir)
        new_exe = extract_update_exe(zip_path, work_dir)
        script = create_swap_script(new_exe, work_dir=work_dir)
        subprocess.Popen(
            ["cmd", "/c", str(script)],
            creationflags=subprocess.CREATE_NO_WINDOW,
            close_fds=True,
        )
        return True, str(script)
    except Exception as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        return False, str(exc)
