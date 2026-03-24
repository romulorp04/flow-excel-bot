@echo off
chcp 65001 >nul 2>&1
title Frontend - Consulta CREA-MG

echo ==============================
echo   Iniciando Frontend (porta 8080)
echo ==============================
echo.

call npm install --silent 2>nul
echo Frontend rodando em http://localhost:8080
echo Pressione Ctrl+C para encerrar.
echo.
call npm run dev
