import { useState } from "react";
import {
  Download,
  FileText,
  FlaskConical,
  Microscope,
  Plus,
  Scan,
  Trash2,
  type LucideIcon,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DocumentUploadDialog } from "@/features/documents/components/DocumentUploadDialog";
import { useDeleteDocument, useDocuments } from "@/features/documents/hooks";
import type { CaseDocument, DocumentType } from "@/features/documents/types";

interface DocumentsSectionProps {
  caseId: number;
  organizationId: number;
}

const TYPE_META: Record<DocumentType, { label: string; icon: LucideIcon }> = {
  conclusion: { label: "Conclusion", icon: FileText },
  scan: { label: "Scan", icon: Scan },
  analysis: { label: "Analysis", icon: FlaskConical },
  histology: { label: "Histology", icon: Microscope },
  other: { label: "Other", icon: FileText },
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatBytes(bytes: number | null): string {
  if (bytes === null) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

const TYPE_FILTER_OPTIONS: { value: DocumentType | ""; label: string }[] = [
  { value: "", label: "All types" },
  { value: "conclusion", label: "Conclusions" },
  { value: "scan", label: "Scans" },
  { value: "analysis", label: "Analyses" },
  { value: "histology", label: "Histology" },
  { value: "other", label: "Other" },
];

export function DocumentsSection({
  caseId,
  organizationId,
}: DocumentsSectionProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [typeFilter, setTypeFilter] = useState<DocumentType | "">("");
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const { data, isLoading, isError, error } = useDocuments({
    case: caseId,
    page_size: 100,
    type: typeFilter || undefined,
  });

  const deleteDocument = useDeleteDocument();

  async function handleDelete(doc: CaseDocument) {
    const confirmed = window.confirm(
      `Delete "${doc.title || doc.original_filename}"? This cannot be undone.`,
    );
    if (!confirmed) return;

    setDeletingId(doc.id);
    try {
      await deleteDocument.mutateAsync(doc.id);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Documents
        </CardTitle>
        <div className="flex items-center gap-2">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as DocumentType | "")}
            className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          >
            {TYPE_FILTER_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <Button size="sm" onClick={() => setDialogOpen(true)}>
            <Plus className="mr-1 h-3 w-3" />
            Upload
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {isLoading && (
          <div className="p-6 text-center text-muted-foreground">
            Loading documents…
          </div>
        )}

        {isError && (
          <div className="p-6 text-center text-destructive">
            Error: {error instanceof Error ? error.message : "Unknown error"}
          </div>
        )}

        {data && data.results.length === 0 && (
          <div className="p-6 text-center text-muted-foreground">
            {typeFilter
              ? "No documents of this type."
              : "No documents yet. Upload the first one."}
          </div>
        )}

        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>File</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Uploaded</TableHead>
                <TableHead className="w-24"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((doc) => {
                const meta = TYPE_META[doc.type];
                const Icon = meta.icon;
                return (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">
                      <span className="inline-flex items-center gap-2">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                        {meta.label}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm">
                      {doc.title || "—"}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      <a
                        href={doc.file_url ?? "#"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline"
                      >
                        {doc.original_filename}
                      </a>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatBytes(doc.file_size)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(doc.uploaded_at)}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <a
                          href={`/api/documents/${doc.id}/download/`}
                          title="Download"
                          className="inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
                        >
                          <Download className="h-4 w-4" />
                        </a>
                        <button
                          type="button"
                          title="Delete"
                          onClick={() => handleDelete(doc)}
                          disabled={deletingId === doc.id}
                          className="inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <DocumentUploadDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        caseId={caseId}
        organizationId={organizationId}
      />
    </Card>
  );
}
