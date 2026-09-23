interface BarChartItem {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  items: BarChartItem[];
  /** Optional explicit max (otherwise computed from items). */
  maxValue?: number;
  /** Show value at the end of each bar. */
  showValue?: boolean;
  /** Optional unit suffix, e.g. " days". */
  unit?: string;
}

export function BarChart({
  items,
  maxValue,
  showValue = true,
  unit = "",
}: BarChartProps) {
  const computedMax = Math.max(...items.map((i) => i.value), 1);
  const max = maxValue ?? computedMax;

  return (
    <div className="space-y-2">
      {items.map((item) => {
        const percent = max > 0 ? (item.value / max) * 100 : 0;
        return (
          <div key={item.label} className="space-y-1">
            <div className="flex items-baseline justify-between gap-2 text-sm">
              <span className="font-medium truncate">{item.label}</span>
              {showValue && (
                <span className="text-muted-foreground tabular-nums">
                  {item.value}
                  {unit}
                </span>
              )}
            </div>
            <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${percent}%`,
                  backgroundColor: item.color ?? "hsl(var(--primary))",
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
