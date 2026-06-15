from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from core.brand import APP_VERSION, GITHUB_REPO


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    tag: str
    download_url: str
    notes_url: str


def parse_version(version: str) -> tuple[int, ...]:
    parts = [int(p) for p in re.findall(r"\d+", version)]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:4])


def is_newer(remote: str, local: str = APP_VERSION) -> bool:
    return parse_version(remote) > parse_version(local)


def fetch_latest_release(timeout: int = 12) -> Optional[ReleaseInfo]:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "CrimsonTune-Updater"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None

    tag = str(payload.get("tag_name", "")).lstrip("vV")
    if not tag:
        return None

    download_url = ""
    for asset in payload.get("assets", []):
        name = str(asset.get("name", ""))
        if name.endswith(".zip"):
            download_url = str(asset.get("browser_download_url", ""))
            break

    return ReleaseInfo(
        version=tag,
        tag=str(payload.get("tag_name", f"v{tag}")),
        download_url=download_url,
        notes_url=str(payload.get("html_url", "")),
    )


def check_for_update(local_version: str = APP_VERSION) -> tuple[Optional[ReleaseInfo], str]:
    latest = fetch_latest_release()
    if latest is None:
        return None, "error"
    if is_newer(latest.version, local_version):
        return latest, "available"
    return None, "latest"
