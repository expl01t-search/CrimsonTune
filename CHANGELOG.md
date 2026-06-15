# Changelog

## [2.2.1] - 2026-06-16

### Fixed
- **Автообновление в EXE:** PyInstaller больше не исключает `http`/`email` — кнопка «Проверить обновления» не зависает; `UpdateCheckWorker` с защитой от сбоев
- **Фильтр «Доступные»:** скрыты incompatible и admin-blocked твики
- **Смена языка:** переводятся все уже загруженные вкладки категорий и поиск
- **Профили:** счётчики «применить X/Y» обновляются после apply и rescan

### Changed
- **UI:** стиль `#filterCombo`, улучшенные popup-меню QComboBox, сортировка твиков в категориях
- **Производительность:** один scan состояний на refresh/filter; убран лишний полный ScanWorker после apply; splash/rescan с реальной GPU/RAM-совместимостью
- **Сборка:** hiddenimports для `backlog`, `updater`, `http.client`
- **Графика:** убрана пустая подкатегория AMD из вкладки (AMD-твики по-прежнему фильтруются по GPU)
- Удалён мёртвый код: `ui/animations.py`, `line_chart.py`, дубли в `theme.py`
- `ApplyWorker` перенесён в `ui/workers.py`
- Версия приложения **2.2.1**

## [2.2.0] - 2026-06-16

### Added
- **+117 твиков** (каталог **321**): модуль `backlog_catalog` + `backlog` — OptimizerNXT, GTweak, Optimize-Windows, Ghost Spectre, dimaoudegrim, Sparkle
- **Приватность (43):** Recall, Spotlight, clipboard sync, Chrome/Firefox/VS/Office telemetry, CEIP, Find My Device, Focus Assist, NFC и др.
- **Интерфейс (22):** Snap Assist, taskbar, Explorer (Gallery/Home, checkboxes), Photo Viewer, контекстное меню
- **Эксперт (12):** Core Isolation, VBS, RDP, SmartScreen, pause WU до 2077, hosts-block telemetry
- **Сеть/игры:** Active Probing, netsh gaming, NIC LSO/RSS, FTH, MMCSS SFIO, boot splash, windowed games opt
- **Службы (21):** Ndu, PcaSvc, Spooler, TabletInput, Biometrics и др. — отдельными твиками
- **Разовые:** debloat UWP, EmptyStandbyList, kill overlays, Compact OS, God Mode, CEIP tasks
- **Профили:** `gaming_plus` (топ gaming+backlog), `ghost_superlite` (Ghost Spectre safe preset)
- Подсказки RU + EN для каждого нового твика; проверки состояния в `tweak_state`

### Changed
- Версия приложения **2.2.0**
- README: 321 твик, 7 профилей, ссылка на zip v2.2.0

### Fixed
- **USB Selective Suspend / Core Parking:** на кастомных планах (PowerX и др.) алиасы `SUB_USB`/`CPMINCORES` не работают — GUID + fallback через реестр
- **Parental Controls:** служба `WpcMonSvc` вместо ошибочного `SEMgrSvc`
- **pause_updates_extreme:** каталог, handler и проверка состояния синхронизированы
- **restore_legacy_photo_viewer:** корректный статус «активен» (не ONE_SHOT)
- Откат USB/Core Parking больше не маскирует ошибки реестра

## [2.1.2] - 2026-06-15

### Changed
- **Главная:** компактный блок оптимизации — только gauge и две строки (Активно / Доступно)

### Removed
- Экспорт отчёта и модуль `optimization_report`
- Неиспользуемые строки локализации и мёртвый код UI
- Папка `tests/` из репозитория (остаётся локально; CI — проверка импорта и compileall)
- `pytest` из `requirements-dev.txt` (только PyInstaller для сборки)

## [2.1.1] - 2026-06-15

### Fixed
- **Зависание при переключении вкладок:** мгновенное переключение категорий, ленивая загрузка списка, проверки состояния батчами по 24 твика
- Убран сброс кэша состояний при каждом открытии списка

