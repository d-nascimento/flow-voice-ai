@echo off
title Flow Voice AI
cd /d "%~dp0"
echo ===================================================
echo   Iniciando Flow Voice AI...
echo ===================================================
".venv\Scripts\python.exe" -m src.app
pause
