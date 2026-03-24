import { Download, FolderArchive, FileText, Terminal } from "lucide-react";
import { Button } from "@/components/ui/button";

const files = [
  {
    label: "Backend completo (ZIP)",
    description: "Código FastAPI + automação + scripts de inicialização",
    href: "/downloads/backend.zip",
    icon: FolderArchive,
    primary: true,
  },
];

const scripts = [
  { label: "start_all.bat", description: "Sobe backend + frontend juntos (Windows)" },
  { label: "start_backend.bat", description: "Sobe apenas o backend na porta 8000" },
  { label: "start.sh", description: "Script para Linux / Mac" },
];

export function BackendDownload() {
  return (
    <div className="border border-border/60 bg-card rounded-xl p-5 space-y-4">
      <div className="flex items-start gap-3">
        <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
          <Download className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">Arquivos do Backend</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Baixe os arquivos necessários para rodar o servidor de automação localmente.
          </p>
        </div>
      </div>

      {/* Download principal */}
      <div className="space-y-2">
        {files.map((f) => (
          <a
            key={f.href}
            href={f.href}
            download
            className="flex items-center gap-3 bg-primary/5 hover:bg-primary/10 border border-primary/20 rounded-lg px-4 py-3 transition-colors group"
          >
            <f.icon className="h-5 w-5 text-primary shrink-0" />
            <div className="flex-1 min-w-0">
              <span className="text-sm font-semibold text-foreground">{f.label}</span>
              <p className="text-xs text-muted-foreground">{f.description}</p>
            </div>
            <Button variant="default" size="sm" className="shrink-0 pointer-events-none" tabIndex={-1}>
              <Download className="h-3.5 w-3.5 mr-1.5" />
              Baixar
            </Button>
          </a>
        ))}
      </div>

      {/* Conteúdo do zip */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
          <Terminal className="h-3.5 w-3.5" /> Scripts incluídos no ZIP
        </h4>
        <div className="grid sm:grid-cols-3 gap-2">
          {scripts.map((s) => (
            <div key={s.label} className="flex items-start gap-2 bg-muted/40 rounded-lg px-3 py-2.5">
              <FileText className="h-3.5 w-3.5 text-muted-foreground mt-0.5 shrink-0" />
              <div>
                <span className="text-xs font-medium text-foreground">{s.label}</span>
                <p className="text-[11px] text-muted-foreground leading-tight">{s.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
