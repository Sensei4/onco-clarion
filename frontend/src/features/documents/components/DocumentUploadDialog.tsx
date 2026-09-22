import { useEffect, useRef, useState, type FormEvent } from "react";
import { Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useUploadDocument } from "@/features/documents/hooks";
import type {
  DocumentType,
  UploadDocumentPayload,
} from "@/features/documents/types";
import { ApiRequestError } from "@/lib/api";

interface DocumentUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  caseId: number;
  organizationId: number;
  /** Optional referral to link the document to. */
  referralId?: number | null;
  onSuccess?: () => void;
}

const TYPE_OPTIONS: { value: DocumentType; label: string }[] = [
  { value: "conclusion", label: "Conclusion" },
  { value: "scan", label: "Scan" },
  { value: "analysis", label: "Analysis" },
  { value: "histology", label: "Histology" },
  { value: "other", label: "Other" },
];

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function DocumentUploadDialog({
  open,
  onOpenChange,
  caseId,
  organizationId,
  referralId,
  onSuccess,
}: DocumentUploadDialogProps) {
  const uploadDocument = useUploadDocument();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [type, setType] = useState<DocumentType>("other");
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setType("other");
      setTitle("");
      setFile(null);
      setError(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }, [open]);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    setFile(selected);
    // Auto-fill title from filename if empty
    if (selected && !title) {
      const base = selected.name.replace(/\.[^.]+$/, "");
      setTitle(base);
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError("Please select a file.");
      return;
    }

    const payload: UploadDocumentPayload = {
      case: caseId,
      organization: organizationId,
      type,
      title: title.trim(),
      referral: referralId ?? null,
      file,
    };

    try {
      await uploadDocument.mutateAsync(payload);
      onOpenChange(false);
      onSuccess?.();
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }
  }

  const selectClass =
    "w-full h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Upload document</DialogTitle>
            <DialogDescription>
              Attach a file to this cancer case.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="doc_file">File</Label>
              <input
                id="doc_file"
                ref={fileInputRef}
                type="file"
                onChange={handleFileChange}
                className="w-full text-sm file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-primary-foreground hover:file:bg-primary/90"
                required
              />
              {file && (
                <p className="text-xs text-muted-foreground">
                  {file.name} · {formatBytes(file.size)}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="doc_type">Type</Label>
              <select
                id="doc_type"
                value={type}
                onChange={(e) => setType(e.target.value as DocumentType)}
                className={selectClass}
              >
                {TYPE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="doc_title">Title</Label>
              <Input
                id="doc_title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. CT chest report"
              />
            </div>

            {error && (
              <p className="text-destructive text-sm" role="alert">
                {error}
              </p>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={uploadDocument.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={uploadDocument.isPending || !file}>
              {uploadDocument.isPending ? (
                "Uploading…"
              ) : (
                <>
                  <Upload className="mr-1 h-3 w-3" />
                  Upload
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
