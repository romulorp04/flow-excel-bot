// Backend API client
// Configure BACKEND_URL to point to your FastAPI server

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export interface CanalAcessoResponse {
  email: string;
  canal: string;
  status: "sucesso" | "erro" | "nao_encontrado";
}

export interface CreaResponse {
  cpf: string;
  nome_crea: string;
  situacao_crea: string;
  titulo_crea: string;
  status: "sucesso" | "erro" | "nao_encontrado";
}

export async function consultarCanalAcesso(email: string): Promise<CanalAcessoResponse> {
  const res = await fetch(`${BACKEND_URL}/api/consulta/canal-acesso`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

export async function consultarCreaMG(cpf: string): Promise<CreaResponse> {
  const res = await fetch(`${BACKEND_URL}/api/consulta/crea-mg`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cpf }),
  });
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}
