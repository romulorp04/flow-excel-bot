import { useState, useEffect } from "react";
import { Wifi, WifiOff } from "lucide-react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const POLL_INTERVAL = 10_000;

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