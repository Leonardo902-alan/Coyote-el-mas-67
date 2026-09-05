@echo off
cd /d "%~dp0"
echo.
echo  Configuracion de Vercel para Fish Audio (plan Pro)
echo  ---------------------------------------------------
echo.
echo  En vercel.com ^> tu proyecto ^> Settings ^> Environment Variables
echo  anade estas dos variables:
echo.
echo    FISH_AUDIO_API_KEY = (tu token de fish.audio)
echo    FISH_AUDIO_MODEL   = s2-pro
echo.
echo  Marca Production, Preview y Development.
echo  Luego: Deployments ^> Redeploy
echo.
echo  O con Vercel CLI (si lo tienes instalado):
echo    vercel env add FISH_AUDIO_API_KEY
echo    vercel env add FISH_AUDIO_MODEL
echo.
pause
