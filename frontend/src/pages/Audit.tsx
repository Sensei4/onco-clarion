import { useState } from "react";
import {
  Download,
  Eye,
  FileEdit,
  LogIn,
  LogOut,
  Plus,
  Trash2,
  type LucideIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuditEvents } from "@/features/audit/hooks";
import type {
  AuditAction,
  AuditEvent,
  AuditListParams,
} from "@/features/audit/types";
import { useDebounce } from "@/hooks/useDebounce";

const PAGE_SIZE = 50;

const ACTION_META: Record<
  AuditAction,
  {
    label: string;
    icon: LucideIcon;
    variant: "default" | "secondary" | "destructive" | "outline";
  }
> = {
  view: { label: "View", icon: Eye, variant: "outline" },
  create: { label: "Create", icon: Plus, variant: "default" },
  update: { label: "Update", icon: FileEdit, variant: "secondary" },
  delete: { label: "Delete", icon: Trash2, variant: "destructive" },
  download: { label: "Download", icon: Download, variant: "secondary" },
  login: { label: "Login", icon: LogIn, variant: "outline" },
  logout: { label: "Logout", icon: LogOut, variant: "outline" },
};

const ACTION_FILTER_OPTIONS: { value: AuditAction | ""; label: string }[] = [
  { value: "", label: "All actions" },
  { value: "view", label: "View" },
  { value: "create", label: "Create" },
  { value: "update", label: "Update" },
  { value: "delete", label: "Delete" },
  { value: "download", label: "Download" },
  { value: "login", label: "Login" },
  { value: "logout", label: "Logout" },
];

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function Audit() {
  const [action, setAction] = useState<AuditAction | "">("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const debouncedSearch = useDebounce(search, 300);

  const params: AuditListParams = {
    page,
    page_size: PAGE_SIZE,
    action: action || undefined,
    search: debouncedSearch || undefined,
  };

  const { data, isLoading, isError, error, isFetching } =
    useAuditEvents(params);

  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 0;
  const hasPrev = data?.previous != null;
  const hasNext = data?.next != null;

  function handleActionChange(value: AuditAction | "") {
    setAction(value);
    setPage(1);
  }

  function handleSearchChange(value: string) {
    setSearch(value);
    setPage(1);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Audit log</h1>
        <p className="text-muted-foreground">
          {data
            ? `${data.count} event${data.count === 1 ? "" : "s"}`
            : "Loading…"}
        </p>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <select
          value={action}
          onChange={(e) =>
            handleActionChange(e.target.value as AuditAction | "")
          }
          className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
        >
          {ACTION_FILTER_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <Input
          placeholder="Search by entity, user, IP…"
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Events
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading && (
            <div className="p-8 text-center text-muted-foreground">
              Loading audit events…
            </div>
          )}

          {isError && (
            <div className="p-8 text-center text-destructive">
              Error: {error instanceof Error ? error.message : "Unknown error"}
            </div>
          )}

          {data && data.results.length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              No audit events found.
            </div>
          )}

          {data && data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Entity</TableHead>
                  <TableHead>IP</TableHead>
                  <TableHead>Request</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.results.map((e: AuditEvent) => {
                  const meta = ACTION_META[e.action];
                  const Icon = meta.icon;
                  return (
                    <TableRow key={e.id}>
                      <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                        {formatDateTime(e.timestamp)}
                      </TableCell>
                      <TableCell className="text-sm">
                        {e.user_name ?? "—"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={meta.variant}>
                          <Icon className="mr-1 h-3 w-3" />
                          {meta.label}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">
                        <span className="font-medium">{e.entity_type}</span>
                        {e.entity_repr && (
                          <span className="ml-2 text-muted-foreground">
                            {e.entity_repr}
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground font-mono">
                        {e.ip_address ?? "—"}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground font-mono">
                        {e.request_method} {e.request_path}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {data && data.count > 0 && (
        <div className="flex items-center justify-between text-sm">
          <p
            className={
              "text-muted-foreground" + (isFetching ? " opacity-50" : "")
            }
          >
            Page {page} of {totalPages || 1}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={!hasPrev || isFetching}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasNext || isFetching}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
