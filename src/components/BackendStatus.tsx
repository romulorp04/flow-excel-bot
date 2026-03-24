import { useState, useEffect, useCallback } from "react";
import { Wifi, WifiOff, Copy, Check, ExternalLink, Terminal, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const POLL_INTERVAL = 8_000;

export function useBackendOnline() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    const check = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/health`, { signal: AbortSignal.timeout(3000) });
        if (active) setOnline(res.ok);
      } catch {
        if (active) setOnline(false);
      }
    };
    check();
    const id = setInterval(check, POLL_INTERVAL);
    return () => { active = false; clearInterval(id); };
  }, []);

  return online;
}

export function BackendStatus() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    const check = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/health`, { signal: AbortSignal.timeout(3000) });
        if (active) setOnline(res.ok);
      } catch {
        if (active) setOnline(false);
      }
    };
    check();
    const id = setInterval(check, POLL_INTERVAL);
    return () => { active = false; clearInterval(id); };
  }, []);

  if (online === null) return null;

  return (
    <div
      className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full transition-colors ${
        online
          ? "bg-green-500/15 text-green-600 dark:text-green-400"
          : "bg-destructive/15 text-destructive"
      }`}
      title={online ? `Backend online em ${BACKEND_URL}` : `Backend offline em ${BACKEND_URL}`}
    >
      {online ? <Wifi className="h-3.5 w-3.5" /> : <WifiOff className="h-3.5 w-3.5" />}
      <span>{online ? "Backend online" : "Backend offline"}</span>
    </div>
  );
}

export function BackendOfflineBanner() {
  const [online, setOnline] = useState<boolean | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let active = true;
    const check = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/health`, { signal: AbortSignal.timeout(3000) });
        if (active) setOnline(res.ok);
      } catch {
        if (active) setOnline(false);
      }
    };
    check();
    const id = setInterval(check, POLL_INTERVAL);
    return () => { active = false; clearInterval(id); };
  }, []);

  const handleCopy = useCallback((text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      toast.success("Comando copiado!");
      setTimeout(() => setCopied(false), 2000);
    });
  }, []);

  if (online !== false) return null;

  return (
    <div className="border border-destructive/30 bg-destructive/5 rounded-xl p-5 space-y-4">
      <div className="flex items-start gap-3">
        <div className="h-9 w-9 rounded-lg bg-destructive/15 flex items-center justify-center shrink-0 mt-0.5">
          <WifiOff className="h-5 w-5 text-destructive" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">Backend não detectado</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            O servidor de automação não está respondendo em <code className="bg-muted px-1 py-0.5 rounded text-[11px]">{BACKEND_URL}</code>. 
            Siga os passos abaixo para iniciá-lo.
          </p>
        </div>
      </div>

      {/* Pré-requisitos */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-foreground flex items-center gap-1.5">
          <Download className="h-3.5 w-3.5" /> Pré-requisitos (instale se ainda não tiver)
        </h4>
        <div className="grid sm:grid-cols-2 gap-2">
          <a
            href="https://www.python.org/downloads/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs bg-muted/60 hover:bg-muted rounded-lg px-3 py-2.5 transition-colors group"
          >
            <span className="font-medium text-foreground">Python 3.10+</span>
            <ExternalLink className="h-3 w-3 text-muted-foreground group-hover:text-foreground transition-colors ml-auto" />
          </a>
          <a
            href="https://nodejs.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs bg-muted/60 hover:bg-muted rounded-lg px-3 py-2.5 transition-colors group"
          >
            <span className="font-medium text-foreground">Node.js 18+</span>
            <ExternalLink className="h-3 w-3 text-muted-foreground group-hover:text-foreground transition-colors ml-auto" />
          </a>
          <a
            href="https://googlechromelabs.github.io/chrome-for-testing/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs bg-muted/60 hover:bg-muted rounded-lg px-3 py-2.5 transition-colors group"
          >
            <span className="font-medium text-foreground">ChromeDriver</span>
            <ExternalLink className="h-3 w-3 text-muted-foreground group-hover:text-foreground transition-colors ml-auto" />
          </a>
          <a
            href="https://www.google.com/chrome/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs bg-muted/60 hover:bg-muted rounded-lg px-3 py-2.5 transition-colors group"
          >
            <span className="font-medium text-foreground">Google Chrome</span>
            <ExternalLink className="h-3 w-3 text-muted-foreground group-hover:text-foreground transition-colors ml-auto" />
          </a>
        </div>
      </div>

      {/* Passos */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-foreground flex items-center gap-1.5">
          <Terminal className="h-3.5 w-3.5" /> Como iniciar
        </h4>

        <div className="space-y-1.5">
          <Step n={1} title="Opção rápida — duplo-clique no arquivo:">
            <CodeBlock text="start_all.bat" onCopy={handleCopy} copied={copied} />
            <p className="text-[11px] text-muted-foreground mt-1">
              Esse script instala as dependências, sobe o backend na porta 8000, espera ele ficar pronto e depois abre o frontend.
            </p>
          </Step>

          <Step n={2} title="Ou, pelo terminal (CMD / PowerShell):">
            <CodeBlock text="cd backend && pip install -r requirements.txt && python -m uvicorn main:app --host 127.0.0.1 --port 8000" onCopy={handleCopy} copied={copied} />
          </Step>

          <Step n={3} title="Verifique se está funcionando:">
            <CodeBlock text={`curl ${BACKEND_URL}/api/health`} onCopy={handleCopy} copied={copied} />
            <p className="text-[11px] text-muted-foreground mt-1">
              Deve retornar <code className="bg-muted px-1 py-0.5 rounded">{`{"status":"ok"}`}</code>. Esta página recarrega automaticamente ao detectar o backend.
            </p>
          </Step>
        </div>
      </div>
    </div>
  );
}

function Step({ n, title, children }: { n: number; title: string; children: React.ReactNode }) {
  return (
    <div className="bg-muted/40 rounded-lg px-3 py-2.5">
      <p className="text-xs text-foreground">
        <span className="inline-flex items-center justify-center h-4 w-4 rounded-full bg-primary text-primary-foreground text-[10px] font-bold mr-1.5">{n}</span>
        <span className="font-medium">{title}</span>
      </p>
      <div className="mt-1.5 ml-5.5">{children}</div>
    </div>
  );
}

function CodeBlock({ text, onCopy, copied }: { text: string; onCopy: (t: string) => void; copied: boolean }) {
  return (
    <div className="flex items-center gap-1 bg-background border rounded-md px-2.5 py-1.5 font-mono text-[11px] text-foreground">
      <code className="flex-1 break-all select-all">{text}</code>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0"
        onClick={() => onCopy(text)}
        title="Copiar"
      >
        {copied ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
      </Button>
    </div>
  );
}
