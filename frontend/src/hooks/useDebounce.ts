import { useEffect, useState } from "react";

/**
 * Returns a debounced value that only updates after `delay` ms
 * have passed without further changes.
 *
 * Used for search inputs to avoid firing a request on every keystroke.
 */
export function useDebounce<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
