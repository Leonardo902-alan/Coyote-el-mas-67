@echo off
cd /d "%~dp0"
python scripts\generate_keyframes.py
echo.
echo Iniciando Cartel del Coyote...
python server.py
pause
