<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=d63031&height=140&section=header&text=CrimsonTune&fontSize=38&fontColor=ffffff&animation=fadeIn" alt="CrimsonTune" />

**Точная настройка Windows 10** · desktop · RU/EN · Crimson Dark

<br>

[![v2.2.1](https://img.shields.io/badge/v2.2.1-321_твика-d63031?style=for-the-badge)](https://github.com/expl01t-search/CrimsonTune/releases/latest)
[![Windows 10](https://img.shields.io/badge/Windows-10_x64-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/expl01t-search/CrimsonTune)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/expl01t-search/CrimsonTune/blob/main/requirements.txt)
[![MIT](https://img.shields.io/badge/License-MIT-8b1e1e?style=for-the-badge)](https://github.com/expl01t-search/CrimsonTune/blob/main/LICENSE)

<br>

[![⬇ Скачать ZIP](https://img.shields.io/badge/⬇_Скачать_CrimsonTune-d63031?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune-v2.2.1-win64.zip)
[![English](https://img.shields.io/badge/🇬🇧_English-README.en.md-555?style=for-the-badge)](README.en.md)

<br>

<a href="assets/screenshots/dashboard.png">
  <img src="assets/screenshots/dashboard.png" alt="Главная панель CrimsonTune" width="880" />
</a>

<sub>321 твик · 7 профилей · умное сканирование · откат · автообновление</sub>

</div>

---

## О проекте

**CrimsonTune** — один инструмент вместо `.reg`, `.bat` и длинных гайдов. Твики из проверенных источников (WinUtil, Optimize #Expl01t, BoosterX, MSI Mode, SSD Mini Tweaker и др.) с понятным UI, фильтрами и полным откатом.

> ⚠️ Запуск **от имени администратора** — работа с реестром, службами и планировщиком.

---

## Возможности

| | |
|:--|:--|
| **321 твик** | Performance · SSD · Gaming · Graphics · Network · Privacy · System · Expert |
| **7 профилей** | Balanced · Gamer Pro · Gaming Plus · Max Performance · Privacy · SSD · Ghost Superlite |
| **Умный UI** | Скан состояния · фильтры · бейджи «активен / перезагрузка» · кольцо % на главной |
| **Безопасность** | Expert-вкладка · экспорт `.reg` · `RESTORE.bat` / `--restore-all` |
| **i18n** | Русский и English — **Настройки → Язык** |

---

## Быстрый старт

1. Скачай [**CrimsonTune-v2.2.1-win64.zip**](https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune-v2.2.1-win64.zip)
2. Распакуй и запусти **`CrimsonTune.exe` от администратора**
3. Выбери профиль или включай твики по категориям — **Настройки → Проверить обновления**

<details>
<summary><strong>Из исходников / сборка</strong></summary>

```bash
git clone https://github.com/expl01t-search/CrimsonTune.git
cd CrimsonTune
pip install -r requirements.txt
python main.py
```

Сборка EXE: `pip install -r requirements-dev.txt` → `python tools/gen_icon.py` → `pyinstaller build.spec`

Данные приложения: `%AppData%\CrimsonTune`

</details>

---

## Скриншоты

<p align="center">
  <a href="assets/screenshots/performance.png"><img src="assets/screenshots/performance.png" width="440" alt="Производительность" /></a>
  <a href="assets/screenshots/games.png"><img src="assets/screenshots/games.png" width="440" alt="Игры" /></a>
</p>
<p align="center">
  <a href="assets/screenshots/expert.png"><img src="assets/screenshots/expert.png" width="440" alt="Эксперт" /></a>
  <a href="assets/screenshots/settings.png"><img src="assets/screenshots/settings.png" width="440" alt="Настройки" /></a>
</p>

---

## Changelog

История версий — [**CHANGELOG.md**](CHANGELOG.md) · релизы — [**Releases**](https://github.com/expl01t-search/CrimsonTune/releases)

---

<div align="center">

<sub>PySide6 · Python 3.11+ · PyInstaller</sub>

<img src="https://capsule-render.vercel.app/api?type=waving&color=d63031&height=80&section=footer&animation=fadeIn" alt="" />

</div>
