<p align="center">
  <a href="README.md"><strong>🇷🇺 Русский</strong></a>
  &nbsp;·&nbsp;
  <a href="README.en.md"><strong>🇬🇧 English</strong></a>
</p>

<p align="center">
  <img src="icon.ico" alt="CrimsonTune" width="96" height="96" />
</p>

<h1 align="center">CrimsonTune</h1>

<p align="center">
  <strong>Precise Windows 10 tuning</strong><br>
  Desktop optimizer with smart scanning, profiles, and a crimson-dark interface
</p>

<p align="center">
  <a href="https://github.com/expl01t-search/CrimsonTune/releases/latest">
    <img src="https://img.shields.io/github/v/release/expl01t-search/CrimsonTune?style=for-the-badge&label=Release&color=d63031" alt="Release" />
  </a>
  <a href="https://github.com/expl01t-search/CrimsonTune/releases/latest">
    <img src="https://img.shields.io/badge/Windows-10%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows 10" />
  </a>
  <a href="https://github.com/expl01t-search/CrimsonTune/blob/main/requirements.txt">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  </a>
  <a href="https://github.com/expl01t-search/CrimsonTune/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-8b1e1e?style=for-the-badge" alt="License" />
  </a>
  <a href="README.md">
    <img src="https://img.shields.io/badge/UI-English_·_Русский-d63031?style=for-the-badge" alt="EN / RU" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune.exe">
    <img src="https://img.shields.io/badge/⬇️_Download_CrimsonTune.exe-d63031?style=for-the-badge" alt="Download EXE" />
  </a>
</p>

---

## About

**CrimsonTune** is a modern Windows 10 tweaker built with **PySide6 (Qt 6)**. It bundles proven optimizations from popular sources into a clean UI and helps you tune your system safely — without noise or guesswork.

> Run as **Administrator** — most tweaks modify the registry and Windows services.

> **UI language:** Russian and English — switch in **Settings → Language**.

---

## Features

| | |
|---|---|
| **129 tweaks** | WinUtil, Winhance, Sophia, Optimize #Expl01t, DLCI, ReadyPC |
| **Smart scan** | Detects tweaks already active in Windows and prevents duplicate toggles |
| **4 profiles** | Balanced, Gamer Pro, Max Performance, Privacy |
| **Filters** | All · Available · Active · One-shot |
| **`.reg` backup** | Export active tweak settings from the app |
| **Crimson Dark UI** | Dark theme, animations, splash screen, auto-scan on launch |
| **RU / EN** | Full UI and tweak description localization |

---

## Quick start

### Download the EXE

1. Open [**Releases**](https://github.com/expl01t-search/CrimsonTune/releases/latest)
2. Download `CrimsonTune.exe` or `CrimsonTune-v*-win64.zip`
3. Run **as Administrator**

### Run from source

```bash
git clone https://github.com/expl01t-search/CrimsonTune.git
cd CrimsonTune
pip install -r requirements.txt
python main.py
```

### Build EXE

```bash
python tools/gen_icon.py
pyinstaller build.spec
```

Output: `dist/CrimsonTune.exe`

---

## Screenshots

<p align="center">
  <img src="assets/screenshots/dashboard.png" alt="CrimsonTune — home dashboard with hardware monitoring and optimization ring" width="920" />
</p>

<p align="center">
  <sub>Home · CPU/GPU/RAM monitoring · optimization ring · quick cleanup</sub>
</p>

---

## Stack

| Layer | Technology |
|-------|------------|
| GUI | PySide6 + QSS `cyber_forge.qss` |
| Animations | `QPropertyAnimation`, `QEasingCurve` |
| System | Python 3.11+, `winreg`, `psutil` |
| Build | PyInstaller |

---

## Project structure

```
CrimsonTune/
├── core/           # app, detector, backups, i18n
├── tweaks/         # tweak handlers by category
├── ui/             # windows, components, theme
├── config/         # tweaks.json, profiles
├── locales/        # RU / EN
├── tools/gen_icon.py
└── main.py
```

---

## Safety

Risky and destructive tweaks are grouped under the **Expert** tab — apply only if you understand the consequences.

User data is stored in `%AppData%\CrimsonTune`  
(with automatic migration from `VeloForge` / `WinTweaker`).

---

## Restore settings

```bat
RESTORE.bat
```

or

```bash
python main.py --restore-all
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

---

<p align="center">
  <sub>Made with ❤️ for precise Windows tuning</sub><br>
  <sub><a href="README.md">Читать на русском</a></sub>
</p>
