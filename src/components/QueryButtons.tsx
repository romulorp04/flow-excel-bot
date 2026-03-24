import { Search, Building2, ExternalLink, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface QueryButtonsProps {
  enabled: boolean;
  showCftButton: boolean;
  showCauButton: boolean;
  isQueryingCanal: boolean;
  isQueryingCrea: boolean;
  onQueryCanal: () => void;
  onQueryCrea: () => void;
}

export function QueryButtons({
  enabled,
  showCftButton,
  showCauButton,
  isQueryingCanal,
  isQueryingCrea,
  onQueryCanal,
  onQueryCrea,
}: QueryButtonsProps) {
  const isAnyQuerying = isQueryingCanal || isQueryingCrea;

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-foreground">Consultas</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Button
          onClick={onQueryCanal}
          disabled={!enabled || isAnyQuerying}
          size="lg"
          className="justify-start gap-2"
        >
          {isQueryingCanal ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          Consultar Canal de Acesso
        </Button>

        <Button
          onClick={onQueryCrea}
          disabled={!enabled || isAnyQuerying}
          size="lg"
          className="justify-start gap-2"
        >
          {isQueryingCrea ? <Loader2 className="h-4 w-4 animate-spin" /> : <Building2 className="h-4 w-4" />}
          Consultar CREA-MG
        </Button>
      </div>

      {(showCftButton || showCauButton) && (
        <div className="pt-2 border-t">
          <p className="text-xs text-muted-foreground mb-2">Consulta manual em outros conselhos</p>
          <div className="flex gap-2">
            {showCftButton && (
              <Button variant="outline" size="sm" className="gap-1.5" asChild>
                <a href="https://corporativo.sinceti.net.br/sight/externo.php?form=PesquisarProfissionalEmpresa" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-3.5 w-3.5" /> CFT/CRT
                </a>
              </Button>
            )}
            {showCauButton && (
              <Button variant="outline" size="sm" className="gap-1.5" asChild>
                <a href="https://acheumarquiteto.caubr.gov.br/" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-3.5 w-3.5" /> CAU
                </a>
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