### Removed
- Документация и шаг CI для подписи EXE (отложено)

## [2.1.0] - 2026-06-15

### Added
- **Группы дублей:** Game DVR, телеметрия, план питания — честный % на главной
- **Экспорт отчёта** (JSON + MD) на Dashboard → `AppData/CrimsonTune/reports/`
- **Windows 11:** бейдж на главной, совместимость твиков с `10.0` на Win11
- **Установка обновления** из Настроек (скачивание zip + перезапуск)
- **E2E UI-тесты** (`pytest-qt`): toggle ON, бейдж перезагрузки, refresh строк

## [2.0.0] - 2026-06-15

### Major — CrimsonTune 2.0
- **Надёжность состояния твиков:** переключатель ON для всех применённых твиков (реестр, службы, powercfg); проверки через реестр и cp866 для русской Windows
- **Честный процент оптимизации:** пересекающиеся твики (Prefetch/Superfetch, индексирование, Nagle) считаются одним слотом — без «накрутки» процентов
- **Бейдж «Применено · перезагрузка»** для твиков, применённых через CrimsonTune, но ещё не подтверждённых Windows
- **Предупреждение о дублях** при применении пересекающихся твиков из одной группы

### Added
- **CI:** GitHub Actions — `pytest` на каждый push/PR (`ci.yml`)
- **Автообновление:** проверка релизов GitHub (Настройки + фоновая проверка при старте)
- **Релизы:** только архив `.zip` + `RELEASE_NOTES.md` из CHANGELOG (без отдельного EXE в Assets)
- Интеграционные тесты состояния, групп твиков, updater, extract_release_notes
- `core/tweak_groups.py`, `core/updater.py`, `tools/extract_release_notes.py`

### Fixed
- Единый `BackupManager` через `TweakManager` (корректный счётчик применённых в Настройках)
- Счётчик «Активно» учитывает применённые твики; гибернация и DWORD-проверки реестра

## [1.2.24] - 2026-06-15

### Fixed
- **UI после применения:** переключатель включается для всех типов твиков (реестр, службы, powercfg), если твик применён через CrimsonTune
- **Счётчик «Активно»** в списке и на главной учитывает применённые твики, а не только подтверждённые в Windows
- **Проверка реестра:** корректное сравнение DWORD (в т.ч. `0xFFFFFFFF` / `-1`)
- **Гибернация:** проверка через реестр `HibernateEnabled`, не только `powercfg /a`
- **Консоль Windows:** чтение вывода `sc`/`netsh`/`powercfg` в кодировке cp866 (русская Windows)
- Мгновенное обновление строк списка сразу после применения, без ожидания полного скана

## [1.2.23] - 2026-06-15

### Changed
- **Определение активных твиков:** проверка служб по типу запуска (`disabled`), а не только `STOPPED`
- Добавлены проверки: Game Mode, HAGS, MPO, Win32PrioritySeparation — **100% покрытие** отслеживаемых твиков
- **Процент на главной:** взвешенная оценка по риску (safe/medium/high), только совместимые и с проверкой в системе
- Статистика «Ожидают проверки» для твиков, применённых через CrimsonTune, но не подтверждённых в Windows

## [1.2.22] - 2026-06-15

### Changed
- **Производительность:** batch-scan кэш для проверок твиков, кэш `netsh tcp global`, батчинг списка (24 строки/кадр)
- **Старт:** ускорен splash (handoff ~280 ms вместо 450 ms)
- **UI:** обновлён QSS — sidebar, карточки твиков, бейджи, состояния hover/pressed/focus
- Состояние «Загрузка списка…» при открытии больших категорий

## [1.2.21] - 2026-06-15

### Changed
- **Размер EXE −20%** (~49 → ~36 MB): исключены неиспользуемые модули Qt, плагины и лишние DLL
- `tools/pyi_excludes.py` — фильтрация сборки PyInstaller
- Dev-зависимости вынесены в `requirements-dev.txt` (pytest, pyinstaller)
- Кэш EXE в AppData: копируются только `config` и `locales` (без лишней папки `ui`)

