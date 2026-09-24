import { useEffect, useMemo, useRef, useState } from "react";
import { Loader2, Search as SearchIcon, X } from "lucide-react";

import { Input } from "@/components/ui/input";
import { useIcd11Search } from "@/features/dictionaries/hooks";
import type { MmsEntity } from "@/features/dictionaries/types";
import { useDebounce } from "@/hooks/useDebounce";
import { cn } from "@/lib/utils";

export interface Icd11Selection {
  uri: string;
  the_code: string;
  title: string;
}

interface Icd11SearchProps {
  value: Icd11Selection | null;
  onChange: (value: Icd11Selection | null) => void;
  placeholder?: string;
  disabled?: boolean;
  chapter?: string;
}

export function Icd11Search({
  value,
  onChange,
  placeholder = "Search ICD-11 code or name…",
  disabled = false,
  chapter = "02",
}: Icd11SearchProps) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const debouncedQuery = useDebounce(query, 300);

  const searchParams = useMemo(
    () => ({ q: debouncedQuery, chapter, page_size: 20 }),
    [debouncedQuery, chapter],
  );

  const { data, isLoading } = useIcd11Search(
    searchParams,
    !disabled && debouncedQuery.length >= 2,
  );

  // Filter out entities with empty code (parents without a code)
  const results: MmsEntity[] = useMemo(() => {
    const items = data?.results ?? [];
    return items.filter((item) => item.the_code.trim() !== "").slice(0, 10);
  }, [data]);

  // Reset highlight when results change
  useEffect(() => {
    setHighlightedIndex(0);
  }, [debouncedQuery]);

  // Click outside — close dropdown
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [open]);

  function handleSelect(item: MmsEntity) {
    onChange({
      uri: item.uri,
      the_code: item.the_code,
      title: item.title,
    });
    setQuery("");
    setOpen(false);
  }

  function handleClear() {
    onChange(null);
    setQuery("");
    inputRef.current?.focus();
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!open || results.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((i) => (i + 1) % results.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((i) => (i - 1 + results.length) % results.length);
    } else if (e.key === "Enter") {
      e.preventDefault();
      handleSelect(results[highlightedIndex]);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  const showDropdown = open && debouncedQuery.length >= 2;
  const showNoResults = showDropdown && !isLoading && results.length === 0;

  return (
    <div ref={containerRef} className="relative">
      {value ? (
        <div className="flex items-center justify-between gap-2 rounded-md border border-input bg-background px-3 py-2 text-sm">
          <div className="flex items-baseline gap-2 min-w-0">
            <span className="font-mono font-medium shrink-0">
              {value.the_code}
            </span>
            <span className="truncate text-muted-foreground">
              {value.title}
            </span>
          </div>
          <button
            type="button"
            onClick={handleClear}
            disabled={disabled}
            className="shrink-0 rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-foreground disabled:opacity-50"
            aria-label="Clear selection"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <>
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              ref={inputRef}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setOpen(true);
              }}
              onFocus={() => setOpen(true)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              className="pl-9"
              autoComplete="off"
            />
            {isLoading && (
              <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
            )}
          </div>

          {showDropdown && (
            <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
              {results.length > 0 ? (
                <ul className="max-h-64 overflow-y-auto py-1">
                  {results.map((item, index) => (
                    <li key={item.uri}>
                      <button
                        type="button"
                        onClick={() => handleSelect(item)}
                        onMouseEnter={() => setHighlightedIndex(index)}
                        className={cn(
                          "flex w-full items-baseline gap-2 px-3 py-2 text-left text-sm",
                          index === highlightedIndex
                            ? "bg-accent text-accent-foreground"
                            : "hover:bg-accent/50",
                        )}
                      >
                        <span className="font-mono font-medium shrink-0">
                          {item.the_code}
                        </span>
                        <span className="truncate">{item.title}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : showNoResults ? (
                <div className="px-3 py-2 text-sm text-muted-foreground">
                  No results for «{debouncedQuery}».
                </div>
              ) : null}
            </div>
          )}
        </>
      )}
    </div>
  );
}
