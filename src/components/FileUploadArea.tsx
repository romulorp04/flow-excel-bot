import { useCallback, useState } from "react";
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface FileUploadAreaProps {
  onFileLoaded: (content: string, fileName: string) => void;
  isLoaded: boolean;
  fileName?: string;
  error?: string;
}

export function FileUploadArea({ onFileLoaded, isLoaded, fileName, error }: FileUploadAreaProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = useCallback(
    (file: File) => {
      if (!file.name.endsWith(".xls") && !file.name.endsWith(".html")) {
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        onFileLoaded(content, file.name);
      };
      reader.readAsText(file, "utf-8");
    },
    [onFileLoaded]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div className="space-y-2">
      <label
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`relative flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 cursor-pointer transition-all duration-200 ${
          isDragging
            ? "border-accent bg-accent/5"
            : isLoaded
            ? "border-success/50 bg-success/5"
            : error
            ? "border-destructive/50 bg-destructive/5"
            : "border-border hover:border-primary/40 hover:bg-muted/50"
        }`}
      >
        <input
          type="file"
          accept=".xls,.html"
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <AnimatePresence mode="wait">
          {isLoaded ? (
            <motion.div key="loaded" initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex flex-col items-center gap-2">
              <CheckCircle2 className="h-10 w-10 text-success" />
              <div className="text-center">
                <p className="font-semibold text-foreground">Arquivo carregado com sucesso</p>
                <p className="text-sm text-muted-foreground flex items-center gap-1.5 mt-1">
                  <FileSpreadsheet className="h-4 w-4" /> {fileName}
                </p>
              </div>
            </motion.div>
          ) : error ? (
            <motion.div key="error" initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex flex-col items-center gap-2">
              <AlertCircle className="h-10 w-10 text-destructive" />
              <p className="text-sm text-destructive font-medium">{error}</p>
            </motion.div>
          ) : (
            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center gap-2">
              <Upload className="h-10 w-10 text-muted-foreground" />
              <div className="text-center">
                <p className="font-medium text-foreground">Arraste o arquivo ou clique para selecionar</p>
                <p className="text-sm text-muted-foreground mt-1">Arquivo .xls exportado do sistema (formato HTML)</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </label>
      {isLoaded && (
        <p className="text-xs text-muted-foreground text-center">Clique ou arraste para substituir o arquivo</p>
      )}
    </div>
  );
}
