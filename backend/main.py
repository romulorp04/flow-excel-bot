"""
Backend FastAPI — Consulta CREA-MG via automação Selenium.

Iniciar com:
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from automacao.crea_mg import consultar_crea_mg

app = FastAPI(title="Consulta CREA-MG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreaRequest(BaseModel):
    cpf: str


class CreaResponse(BaseModel):
    cpf: str
    nome_crea: str = ""
    situacao_crea: str = ""
    titulo_crea: str = ""
    status: str = "sucesso"
    error_message: str = ""
    etapa: str = ""
    url_acessada: str = ""
    logs: list[str] = []


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/consulta/crea-mg", response_model=CreaResponse)
def rota_consulta_crea(req: CreaRequest):
    cpf_limpo = req.cpf.replace(".", "").replace("-", "").replace(" ", "")
    resultado = consultar_crea_mg(cpf_limpo)
    return CreaResponse(**resultado)
