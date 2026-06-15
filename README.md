<p align="center">
  <a href="README.md"><strong>🇷🇺 Русский</strong></a>
  &nbsp;·&nbsp;
  <a href="README.en.md"><strong>🇬🇧 English</strong></a>
</p>

<p align="center">
  <img src="icon.ico" alt="CrimsonTune" width="112" height="112" />
</p>

<h1 align="center">CrimsonTune</h1>

<p align="center">
  <strong>Точная настройка Windows 10</strong><br>
  <sub>Desktop-оптимизатор · умное сканирование · профили · Crimson Dark UI</sub>
</p>

<p align="center">
  <a href="https://github.com/expl01t-search/CrimsonTune/releases/latest">
    <img src="https://img.shields.io/badge/v1.2.20-204_твика-d63031?style=for-the-badge" alt="v1.2.20" />
  </a>
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
</p>

<p align="center">
  <a href="https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune.exe">
    <img src="https://img.shields.io/badge/⬇️_Скачать_CrimsonTune.exe-d63031?style=for-the-badge&logo=windows&logoColor=white" alt="Download" />
  </a>
</p>

---

## Зачем CrimsonTune

Один инструмент вместо десятка `.reg`, `.bat` и полуручных гайдов. CrimsonTune собирает проверенные твики из **WinUtil**, **Optimize #Expl01t**, **BoosterX**, **SpeedGuide**, **MSI Mode Utility** и **SSD Mini Tweaker** — и даёт им понятный интерфейс с откатом, сканированием и профилями.

> Запускайте **от имени администратора** — твики работают с реестром, службами и планировщиком.

> **Язык:** русский и английский — **Настройки → Язык**.

---

## Что внутри

<table>
<tr>
<td width="50%" valign="top">

### Производительность
- CPU, RAM, службы, питание
- **SSD-пакет** (TRIM, дефрагментация OFF, NTFS)
- Отключение SysMain, hibernation, prefetch

### Игры и сеть
- **MSI Mode High** (GPU / USB / LAN)
- MMCSS, Nagle OFF на NIC, TCP ECN/CTCP
- Игровые твики и таймер

</td>
<td width="50%" valign="top">

### Графика
- NVIDIA: P-State, MaxFrameLatency, driver perf
- DirectX / OpenGL / AMD (по железу)

### Безопасность UI
- Опасные твики — вкладка **Эксперт**
- Умное сканирование: не включить дважды
- Экспорт `.reg` и полный откат

</td>
</tr>
</table>

| | |
|---|---|
| **204 твика** | performance · SSD · gaming · graphics · network · privacy · system · expert |
| **10 вкладок** | Главная · Производительность · Игры · Графика · Сеть · Приватность · Система · Эксперт · Профили · Настройки |
| **5 профилей** | Balanced · Gamer Pro · Max Performance · Privacy · **SSD** |
| **Фильтры** | Все · Доступные · Активные · Разовые |
| **Crimson Dark** | Тёмная тема, анимации, splash, автоскан при старте |

---

## SSD-оптимизация

На вкладке **Производительность** появилась подкатегория **SSD** — набор из SSD Mini Tweaker и связанных NTFS-твиков:

| Твик | Действие |
|------|----------|
| TRIM | `fsutil DisableDeleteNotify=0` на томах |
| Prefetch / Superfetch OFF | Не нужны на SSD |
| Дефрагментация OFF | Служба, планировщик, boot defrag |
| Layout.ini OFF | OptimalLayout + Prefetch scenario |
| Индексирование дисков OFF | WMI/CIM на фиксированных томах |
| Защита системы OFF | Освобождает место (risk: high) |

Дополнительно в профиле **SSD**: `ntfs_memory_ssd`, `large_system_cache_on`, `disable_paging_executive`, `ntfs_8dot3_off`, `disable_hibernation` и др.

---

## Быстрый старт

### Скачать EXE

1. [**Releases**](https://github.com/expl01t-search/CrimsonTune/releases/latest)
2. `CrimsonTune.exe` или `CrimsonTune-v*-win64.zip`
3. Запуск **от имени администратора**

### Из исходников

```bash
git clone https://github.com/expl01t-search/CrimsonTune.git
cd CrimsonTune
pip install -r requirements.txt
python main.py
```

### Сборка

```bash
python tools/gen_icon.py
pyinstaller build.spec
```

→ `dist/CrimsonTune.exe`

---

## Скриншоты

<p align="center">
  <img src="assets/screenshots/dashboard.png" alt="CrimsonTune — главная панель" width="920" />
</p>

<p align="center"><sub>Главная · CPU/GPU/RAM · кольцо оптимизации · быстрая очистка</sub></p>

---

## Стек

| Слой | Технология |
|------|------------|
| GUI | PySide6 + `cyber_forge.qss` |
| Система | Python 3.11+, `winreg`, `psutil` |
| Сборка | PyInstaller |

```
CrimsonTune/
├── core/       # приложение, сканер, бэкапы, i18n
├── tweaks/     # performance, ssd, nvidia, msi_mode, expert…
├── ui/         # окна, компоненты, тема
├── config/     # tweaks.json, профили (в т.ч. ssd.json)
└── locales/    # RU / EN
```

---

## Восстановление

```bat
RESTORE.bat
```

или `python main.py --restore-all`

Данные: `%AppData%\CrimsonTune` (миграция из VeloForge / WinTweaker).

---

## Changelog

[CHANGELOG.md](CHANGELOG.md)

---

<p align="center">
  <sub>Сделано для точной настройки Windows</sub><br>
  <a href="README.en.md">Read in English</a>
</p>
