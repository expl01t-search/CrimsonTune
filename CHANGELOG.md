# Changelog

## [1.2.2] - 2026-06-15

### Fixed
- EXE: корректные пути к `config/tweaks.json` и `locales/` через `sys._MEIPASS`
- Сборка: `icon.ico` включён в bundle, UPX отключён для стабильности

## [1.2.1] - 2026-06-15

### Changed
- Обновлён README: современный дизайн, badges, быстрый старт
- Улучшена иконка приложения (multi-size ICO)
- Очистка проекта от артефактов сборки и лишних папок
- Добавлен MIT License

## [1.2.0] - 2026-06-15

### CrimsonTune — точная настройка Windows 10

- **129 твиков** из WinUtil, Winhance, Sophia, Optimize #Expl01t, DLCI, ReadyPC
- Умное сканирование уже активных настроек
- 4 профиля оптимизации с пропуском применённых твиков
- Splash-экран и автоскан при запуске
- Фильтры: Все / Доступные / Активные / Разовые
- Бэкап `.reg` активных настроек
- Тёмно-красная тема на PySide6 (Qt 6)
- Локализация RU / EN

### Установка

1. Скачайте `CrimsonTune.exe` или `CrimsonTune-v1.2.0-win64.zip` из [Releases](https://github.com/expl01t-search/CrimsonTune/releases).
2. Запустите от имени администратора.

### Из исходников

```bash
pip install -r requirements.txt
python main.py
```
