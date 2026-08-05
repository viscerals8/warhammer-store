@echo off
echo ========================================
echo Warhammer Store - Iniciando Frontend
echo ========================================

cd frontend

if not exist "node_modules\" (
    echo Instalando dependencias...
    npm install
)

echo.
echo ========================================
echo Iniciando servidor Angular...
echo Aplicacion disponible en: http://localhost:4200
echo ========================================
echo.

ng serve --open

pause