## [1.2.20] - 2026-06-15

### Added
- **SSD-пакет** (SSD Mini Tweaker): TRIM, отключение Prefetch/Superfetch, дефрагментации при загрузке, Layout.ini
- Отключение службы и плановой дефрагментации, индексирования томов, защиты системы (высокий риск)
- Профиль **SSD** и подкатегория SSD на вкладке «Производительность»
- Обновлённые README (RU/EN)

## [1.2.19] - 2026-06-15

### Added
- **MSI Mode: High (GPU/USB/LAN)** — MSISupported + DevicePriority High как MSI Mode Utility v3
- **NVIDIA:** MaxFrameLatency 1, отключение runtime PM, driver perf (nvlddmkm + NVTweak)

## [1.2.18] - 2026-06-15

### Removed
- Твики-инструкции без реального применения: `nvidia_max_performance`, `nvidia_low_latency`, `amd_anti_lag`

## [1.2.17] - 2026-06-15

### Added
- **+16 твиков** из BoosterX, SpeedGuide, CS2 Ping Optimizer, dimaoudegrim, RPG Russia:
  - Nagle OFF на NIC (TcpDelAckTicks), Psched NonBestEffortLimit, MMCSS Games full priority
  - TCP ECN, CTCP, отключение RSC, отключение сжатия памяти
  - Explorer SeparateProcess, кэш иконок, отключение сжатия NTFS
  - Nearby Sharing OFF, AutoRun OFF, Edge Startup Boost OFF, Phone Link OFF

## [1.2.16] - 2026-06-15

### Changed
- Сайдбар: **14 → 10** пунктов — NVIDIA, AMD, DirectX и OpenGL объединены во вкладку **Графика**
- Вкладка **Система** теперь включает твики категории «Визуал»; на объединённых страницах показывается метка подкатегории

## [1.2.15] - 2026-06-15

### Added
- Вкладки **NVIDIA**, **AMD** и **Эксперт** — GPU-специфичные и опасные твики отдельно
- NVIDIA: `nvidia_disable_pstate` (NVIDIA-p-state.reg), `nvidia_disable_telemetry` (Delete NVIDIA Telemetry.bat)
- Эксперт: Defender, Firewall, DNS cache, массовое отключение служб, полный WU OFF и др. из Optimize #Expl01t

### Changed
- NVIDIA/AMD твики перенесены из «Система» / «Игры» в отдельные вкладки
- Твики удаления служб и аналогичные помечены категорией «Эксперт»

### Removed
- `config/blacklist.json` — опасные твики доступны во вкладке «Эксперт» с явной маркировкой

## [1.2.14] - 2026-06-15

### Added
- **Custom-DirectX** (anton18-png): 27 твиков DirectX/D3D11/D3D12 — VSync, MMX, D3D12 runtime, latency и др.
- **Optimize #Expl01t · Доп твики**: Boost TCP, UAC OFF, mitigations, контекстное меню, компактные кнопки окна и др.

### Changed
- `enable_shader_cache` — корректный `EnableShaderCache` на GPU-адаптере (Custom-DirectX)

### Removed
- Пустые hint-твики: DirectX 12 Ultimate, NVIDIA Reflex/Threaded, AMD texture hint, max prerendered frames

## [1.2.13] - 2026-06-15

