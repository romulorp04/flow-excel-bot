export interface UserRow {
  id: number;
  situacao: string;
  nome: string;
  cpf: string;
  rg: string;
  numRegProfissional: string;
  conselho: string;
  profissao: string;
  email: string;
  telefone: string;
  celular: string;
  endereco: string;
  bairro: string;
  cep: string;
  municipio: string;
  estado: string;
}

export interface QueryResult extends UserRow {
  canalAcesso?: string;
  nomeCrea?: string;
  situacaoCrea?: string;
  tituloCrea?: string;
  statusCanalAcesso?: "pendente" | "consultando" | "sucesso" | "erro" | "nao_encontrado";
  statusCrea?: "pendente" | "consultando" | "sucesso" | "erro" | "nao_encontrado" | "ignorado";
}

const EXPECTED_HEADERS = ["Situação", "Nome", "CPF", "RG", "Nº Reg. Profissional", "Conselho", "Profissão", "E-Mail", "Telefone", "Celular", "Endereço", "Bairro", "CEP", "Município", "Estado"];

export function parseHtmlExcel(htmlContent: string): { data: UserRow[]; error?: string } {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlContent, "text/html");
  const table = doc.querySelector("table");

  if (!table) {
    return { data: [], error: "Nenhuma tabela encontrada no arquivo." };
  }

  const rows = table.querySelectorAll("tr");
  if (rows.length < 2) {
    return { data: [], error: "A tabela não contém dados suficientes." };
  }

  const headerCells = rows[0].querySelectorAll("th, td");
  const headers = Array.from(headerCells).map((c) => c.textContent?.trim() || "");

  // Validate minimum required columns
  const requiredCols = ["Nome", "CPF", "E-Mail", "Conselho"];
  const missing = requiredCols.filter((col) => !headers.includes(col));
  if (missing.length > 0) {
    return { data: [], error: `Colunas obrigatórias não encontradas: ${missing.join(", ")}` };
  }

  const colIndex = (name: string) => headers.indexOf(name);

  const data: UserRow[] = [];
  for (let i = 1; i < rows.length; i++) {
    const cells = rows[i].querySelectorAll("td");
    const get = (name: string) => {
      const idx = colIndex(name);
      return idx >= 0 ? cells[idx]?.textContent?.trim() || "" : "";
    };

    const cpf = get("CPF").replace(/\D/g, "").padStart(11, "0");

    data.push({
      id: i,
      situacao: get("Situação"),
      nome: get("Nome"),
      cpf,
      rg: get("RG"),
      numRegProfissional: get("Nº Reg. Profissional"),
      conselho: get("Conselho"),
      profissao: get("Profissão"),
      email: get("E-Mail"),
      telefone: get("Telefone"),
      celular: get("Celular"),
      endereco: get("Endereço"),
      bairro: get("Bairro"),
      cep: get("CEP"),
      municipio: get("Município"),
      estado: get("Estado"),
    });
  }

  return { data };
}
