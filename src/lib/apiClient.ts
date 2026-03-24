const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export interface CanalAcessoResponse {
  email: string;
  canal: string;
  status: "sucesso" | "erro" | "nao_encontrado";
  error_message?: string;
}

export interface CreaResponse {
  cpf: string;
  nome_crea: string;
  situacao_crea: string;
  titulo_crea: string;
  status: "sucesso" | "erro" | "nao_encontrado";
  error_message?: string;
  etapa?: string;
  url_acessada?: string;
  logs?: string[];
}

async function parseResponse<T>(res: Response): Promise<T> {
  const body = await res.json().catch(() => null);

  if (!res.ok) {
    const detail = body?.error_message || body?.detail || `Erro HTTP ${res.status}`;
    throw new Error(detail);
  }

  return body as T;
}

export async function consultarCanalAcesso(email: string): Promise<CanalAcessoResponse> {
  const res = await fetch(`${BACKEND_URL}/api/consulta/canal-acesso`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  return parseResponse<CanalAcessoResponse>(res);
}

export async function consultarCreaMG(cpf: string): Promise<CreaResponse> {
  let res: Response;
  try {
    res = await fetch(`${BACKEND_URL}/api/consulta/crea-mg`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cpf }),
    });
  } catch (networkErr) {
    const err: any = new Error(
      `⚠️ Backend fora do ar em ${BACKEND_URL}. ` +
      `Para iniciar: cd backend && uvicorn main:app --port 8000. ` +
      `Detalhe: ${networkErr instanceof Error ? networkErr.message : String(networkErr)}`
    );
    err.etapa = "conexao_backend";
    err.url_acessada = `${BACKEND_URL}/api/consulta/crea-mg`;
    err.logs = [
      "O frontend tentou conectar ao backend mas ele não respondeu.",
      `URL tentada: ${BACKEND_URL}/api/consulta/crea-mg`,
      "Solução: inicie o backend Python com 'cd backend && uvicorn main:app --port 8000'",
    ];
    throw err;
  }

  const body = await res.json().catch(() => null);

  if (!res.ok) {
    const detail = body?.error_message || body?.detail || `Erro HTTP ${res.status}`;
    const err: any = new Error(detail);
    err.etapa = body?.etapa || "resposta_backend";
    err.url_acessada = body?.url_acessada;
    err.logs = body?.logs;
    throw err;
  }

  return body as CreaResponse;
}
