@echo off
echo ========================================
echo Warhammer Store - Inicio Rapido
echo ========================================
echo.

choice /C 12 /M "Selecciona opcion: (1) Solo Backend, (2) Solo Frontend, (3) Ambos, (4) Salir"
if errorlevel 4 goto end
if errorlevel 3 goto both
if errorlevel 2 goto frontend
if errorlevel 1 goto backend

:backend
start cmd /k "cd /d %cd%\backend && call start-backend.bat"
goto end

:frontend
start cmd /k "cd /d %cd%\frontend && call start-frontend.bat"
goto end

:both
start cmd /k "cd /d %cd%\backend && call start-backend.bat"
timeout /t 5 > nul
start cmd /k "cd /d %cd%\frontend && call start-frontend.bat"
goto end

:end
echo.
echo Servicios iniciados en ventanas separadas.
echo Presiona cualquier tecla para salir...
pause > nul