### Added
- RAM Optimization (Optimize #Expl01t): 8 профилей `SvcHostSplitThresholdInKB` (2–64 GB)
- Показывается только твик, подходящий под объём RAM в системе

## [1.2.12] - 2026-06-15

### Fixed
- Gauge при первом открытии окна: синхронизация layout до/после show, fallback-ширина 200px
- Убран `setMaximumHeight` на контейнере gauge — подпись больше не наезжает при старте
- Пересчёт gauge при resize колонки оптимизации

## [1.2.11] - 2026-06-15

### Fixed
- Дашборд: gauge оптимизации масштабируется и центрируется при изменении размера окна
- Подпись под gauge больше не наезжает на кольцо и процент

## [1.2.10] - 2026-06-15

### Fixed
- Краш при смене вкладок: `hideEvent` dashboard больше не трогает `DiskLoadWorker`
- Сайдbar: `finished` только сбрасывает ссылку, `stop()` — только при прерывании анимации
- `DiskLoadWorker` без parent-widget (корректный lifecycle QThread)

## [1.2.9] - 2026-06-15

### Fixed
- Краш при переключении вкладок: `DiskLoadWorker` больше не удаляется через `deleteLater` во время fade-анимации
- Краш сайдбара: `QPropertyAnimation` индикатора — без `DeleteWhenStopped`, безопасная остановка через `shiboken6.isValid`

## [1.2.8] - 2026-06-15

### Fixed
- Анимации вкладок: fade через paint-based overlay вместо `QGraphicsOpacityEffect` (не работал на Windows)
- Страницы твиков: убран `WA_DontShowOnScreen` из `TweakListPanel` — контент снова отображается после lazy-load
- Дашборд: gauge и подпись не наезжают друг на друга, min-width правой колонки 280px

## [1.2.7] - 2026-06-15

### Fixed
- EXE: метаданные версии в свойствах файла (описание, copyright, product version)
- Зависание на splash «Подготовка интерфейса…» — исправлен краш в `AnimatedPageStack`, ленивая загрузка категорий, async-диски

## [1.2.6] - 2026-06-15

### Fixed
- Анимации вкладок на Windows: переход на overlay-fade вместо `QGraphicsOpacityEffect` на страницах (пустой экран / мгновенное переключение)
- Resize дашборда: `hardwareScroll` с `setWidgetResizable`, debounce 60ms, `wordWrap` на заголовках оптимизации и статистике
- Убрана хрупкая логика `setFixedHeight` / `setFixedWidth` на колонке железа

## [1.2.5] - 2026-06-15

### Fixed
- `_current_page` синхронизируется с анимацией вкладок через `AnimatedPageStack.page_shown`
- Профили: исправлены ID твиков (`disable_game_bar_presence`, `menu_show_delay_zero`)
- Кэш EXE: `.bundle_stamp` и полный re-seed при изменении bundle после переустановки
- Индикатор сайдбара не «прыгает» при resize окна
- `TweakRow.update_meta()` обновляет бейдж статуса при смене языка
- Смена языка: обновляется только текущая страница твиков (быстрее)
- Перевод onboarding, progress overlay, результата очистки диска
- Защита от path traversal в `_quick_action`
- Кнопка «Сканировать» корректно переводится во время активного скана

### Changed
- Тесты: 45/45 — совместимость GPU, формулировки admin-hint

## [1.2.4] - 2026-06-15

### Added
- `AnimatedPageStack` — плавное переключение вкладок (fade 280ms)
- Анимированный красный индикатор в сайдбаре (220ms)
- `utils/categories.py` — единый список категорий твиков
- `tweaks/registry.py` — регистрация handler-модулей

### Changed
- Смена языка RU/EN **без перезапуска** — hot reload всего UI, включая названия твиков
- Минимальная ширина окна **960px**
- Удалены docstring'и и комментарии из Python-кода (69 файлов)

### Fixed
- Восстановлен кэш ресурсов EXE в AppData (`core/paths.py`)
- Дашборд: локализация железа, gauge без наложения текста
- Страница профилей: `retranslate_ui()`
- Debounce при resize дашборда

## [1.2.3] - 2026-06-15

### Fixed
- EXE: краш при переключении на EN — кэш `config/`, `locales/`, `ui/` в `%AppData%\CrimsonTune\runtime\`
- EXE: стабильный перезапуск через `subprocess.Popen`
- Дашборд: текст «Оптимизация Windows» вынесен из кольца gauge, подпись с отступами
- i18n: карточки CPU/GPU/RAM/диски, строки твиков (`TweakRow.update_meta`), поиск и настройки
- Resize: gauge 192px, прокрутка колонки железа, debounce синхронизации высоты
- Toolbar: `min-width` поиска, size policy кнопок; мин. размер окна **920×580**

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
