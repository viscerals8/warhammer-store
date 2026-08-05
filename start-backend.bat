@echo off
echo ========================================
echo Warhammer Store - Iniciando Backend
echo ========================================

cd backend

if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt > nul 2>&1

echo.
echo Inicializando base de datos...
python init_db.py

echo.
echo ========================================
echo Iniciando servidor FastAPI...
echo API disponible en: http://localhost:8000
echo Docs en: http://localhost:8000/docs
echo ========================================
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
