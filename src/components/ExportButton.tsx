import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { QueryResult } from "@/lib/parseHtmlExcel";
import * as XLSX from "xlsx";

interface ExportButtonProps {
  canalResults: QueryResult[];
  creaResults: QueryResult[];
}

export function ExportButton({ canalResults, creaResults }: ExportButtonProps) {
  const hasCanal = canalResults.some((r) => r.statusCanalAcesso === "sucesso" || r.statusCanalAcesso === "nao_encontrado" || r.statusCanalAcesso === "erro");
  const hasCrea = creaResults.some((r) => r.statusCrea === "sucesso" || r.statusCrea === "nao_encontrado" || r.statusCrea === "erro" || r.statusCrea === "ignorado");

  if (!hasCanal && !hasCrea) return null;

  const handleExport = () => {
    const wb = XLSX.utils.book_new();

    if (hasCanal) {
      const wsData = canalResults.map((r) => ({
        Nome: r.nome,
        CPF: r.cpf,
        "E-Mail": r.email,
        Conselho: r.conselho,
        Profissão: r.profissao,
        "Canal de Acesso": r.canalAcesso || "",
        Status: r.statusCanalAcesso || "",
        "Detalhe Canal": r.detalheCanalAcesso || "",
      }));
      const ws = XLSX.utils.json_to_sheet(wsData);
      XLSX.utils.book_append_sheet(wb, ws, "Canal de Acesso");
    }

    if (hasCrea) {
      const wsData = creaResults.map((r) => ({
        Nome: r.nome,
        CPF: r.cpf,
        "E-Mail": r.email,
        Conselho: r.conselho,
        Profissão: r.profissao,
        "Nome CREA": r.nomeCrea || "",
        "Situação CREA": r.situacaoCrea || "",
        "Título CREA": r.tituloCrea || "",
        Status: r.statusCrea || "",
        "Detalhe CREA": r.detalheCrea || "",
        "Etapa CREA": r.etapaCrea || "",
        "URL CREA": r.urlCrea || "",
      }));
      const ws = XLSX.utils.json_to_sheet(wsData);
      XLSX.utils.book_append_sheet(wb, ws, "CREA-MG");
    }

    XLSX.writeFile(wb, `Resultado_Consultas_${new Date().toISOString().slice(0, 10)}.xlsx`);
  };

  return (
    <Button onClick={handleExport} variant="outline" className="gap-2">
      <Download className="h-4 w-4" /> Exportar Resultados
    </Button>
  );
}
