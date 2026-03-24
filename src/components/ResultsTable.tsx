import { QueryResult } from "@/lib/parseHtmlExcel";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, AlertTriangle, Clock, MinusCircle } from "lucide-react";

interface ResultsTableProps {
  data: QueryResult[];
  type: "canal" | "crea";
}

function StatusBadge({ status }: { status?: string }) {
  switch (status) {
    case "sucesso":
      return <Badge className="bg-success text-success-foreground gap-1 text-xs"><CheckCircle2 className="h-3 w-3" />Sucesso</Badge>;
    case "erro":
      return <Badge variant="destructive" className="gap-1 text-xs"><XCircle className="h-3 w-3" />Erro</Badge>;
    case "nao_encontrado":
      return <Badge variant="secondary" className="gap-1 text-xs"><AlertTriangle className="h-3 w-3" />Não encontrado</Badge>;
    case "consultando":
      return <Badge className="bg-accent text-accent-foreground gap-1 text-xs"><Clock className="h-3 w-3 animate-pulse" />Consultando</Badge>;
    case "ignorado":
      return <Badge variant="outline" className="gap-1 text-xs"><MinusCircle className="h-3 w-3" />Ignorado</Badge>;
    default:
      return <Badge variant="outline" className="gap-1 text-xs text-muted-foreground"><Clock className="h-3 w-3" />Pendente</Badge>;
  }
}

export function ResultsTable({ data, type }: ResultsTableProps) {
  if (data.length === 0) return null;

  return (
    <div className="rounded-lg border overflow-hidden">
      <div className="max-h-[400px] overflow-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/60">
              <TableHead className="font-semibold text-xs">Nome</TableHead>
              <TableHead className="font-semibold text-xs">CPF</TableHead>
              <TableHead className="font-semibold text-xs">E-Mail</TableHead>
              <TableHead className="font-semibold text-xs">Conselho</TableHead>
              <TableHead className="font-semibold text-xs">Profissão</TableHead>
              {type === "canal" && <TableHead className="font-semibold text-xs">Canal de Acesso</TableHead>}
              {type === "crea" && (
                <>
                  <TableHead className="font-semibold text-xs">Nome CREA</TableHead>
                  <TableHead className="font-semibold text-xs">Situação CREA</TableHead>
                  <TableHead className="font-semibold text-xs">Título CREA</TableHead>
                </>
              )}
              <TableHead className="font-semibold text-xs">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row) => (
              <TableRow key={row.id} className="text-sm">
                <TableCell className="font-medium">{row.nome}</TableCell>
                <TableCell className="font-mono text-xs">{row.cpf}</TableCell>
                <TableCell className="text-xs">{row.email}</TableCell>
                <TableCell><Badge variant="outline" className="text-xs">{row.conselho}</Badge></TableCell>
                <TableCell className="text-xs">{row.profissao}</TableCell>
                {type === "canal" && <TableCell className="text-xs font-medium">{row.canalAcesso || "—"}</TableCell>}
                {type === "crea" && (
                  <>
                    <TableCell className="text-xs">{row.nomeCrea || "—"}</TableCell>
                    <TableCell className="text-xs">{row.situacaoCrea || "—"}</TableCell>
                    <TableCell className="text-xs">{row.tituloCrea || "—"}</TableCell>
                  </>
                )}
                <TableCell>
                  <StatusBadge status={type === "canal" ? row.statusCanalAcesso : row.statusCrea} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
