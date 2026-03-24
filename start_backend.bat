@echo off
setlocal
chcp 65001 >nul 2>&1
title Backend - Consulta CREA-MG
set "ROOT=%~dp0"

echo ==============================
echo   Iniciando Backend (porta 8000)
echo ==============================
echo.

call :resolve_python
if errorlevel 1 (
    echo [ERRO] Python 3 nao encontrado. Instale Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

echo Instalando dependencias do backend...
"%PYTHON_EXE%" %PYTHON_EXTRA% -m pip install --quiet --no-cache-dir -r "%ROOT%backend\requirements.txt"
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias do backend.
    pause
    exit /b 1
)

echo.
echo Backend rodando em http://localhost:8000
echo Health check: http://localhost:8000/api/health
echo Pressione Ctrl+C para encerrar.
echo.

pushd "%ROOT%backend"
"%PYTHON_EXE%" %PYTHON_EXTRA% -m uvicorn main:app --host 127.0.0.1 --port 8000
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [ERRO] O backend foi encerrado com codigo %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%

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
