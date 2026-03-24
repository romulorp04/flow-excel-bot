#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo "  Consulta CREA-MG — Iniciando aplicação"
echo "============================================"
echo

# Instalar deps backend
echo "[1/4] Instalando dependências do backend..."
(cd backend && python3 -m pip install --quiet --no-cache-dir -r requirements.txt)

# Instalar deps frontend
echo "[2/4] Instalando dependências do frontend..."
npm install --silent

# Subir backend
echo "[3/4] Iniciando backend na porta 8000..."
(cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!
trap "kill $BACKEND_PID 2>/dev/null" EXIT

# Aguardar backend
echo "     Aguardando backend..."
for i in $(seq 1 15); do
  curl -sf http://localhost:8000/api/health >/dev/null 2>&1 && break || sleep 2
done
echo "     Backend pronto!"

# Subir frontend
echo "[4/4] Iniciando frontend na porta 8080..."
echo
echo "============================================"
echo "  PRONTO! Acesse: http://localhost:8080"
echo "  Backend: http://localhost:8000"
echo "  Ctrl+C para encerrar tudo."
echo "============================================"
echo

npm run dev
