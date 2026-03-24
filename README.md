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

**Windows** — clique duplo em `start.bat` ou execute no terminal:
```
start.bat
```

**Linux / Mac:**
```bash
chmod +x start.sh
./start.sh
```

O script instala tudo, sobe backend (porta **8000**) e frontend (porta **8080**), e abre automaticamente.

Acesse: **http://localhost:8080**

### Rodar manualmente (avançado)

Terminal 1 — Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000
```

Terminal 2 — Frontend:
```bash
npm install
npm run dev
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
| `Failed to fetch` | Backend não está rodando | Inicie o backend com `uvicorn` |
| `Campo CPF não encontrado` | Página do CREA mudou | Revisar seletores em `crea_mg.py` |
| `Timeout no resultado` | Site do CREA lento/fora do ar | Tentar novamente mais tarde |
