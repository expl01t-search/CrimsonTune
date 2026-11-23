<div align="center">

<img src="assets/banner.en.svg" width="100%" alt="CrimsonTune — precise Windows 10 tuning" />

[![Release](https://img.shields.io/github/v/release/expl01t-search/CrimsonTune?style=for-the-badge&color=d63031&labelColor=161b22&label=release)](https://github.com/expl01t-search/CrimsonTune/releases/latest)
[![321 tweaks](https://img.shields.io/badge/tweaks-321-d63031?style=for-the-badge&labelColor=161b22)](#features)
[![Windows 10](https://img.shields.io/badge/Windows-10_x64-d63031?style=for-the-badge&labelColor=161b22&logo=windows&logoColor=d63031)](https://github.com/expl01t-search/CrimsonTune)
[![Python](https://img.shields.io/badge/Python-3.11+-d63031?style=for-the-badge&labelColor=161b22&logo=python&logoColor=d63031)](https://github.com/expl01t-search/CrimsonTune/blob/main/requirements.txt)
[![MIT](https://img.shields.io/badge/license-MIT-d63031?style=for-the-badge&labelColor=161b22)](https://github.com/expl01t-search/CrimsonTune/blob/main/LICENSE)

<br>

[![⬇ Download ZIP](https://img.shields.io/badge/⬇_Download_CrimsonTune-v2.2.1_·_Windows_x64-d63031?style=for-the-badge&labelColor=0d1117&logo=windows&logoColor=white)](https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune-v2.2.1-win64.zip)
[![Русский](https://img.shields.io/badge/Русский-README.md-161b22?style=for-the-badge)](README.md)

<br>

<a href="assets/screenshots/dashboard.png">
  <img src="assets/screenshots/dashboard.png" alt="CrimsonTune home dashboard" width="880" />
</a>

<sub>321 tweaks · 7 profiles · smart scan · revert · auto-update</sub>

</div>

---

## About

**CrimsonTune** replaces scattered `.reg` files, batch scripts, and long guides with one desktop app. Proven tweaks (WinUtil, Optimize #Expl01t, BoosterX, MSI Mode, SSD Mini Tweaker, and more) with filters, profiles, and full restore.

> ⚠️ Run **as Administrator** — registry, services, and scheduled tasks.

---

## Features

| | |
|:--|:--|
| **321 tweaks** | Performance · SSD · Gaming · Graphics · Network · Privacy · System · Expert |
| **7 profiles** | Balanced · Gamer Pro · Gaming Plus · Max Performance · Privacy · SSD · Ghost Superlite |
| **Smart UI** | State scan · filters · status badges · optimization ring on home |
| **Safety** | Expert tab · `.reg` export · `RESTORE.bat` / `--restore-all` |
| **i18n** | Russian & English — **Settings → Language** |

---

## Quick start

1. Download [**CrimsonTune-v2.2.1-win64.zip**](https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune-v2.2.1-win64.zip)
2. Extract and run **`CrimsonTune.exe` as Administrator**
3. Pick a profile or tweak by category — **Settings → Check for updates**

<details>
<summary><strong>From source / build</strong></summary>

```bash
git clone https://github.com/expl01t-search/CrimsonTune.git
cd CrimsonTune
pip install -r requirements.txt
python main.py
```

Build EXE: `pip install -r requirements-dev.txt` → `python tools/gen_icon.py` → `pyinstaller build.spec`

App data: `%AppData%\CrimsonTune`

</details>

---

## Screenshots

<p align="center">
  <a href="assets/screenshots/performance.png"><img src="assets/screenshots/performance.png" width="440" alt="Performance" /></a>
  <a href="assets/screenshots/games.png"><img src="assets/screenshots/games.png" width="440" alt="Games" /></a>
</p>
<p align="center">
  <a href="assets/screenshots/expert.png"><img src="assets/screenshots/expert.png" width="440" alt="Expert" /></a>
  <a href="assets/screenshots/settings.png"><img src="assets/screenshots/settings.png" width="440" alt="Settings" /></a>
</p>

---

## Changelog

Version history — [**CHANGELOG.md**](CHANGELOG.md) · releases — [**Releases**](https://github.com/expl01t-search/CrimsonTune/releases)

---

<div align="center">

<img src="assets/divider.svg" width="100%" alt="" />

<sub>PySide6 · Python 3.11+ · PyInstaller · by <a href="https://github.com/expl01t-search">Expl01t</a></sub>

</div>
