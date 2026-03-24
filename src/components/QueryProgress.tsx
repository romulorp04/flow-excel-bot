import { Progress } from "@/components/ui/progress";
import { Loader2 } from "lucide-react";

interface QueryProgressProps {
  label: string;
  current: number;
  total: number;
  currentItem?: string;
}

export function QueryProgress({ label, current, total, currentItem }: QueryProgressProps) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className="rounded-lg border bg-card p-4 space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-accent" />
          {label}
        </span>
        <span className="text-muted-foreground">{current}/{total} ({pct}%)</span>
      </div>
      <Progress value={pct} className="h-2" />
      {currentItem && (
        <p className="text-xs text-muted-foreground truncate">Consultando: {currentItem}</p>
      )}
    </div>
  );
}
