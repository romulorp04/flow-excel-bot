import { UserRow } from "@/lib/parseHtmlExcel";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface DataPreviewTableProps {
  data: UserRow[];
}

export function DataPreviewTable({ data }: DataPreviewTableProps) {
  if (data.length === 0) return null;

  const conselhos = [...new Set(data.map((r) => r.conselho.toUpperCase().trim()))];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Dados importados — {data.length} registro(s)</h3>
        <div className="flex gap-1.5">
          {conselhos.map((c) => (
            <Badge key={c} variant="secondary" className="text-xs">{c}</Badge>
          ))}
        </div>
      </div>
      <div className="rounded-lg border overflow-hidden">
        <div className="max-h-[280px] overflow-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/60">
                <TableHead className="font-semibold text-xs w-8">#</TableHead>
                <TableHead className="font-semibold text-xs">Nome</TableHead>
                <TableHead className="font-semibold text-xs">CPF</TableHead>
                <TableHead className="font-semibold text-xs">E-Mail</TableHead>
                <TableHead className="font-semibold text-xs">Conselho</TableHead>
                <TableHead className="font-semibold text-xs">Profissão</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((row) => (
                <TableRow key={row.id} className="text-sm">
                  <TableCell className="text-muted-foreground text-xs">{row.id}</TableCell>
                  <TableCell className="font-medium">{row.nome}</TableCell>
                  <TableCell className="font-mono text-xs">{row.cpf}</TableCell>
                  <TableCell className="text-xs">{row.email}</TableCell>
                  <TableCell><Badge variant="outline" className="text-xs">{row.conselho}</Badge></TableCell>
                  <TableCell className="text-xs">{row.profissao}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
