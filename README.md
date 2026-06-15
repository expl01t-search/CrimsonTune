# CrimsonTune — Точная настройка Windows

Desktop-оптимизатор Windows 10 на **PySide6** (Qt 6) с тёмно-красной темой, умным сканированием и **129 твиками**.

## Стек

| Слой | Технология |
|------|-----------|
| GUI | PySide6 + QSS Crimson Dark |
| Анимации | QPropertyAnimation, QEasingCurve |
| Логика | Python 3.11+, winreg, psutil |

## Возможности

- **129 твиков** из WinUtil, Winhance, Sophia, Optimize #Expl01t, DLCI, ReadyPC
- **Умное сканирование** — определяет уже активные настройки, не даёт включить повторно
- **4 профиля** с пропуском уже применённых твиков
- **Splash + автоскан** при запуске
- **Фильтры**: Все / Доступные / Активные / Разовые
- **Применить все твики** в каждой категории
- **Бэкап .reg** активных настроек в Настройках

## Установка

```bash
cd C:\Users\Exploit\Desktop\WinTweaker
pip install -r requirements.txt
python main.py
```

## Сборка EXE

```bash
pyinstaller build.spec
```

Результат: `dist/CrimsonTune.exe`

## Blacklist

Опасные твики в `config/blacklist.json` — никогда не добавляются в приложение.

## Структура UI

```
ui/
├── theme.py, animations.py
├── main_window.py, sidebar.py, dashboard.py
├── tweak_page.py, profiles_page.py, settings_page.py
├── components/  — tweak_card, forge_toggle, stat_card, toast, modal, progress_overlay
└── assets/styles/cyber_forge.qss
```

Данные приложения: `%AppData%\CrimsonTune` (миграция из `VeloForge` / `WinTweaker`).
