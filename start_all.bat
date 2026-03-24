@echo off
setlocal
chcp 65001 >nul 2>&1
title Consulta CREA-MG - Aplicacao Completa
set "ROOT=%~dp0"
set "BACKEND_LOG=%TEMP%\consulta-crea-backend.log"

echo ============================================
echo   Consulta CREA-MG - Iniciando tudo
echo ============================================
echo.

call :resolve_python
if errorlevel 1 (
    echo [ERRO] Python 3 nao encontrado. Instale Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERRO] npm nao encontrado. Instale Node.js 18+ e tente novamente.
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias do backend...
"%PYTHON_EXE%" %PYTHON_EXTRA% -m pip install --quiet --no-cache-dir -r "%ROOT%backend\requirements.txt"
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias do backend.
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias do frontend...
pushd "%ROOT%"
call npm install --silent
if errorlevel 1 (
    popd
    echo [ERRO] Falha ao instalar dependencias do frontend.
    pause
    exit /b 1
)
popd

call :backend_healthy
if not errorlevel 1 (
    echo [3/4] Backend ja esta respondendo em http://localhost:8000
    goto BACKEND_OK
)

echo [3/4] Iniciando backend na porta 8000...
if exist "%BACKEND_LOG%" del "%BACKEND_LOG%" >nul 2>&1
start "Backend - Consulta CREA-MG" /min /d "%ROOT%backend" cmd /c ""%PYTHON_EXE%" %PYTHON_EXTRA% -m uvicorn main:app --host 127.0.0.1 --port 8000 > "%BACKEND_LOG%" 2>&1"

echo      Aguardando backend em /api/health...
set /a TENTATIVAS=0
:ESPERA_BACKEND
call :backend_healthy
if not errorlevel 1 goto BACKEND_OK
set /a TENTATIVAS+=1
if %TENTATIVAS% GEQ 30 (
    echo [ERRO] Backend nao respondeu em http://localhost:8000/api/health.
    if exist "%BACKEND_LOG%" (
        echo.
        echo ===== LOG DO BACKEND =====
        type "%BACKEND_LOG%"
        echo ==========================
    )
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto ESPERA_BACKEND

:BACKEND_OK
echo      Backend pronto!
echo [4/4] Iniciando frontend na porta 8080...
echo.
echo ============================================
echo   PRONTO!
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:8000
echo   Health:   http://localhost:8000/api/health
echo ============================================
echo.

pushd "%ROOT%"
call npm run dev
set "FRONTEND_EXIT=%ERRORLEVEL%"
popd
exit /b %FRONTEND_EXIT%

:resolve_python
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    set "PYTHON_EXTRA="
    exit /b 0
)

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    set "PYTHON_EXTRA=-3"
    exit /b 0
)

exit /b 1

:backend_healthy
powershell -NoProfile -Command "try { $resp = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/api/health' -TimeoutSec 2; if ($resp.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
exit /b %ERRORLEVEL%
