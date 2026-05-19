"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export function SearchForm() {
  const [query, setQuery] = useState("");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const trimmedQuery = query.trim();
  const canSearch = trimmedQuery.length > 0;
  const isSearchEnabled = canSearch && !isPending;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSearch) return;

    startTransition(() => {
      router.push(`/search?q=${encodeURIComponent(trimmedQuery)}`);
    });
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      onSubmit={handleSearch}
      className="relative w-full max-w-2xl mx-auto shadow-2xl rounded-2xl sm:rounded-full bg-card ring-1 ring-border border border-border/50"
    >
      {/* Mobile: stacked layout; sm+: single row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:h-16 sm:rounded-full overflow-hidden focus-within:ring-2 focus-within:ring-primary transition-all">
        <div className="flex items-center flex-1 min-w-0">
          <div className="pl-4 pr-2 sm:pl-6 sm:pr-4 flex items-center justify-center text-muted-foreground shrink-0 pt-3 sm:pt-0">
            <Search className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search medicines (e.g. Paracetamol)..."
            className="flex-1 min-w-0 h-14 sm:h-full bg-transparent text-base sm:text-lg text-foreground outline-none placeholder:text-muted-foreground/70 pr-4"
          />
        </div>
        <div className="px-2 pb-2 sm:pb-0 sm:pr-2 sm:pl-2">
          <button
            type="submit"
            disabled={!isSearchEnabled}
            aria-label={isPending ? "Searching" : "Compare"}
            className={cn(
              "w-full sm:w-auto h-11 sm:h-12 px-6 rounded-xl sm:rounded-full font-semibold transition-all flex items-center justify-center sm:min-w-[120px]",
              isSearchEnabled
                ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-105 active:scale-95 cursor-pointer shadow-lg shadow-primary/20"
                : "bg-muted text-muted-foreground cursor-not-allowed"
            )}
          >
            {isPending ? (
              <>
                <Loader2 aria-hidden="true" className="w-5 h-5 animate-spin" />
                <span className="sr-only">Searching</span>
              </>
            ) : (
              "Compare"
            )}
          </button>
        </div>
      </div>
    </motion.form>
  );
}
