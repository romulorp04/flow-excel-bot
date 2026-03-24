const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export interface CanalAcessoResponse {
  email: string;
  canal: string;
  status: "sucesso" | "erro" | "nao_encontrado";
  error_message?: string;
  etapa?: string;
  url_acessada?: string;
  logs?: string[];
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

function buildDetailedError(
  baseMsg: string,
  route: string,
  extra?: { etapa?: string; url_acessada?: string; logs?: string[] }
): any {
  const err: any = new Error(baseMsg);
  err.etapa = extra?.etapa || "conexao_backend";
  err.url_acessada = extra?.url_acessada || `${BACKEND_URL}${route}`;
  err.logs = extra?.logs || [
    "O frontend tentou conectar ao backend mas ele não respondeu.",
    `URL tentada: ${BACKEND_URL}${route}`,
    "Solução: inicie o backend com 'cd backend && uvicorn main:app --port 8000'",
  ];
  return err;
}

async function fetchBackend<T>(route: string, body: object): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BACKEND_URL}${route}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (networkErr) {
    throw buildDetailedError(
      `⚠️ Backend fora do ar em ${BACKEND_URL}. ` +
      `Para iniciar: cd backend && uvicorn main:app --port 8000. ` +
      `Detalhe: ${networkErr instanceof Error ? networkErr.message : String(networkErr)}`,
      route,
    );
  }

  const json = await res.json().catch(() => null);

  if (!res.ok) {
    const detail = json?.error_message || json?.detail || `Erro HTTP ${res.status}`;
    throw buildDetailedError(detail, route, {
      etapa: json?.etapa || "resposta_backend",
      url_acessada: json?.url_acessada,
      logs: json?.logs,
    });
  }

  return json as T;
}

export async function consultarCanalAcesso(email: string): Promise<CanalAcessoResponse> {
  return fetchBackend<CanalAcessoResponse>("/api/consulta/canal-acesso", { email });
}

export async function consultarCreaMG(cpf: string): Promise<CreaResponse> {
  return fetchBackend<CreaResponse>("/api/consulta/crea-mg", { cpf });
}
