"use client"

import { useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { ChevronDown, FileSearch } from "lucide-react"
import { ClaimDetailsCard } from "@/components/ClaimDetailsCard"
import { ClaimRiskBadge } from "@/components/ClaimRiskBadge"
import { useLanguage } from "@/contexts/language-context"
import { cn } from "@/lib/utils"
import type { Claim } from "@/types/api"

function truncate(text: string, max = 90) {
  if (text.length <= max) return text
  return `${text.slice(0, max).trimEnd()}…`
}

/**
 * Responsive list of extracted claims (keeps the given order).
 * Clicking a row expands the full ClaimDetailsCard. Presentational only.
 */
export function ClaimsTable({ claims }: { claims: Claim[] }) {
  const { t } = useLanguage()
  const c = t.claims
  const [expandedId, setExpandedId] = useState<string | null>(null)

  if (claims.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border/60 py-8 text-center">
        <FileSearch className="mx-auto mb-3 h-10 w-10 text-muted-foreground/50" />
        <p className="text-sm text-muted-foreground">{c.empty}</p>
      </div>
    )
  }

  const toggle = (id: string) =>
    setExpandedId((prev) => (prev === id ? null : id))

  return (
    <div className="space-y-2">
      {/* Header row (desktop) */}
      <div className="hidden grid-cols-[minmax(0,1fr)_auto_auto_auto_auto] items-center gap-3 px-3 pb-1 text-[10px] font-bold uppercase tracking-widest text-muted-foreground sm:grid">
        <span>{c.claimText}</span>
        <span>{c.type}</span>
        <span>{c.riskLevel}</span>
        <span>{c.checkworthiness}</span>
        <span className="sr-only">{c.checkable}</span>
      </div>

      {claims.map((claim, index) => {
        const isExpanded = expandedId === claim.id
        const percent = Math.round((claim.checkworthiness_score ?? 0) * 100)
        const typeLabel = c.typeLabels[claim.claim_type] ?? claim.claim_type

        return (
          <motion.div
            key={claim.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(index * 0.03, 0.3) }}
            className="overflow-hidden rounded-2xl border border-border/60 bg-background/80"
          >
            <button
              type="button"
              onClick={() => toggle(claim.id)}
              aria-expanded={isExpanded}
              className="grid w-full grid-cols-[minmax(0,1fr)_auto] items-center gap-3 p-3 text-left transition-colors hover:bg-muted/35 sm:grid-cols-[minmax(0,1fr)_auto_auto_auto_auto]"
            >
              {/* Claim text */}
              <div className="flex min-w-0 items-center gap-2">
                <ChevronDown
                  className={cn(
                    "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
                    isExpanded && "rotate-180",
                  )}
                />
                <span className="truncate text-sm font-medium">
                  {truncate(claim.raw_text)}
                </span>
              </div>

              {/* Type */}
              <span className="hidden whitespace-nowrap rounded-full border border-border/60 bg-muted/30 px-2.5 py-0.5 text-xs text-muted-foreground sm:inline-block">
                {typeLabel}
              </span>

              {/* Risk */}
              <span className="hidden sm:inline-flex">
                <ClaimRiskBadge risk={claim.risk_level} />
              </span>

              {/* Checkworthiness */}
              <span className="hidden items-center gap-2 sm:inline-flex">
                <span className="h-1.5 w-14 overflow-hidden rounded-full bg-muted">
                  <span
                    className="block h-full rounded-full bg-gradient-to-r from-sky-500 to-indigo-500"
                    style={{ width: `${percent}%` }}
                  />
                </span>
                <span className="w-9 text-right font-mono text-xs font-bold tabular-nums">
                  {percent}%
                </span>
              </span>

              {/* Checkable */}
              <span
                className={cn(
                  "hidden h-2 w-2 justify-self-center rounded-full sm:block",
                  claim.is_checkable ? "bg-emerald-500" : "bg-muted-foreground/40",
                )}
                title={claim.is_checkable ? c.yes : c.no}
              />

              {/* Mobile compact meta */}
              <span className="flex items-center gap-2 justify-self-end sm:hidden">
                <ClaimRiskBadge risk={claim.risk_level} />
                <span className="font-mono text-xs font-bold tabular-nums">
                  {percent}%
                </span>
              </span>
            </button>

            <AnimatePresence initial={false}>
              {isExpanded && (
                <motion.div
                  key="details"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.25 }}
                  className="border-t border-border/50 p-3"
                >
                  <ClaimDetailsCard claim={claim} />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )
      })}
    </div>
  )
}
