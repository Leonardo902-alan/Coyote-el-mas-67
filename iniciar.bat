@echo off
cd /d "%~dp0"

if not exist .env (
  echo.
  echo  [AVISO] No existe .env
  echo  Copia .env.example a .env y pon tu FISH_AUDIO_API_KEY
  echo.
  copy /Y .env.example .env >nul
  echo  Se creo .env - editalo con tu token de Fish Audio antes de continuar.
  pause
  exit /b 1
)

findstr /C:"tu_token" .env >nul 2>&1
if %errorlevel%==0 (
  echo.
  echo  [AVISO] Edita .env y reemplaza tu_token con tu API key de fish.audio
  pause
  exit /b 1
)

echo.
echo  Cartel del Coyote - modo local
echo  Voz IA: Fish Audio ^(desde .env^)
echo  Abre: http://127.0.0.1:5000
echo.
python server.py
pause
