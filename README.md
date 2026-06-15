<p align="center">
  <img src="icon.ico" alt="CrimsonTune" width="96" height="96" />
</p>

<h1 align="center">CrimsonTune</h1>

<p align="center">
  <strong>Точная настройка Windows 10</strong><br>
  Desktop-оптимизатор с умным сканированием, профилями и тёмно-красным интерфейсом
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
</p>

<p align="center">
  <a href="https://github.com/expl01t-search/CrimsonTune/releases/latest/download/CrimsonTune.exe">
    <img src="https://img.shields.io/badge/⬇️_Скачать_CrimsonTune.exe-d63031?style=for-the-badge" alt="Download EXE" />
  </a>
</p>

---

## О проекте

**CrimsonTune** — это современный твикер для Windows 10, собранный на **PySide6 (Qt 6)**. Приложение объединяет проверенные оптимизации из популярных источников, аккуратно упаковывает их в понятный интерфейс и помогает безопасно настроить систему без лишнего шума.

> Запускайте от имени администратора — большинство твиков работают с реестром и системными службами.

---

## Возможности

| | |
|---|---|
| **129 твиков** | WinUtil, Winhance, Sophia, Optimize #Expl01t, DLCI, ReadyPC |
| **Умное сканирование** | Определяет уже активные настройки и не даёт включить их повторно |
| **4 профиля** | Balanced, Gamer Pro, Max Performance, Privacy |
| **Фильтры** | Все · Доступные · Активные · Разовые |
| **Бэкап .reg** | Экспорт активных настроек прямо из приложения |
| **Crimson Dark UI** | Тёмная тема, анимации, splash-экран и автоскан при старте |

---

## Быстрый старт

### Скачать готовый EXE

1. Перейдите в [**Releases**](https://github.com/expl01t-search/CrimsonTune/releases/latest)
2. Скачайте `CrimsonTune.exe` или `CrimsonTune-v*-win64.zip`
3. Запустите **от имени администратора**

### Запуск из исходников

```bash
git clone https://github.com/expl01t-search/CrimsonTune.git
cd CrimsonTune
pip install -r requirements.txt
python main.py
```

### Сборка EXE

```bash
python tools/gen_icon.py
pyinstaller build.spec
```

Готовый файл: `dist/CrimsonTune.exe`

---

## Скриншоты

<p align="center">
  <img src="assets/screenshots/dashboard.png" alt="CrimsonTune — главная панель с мониторингом железа и статусом оптимизации" width="920" />
</p>

<p align="center">
  <sub>Главная · мониторинг CPU/GPU/RAM · кольцо оптимизации · быстрая очистка</sub>
</p>

---

## Стек

| Слой | Технология |
|------|------------|
| GUI | PySide6 + QSS `cyber_forge.qss` |
| Анимации | `QPropertyAnimation`, `QEasingCurve` |
| Система | Python 3.11+, `winreg`, `psutil` |
| Сборка | PyInstaller |

---

## Структура проекта

```
CrimsonTune/
├── core/           # приложение, детектор, бэкапы, i18n
├── tweaks/         # обработчики твиков по категориям
├── ui/             # окна, компоненты, тема
├── config/         # tweaks.json, профили, blacklist
├── locales/        # RU / EN
├── tools/gen_icon.py
└── main.py
```

---

## Безопасность

Опасные и деструктивные твики вынесены в `config/blacklist.json` и **никогда** не попадают в приложение.

Данные пользователя хранятся в `%AppData%\CrimsonTune`  
(с автоматической миграцией из `VeloForge` / `WinTweaker`).

---

## Восстановление настроек

```bat
RESTORE.bat
```

или

```bash
python main.py --restore-all
```

---

## Changelog

См. [CHANGELOG.md](CHANGELOG.md)

---

<p align="center">
  <sub>Сделано с ❤️ для точной настройки Windows</sub>
</p>
