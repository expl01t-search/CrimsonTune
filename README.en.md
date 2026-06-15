<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=d63031&height=140&section=header&text=CrimsonTune&fontSize=38&fontColor=ffffff&animation=fadeIn" alt="CrimsonTune" />

**Precise Windows 10 tuning** · desktop · RU/EN · Crimson Dark

<br>

[![v2.2.1](https://img.shields.io/badge/v2.2.1-321_tweaks-d63031?style=for-the-badge)](https://github.com/expl01t-search/CrimsonTune/releases/latest)
[![Windows 10](https://img.shields.io/badge/Windows-10_x64-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/expl01t-search/CrimsonTune)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/expl01t-search/CrimsonTune/blob/main/requirements.txt)
[![MIT](https://img.shields.io/badge/License-MIT-8b1e1e?style=for-the-badge)](https://github.com/expl01t-search/CrimsonTune/blob/main/LICENSE)

<br>

[![⬇ Download ZIP](https://img.shields.io/badge/⬇_Download_CrimsonTune-d63031?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune-v2.2.1-win64.zip)
[![Русский](https://img.shields.io/badge/🇷🇺_Русский-README.md-555?style=for-the-badge)](README.md)

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

<sub>PySide6 · Python 3.11+ · PyInstaller</sub>

<img src="https://capsule-render.vercel.app/api?type=waving&color=d63031&height=80&section=footer&animation=fadeIn" alt="" />

</div>
