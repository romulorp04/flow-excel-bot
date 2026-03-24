@echo off
chcp 65001 >nul 2>&1
title Backend - Consulta CREA-MG

echo ==============================
echo   Iniciando Backend (porta 8000)
echo ==============================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+
    pause
    exit /b 1
)

echo Instalando dependencias...
cd backend
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo Backend rodando em http://localhost:8000
echo Pressione Ctrl+C para encerrar.
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
