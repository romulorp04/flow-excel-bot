@echo off
chcp 65001 >nul 2>&1
title Consulta CREA-MG - Aplicacao Completa

echo ============================================
echo   Consulta CREA-MG - Iniciando tudo
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+
    pause
    exit /b 1
)

:: Backend: instalar deps
echo [1/4] Instalando dependencias do backend...
cd backend
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias Python.
    pause
    exit /b 1
)
cd ..

:: Frontend: instalar deps
echo [2/4] Instalando dependencias do frontend...
call npm install --silent 2>nul

:: Subir backend em segundo plano
echo [3/4] Iniciando backend na porta 8000...
start /b "Backend" cmd /c "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 2>&1"

:: Aguardar backend
echo      Aguardando backend...
set TENTATIVAS=0
:ESPERA
timeout /t 2 /nobreak >nul
curl -sf http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    set /a TENTATIVAS+=1
    if %TENTATIVAS% GEQ 15 (
        echo [ERRO] Backend nao respondeu apos 30 segundos.
        pause
        exit /b 1
    )
    goto ESPERA
)
echo      Backend pronto!

:: Subir frontend
echo [4/4] Iniciando frontend na porta 8080...
echo.
echo ============================================
echo   PRONTO!
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:8000
echo   Ctrl+C para encerrar tudo.
echo ============================================
echo.
call npm run dev
