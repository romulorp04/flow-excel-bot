# Consulta CREA-MG — Aplicação Web

## Arquitetura

```
┌─────────────────────┐         ┌──────────────────────────┐
│   FRONTEND (React)  │  HTTP   │   BACKEND (Python/FastAPI)│
│   Porta 8080        │ ──────► │   Porta 8000              │
│                     │         │                          │
│  Upload Excel       │         │  POST /api/consulta/     │
│  Tabela de dados    │         │       crea-mg            │
│  Botões de consulta │         │                          │
│  Resultados         │         │  Selenium → CREA-MG site │
│  Exportação         │         │  (automação real)        │
└─────────────────────┘         └──────────────────────────┘
```

## Estrutura de arquivos

| Arquivo | Descrição |
|---------|-----------|
| `src/pages/Index.tsx` | Tela principal do frontend |
| `src/lib/apiClient.ts` | Chamadas HTTP do frontend para o backend |
| `src/lib/parseHtmlExcel.ts` | Leitura e parsing do Excel importado |
| `backend/main.py` | **Servidor FastAPI** — ponto de entrada do backend |
| `backend/automacao/crea_mg.py` | **Automação Selenium** — consulta real ao site do CREA-MG |
| `backend/automacao/browser.py` | Configuração do Chrome/Selenium com opções stealth |
| `backend/requirements.txt` | Dependências Python do backend |

## Como rodar (modo fácil)

### Pré-requisitos
- **Node.js 18+** e **npm**
- **Python 3.10+**
- **Google Chrome** instalado

### Comando único

**Windows** — recomendado: clique duplo em `start_all.bat` ou execute no terminal:
```
start_all.bat
```

Esse script:
- instala dependências do backend e frontend
- sobe o backend em **http://localhost:8000**
- espera o health check em **/api/health** responder
- só então sobe o frontend em **http://localhost:8080**

**Linux / Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Scripts locais

| Arquivo | Função |
|---------|--------|
| `start_backend.bat` | Instala dependências Python e sobe o backend em `http://localhost:8000` |
| `start_frontend.bat` | Sobe apenas o frontend em `http://localhost:8080` |
| `start_all.bat` | Sobe backend, valida `/api/health` e depois sobe o frontend |

O fluxo recomendado no Windows é usar **`start_all.bat`**.

Acesse: **http://localhost:8080**

### Rodar manualmente (avançado)

Terminal 1 — Backend:
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Terminal 2 — Frontend:
```bash
npm install
npm run dev
```

Validação mínima do backend:

```bash
curl http://localhost:8000/api/health
```

Resposta esperada:

```json
{"status":"ok"}
```

## Fluxo de uso

1. Abra o frontend no navegador
2. Faça upload do arquivo Excel padrão (.xls)
3. Os dados serão exibidos na tabela de pré-visualização
4. Clique em **"Consultar CREA-MG"** para executar a automação
5. O backend acessa o site real do CREA-MG via Selenium para cada CPF
6. Os resultados aparecem na tabela com status individual por linha
7. Exporte os resultados em Excel

## Erros comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `Backend fora do ar em http://localhost:8000` | Backend não está rodando | Execute `start_all.bat` ou `start_backend.bat` |
| `Campo CPF não encontrado` | Página do CREA mudou | Revisar seletores em `crea_mg.py` |
| `Timeout no resultado` | Site do CREA lento/fora do ar | Tentar novamente mais tarde |
