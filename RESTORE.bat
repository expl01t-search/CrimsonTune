@echo off
chcp 65001 >nul
echo VeloForge - Экстренный откат
echo ================================
echo Запуск отката всех применённых твиков...
python "%~dp0main.py" --restore-all
pause
