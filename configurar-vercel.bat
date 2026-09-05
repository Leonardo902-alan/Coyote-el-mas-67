@echo off
cd /d "%~dp0"
echo.
echo  Configuracion Vercel - Fish Audio
echo  --------------------------------
echo.
echo  Necesitas DOS valores distintos:
echo.
echo  1) FISH_AUDIO_API_KEY  = fish.audio/app/api-keys  (API Key)
echo  2) FISH_AUDIO_VOICE_ID = 9441e8efd51b4cffb9b35fcb32d91ae6  (ID del modelo)
echo  3) FISH_AUDIO_MODEL    = s2-pro
echo.
echo  En Vercel: Settings ^> Environment Variables ^> Add
echo  Luego Redeploy.
echo.
pause
