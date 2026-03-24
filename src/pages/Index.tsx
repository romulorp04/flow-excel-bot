import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { FileUploadArea } from "@/components/FileUploadArea";
import { DataPreviewTable } from "@/components/DataPreviewTable";
import { QueryButtons } from "@/components/QueryButtons";
import { QueryProgress } from "@/components/QueryProgress";
import { ResultsTable } from "@/components/ResultsTable";
import { ExportButton } from "@/components/ExportButton";
import { parseHtmlExcel, UserRow, QueryResult } from "@/lib/parseHtmlExcel";
import { consultarCanalAcesso, consultarCreaMG } from "@/lib/apiClient";
import { toast } from "sonner";
import { FileSpreadsheet } from "lucide-react";
import { BackendStatus, BackendOfflineBanner } from "@/components/BackendStatus";
import { BackendDownload } from "@/components/BackendDownload";

const Index = () => {
  const [data, setData] = useState<UserRow[]>([]);
  const [fileName, setFileName] = useState<string>();
  const [fileError, setFileError] = useState<string>();
  const [isLoaded, setIsLoaded] = useState(false);

  const [canalResults, setCanalResults] = useState<QueryResult[]>([]);
  const [creaResults, setCreaResults] = useState<QueryResult[]>([]);

  const [isQueryingCanal, setIsQueryingCanal] = useState(false);
  const [isQueryingCrea, setIsQueryingCrea] = useState(false);
  const [canalProgress, setCanalProgress] = useState({ current: 0, total: 0, item: "" });
  const [creaProgress, setCreaProgress] = useState({ current: 0, total: 0, item: "" });

  const conselhos = [...new Set(data.map((r) => r.conselho.toUpperCase().trim()))];
  const showCftButton = conselhos.some((c) => c.includes("CFT") || c.includes("CRT"));
  const showCauButton = conselhos.includes("CAU");

  const handleFileLoaded = useCallback((content: string, name: string) => {
    const { data: parsed, error } = parseHtmlExcel(content);
    if (error) {
      setFileError(error);
      setIsLoaded(false);
      setData([]);
      toast.error(error);
      return;
    }

    setData(parsed);
    setFileName(name);
    setFileError(undefined);
    setIsLoaded(true);
    setCanalResults([]);
    setCreaResults([]);
    toast.success(`${parsed.length} registro(s) carregado(s) com sucesso.`);
  }, []);

  const handleQueryCanal = useCallback(async () => {
    setIsQueryingCanal(true);
    const results: QueryResult[] = data.map((r) => ({ ...r, statusCanalAcesso: "pendente" }));
    setCanalResults([...results]);
    setCanalProgress({ current: 0, total: data.length, item: "" });

    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      results[i].statusCanalAcesso = "consultando";
      results[i].detalheCanalAcesso = "Consulta em andamento no backend.";
      setCanalResults([...results]);
      setCanalProgress({ current: i, total: data.length, item: row.email });

      try {
        const res = await consultarCanalAcesso(row.email);
        results[i].canalAcesso = res.canal;
        results[i].statusCanalAcesso = res.status;
        results[i].detalheCanalAcesso = res.error_message || (res.status === "sucesso" ? "Consulta concluída com sucesso." : "Registro não encontrado na consulta.");
      } catch (error: any) {
        results[i].statusCanalAcesso = "erro";
        results[i].detalheCanalAcesso = error instanceof Error ? error.message : "Falha ao consultar o backend.";
      }

      setCanalResults([...results]);
    }

    setCanalProgress({ current: data.length, total: data.length, item: "" });
    setIsQueryingCanal(false);
    toast.success("Consulta de Canal de Acesso finalizada.");
  }, [data]);

  const handleQueryCrea = useCallback(async () => {
    setIsQueryingCrea(true);
    const results: QueryResult[] = data.map((r) => ({
      ...r,
      statusCrea: r.conselho.trim().toUpperCase() === "CREA" ? "pendente" : "ignorado",
      detalheCrea: r.conselho.trim().toUpperCase() === "CREA" ? "Aguardando processamento." : "Consulta ignorada porque o conselho da linha não é CREA.",
    }));

    setCreaResults([...results]);
    const creaRows = results.filter((r) => r.statusCrea === "pendente");
    setCreaProgress({ current: 0, total: creaRows.length, item: "" });

    let done = 0;
    for (let i = 0; i < results.length; i++) {
      if (results[i].statusCrea !== "pendente") continue;

      results[i].statusCrea = "consultando";
      results[i].detalheCrea = "Iniciando automação Selenium no backend.";
      results[i].etapaCrea = "inicializacao";
      results[i].urlCrea = undefined;
      results[i].logsCrea = [];
      setCreaResults([...results]);
      setCreaProgress({ current: done, total: creaRows.length, item: results[i].cpf });

      try {
        const res = await consultarCreaMG(results[i].cpf);
        results[i].nomeCrea = res.nome_crea;
        results[i].situacaoCrea = res.situacao_crea;
        results[i].tituloCrea = res.titulo_crea;
        results[i].statusCrea = res.status;
        results[i].detalheCrea = res.error_message || (res.status === "sucesso" ? "Consulta concluída com sucesso." : "Resultado vazio ou não encontrado.");
        results[i].etapaCrea = res.etapa;
        results[i].urlCrea = res.url_acessada;
        results[i].logsCrea = res.logs;
      } catch (error: any) {
        results[i].statusCrea = "erro";
        results[i].detalheCrea = error instanceof Error ? error.message : "Falha de comunicação com o backend da automação.";
        results[i].etapaCrea = error?.etapa || "requisicao_frontend";
        results[i].urlCrea = error?.url_acessada;
        results[i].logsCrea = error?.logs;
      }

      done++;
      setCreaResults([...results]);
    }

    setCreaProgress({ current: creaRows.length, total: creaRows.length, item: "" });
    setIsQueryingCrea(false);
    toast.success("Consulta ao CREA-MG finalizada.");
  }, [data]);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container max-w-6xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center">
            <FileSpreadsheet className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground leading-tight">Consulta de Canal de Acesso e CREA-MG</h1>
            <p className="text-xs text-muted-foreground">Sistema de consulta automatizada</p>
          </div>
        <BackendStatus />
        </div>
      </header>

      <main className="container max-w-6xl mx-auto px-4 py-6 space-y-6">
        <BackendOfflineBanner />
        <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-card rounded-xl border p-6 space-y-5">
          <h2 className="text-base font-semibold text-foreground">1. Importar planilha de usuários</h2>
          <FileUploadArea onFileLoaded={handleFileLoaded} isLoaded={isLoaded} fileName={fileName} error={fileError} />

          {isLoaded && data.length > 0 && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}>
              <DataPreviewTable data={data} />
            </motion.div>
          )}
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: isLoaded ? 1 : 0.5, y: 0 }}
          className="bg-card rounded-xl border p-6"
        >
          <h2 className="text-base font-semibold text-foreground mb-4">2. Executar consultas</h2>
          <QueryButtons
            enabled={isLoaded && data.length > 0}
            showCftButton={showCftButton}
            showCauButton={showCauButton}
            isQueryingCanal={isQueryingCanal}
            isQueryingCrea={isQueryingCrea}
            onQueryCanal={handleQueryCanal}
            onQueryCrea={handleQueryCrea}
          />
        </motion.section>

        {isQueryingCanal && <QueryProgress label="Consultando Canal de Acesso..." current={canalProgress.current} total={canalProgress.total} currentItem={canalProgress.item} />}
        {isQueryingCrea && <QueryProgress label="Consultando CREA-MG..." current={creaProgress.current} total={creaProgress.total} currentItem={creaProgress.item} />}

        {canalResults.length > 0 && (
          <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card rounded-xl border p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-foreground">Resultado — Canal de Acesso</h2>
            </div>
            <ResultsTable data={canalResults} type="canal" />
          </motion.section>
        )}

        {creaResults.length > 0 && (
          <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card rounded-xl border p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-foreground">Resultado — CREA-MG</h2>
            </div>
            <ResultsTable data={creaResults} type="crea" />
          </motion.section>
        )}

        {(canalResults.length > 0 || creaResults.length > 0) && (
          <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card rounded-xl border p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-foreground">3. Exportar resultados</h2>
              <ExportButton canalResults={canalResults} creaResults={creaResults} />
            </div>
          </motion.section>
        )}
      </main>
    </div>
  );
};

export default Index;
