"use client"

import { motion } from "framer-motion"
import {
  Clock,
  FileText,
  Layers,
  ScanSearch,
  ShieldAlert,
  Sparkles,
  Tag,
} from "lucide-react"
import { ClaimRiskBadge } from "@/components/ClaimRiskBadge"
import { useLanguage } from "@/contexts/language-context"
import type { Claim, CheckworthinessBucket } from "@/types/api"

function formatTime(seconds: number) {
  const safe = Math.max(0, Math.floor(seconds))
  const mins = Math.floor(safe / 60)
  const secs = safe % 60
  return `${mins}:${secs.toString().padStart(2, "0")}`
}

const BUCKET_COLOR: Record<CheckworthinessBucket, string> = {
  almost_none: "bg-muted-foreground/30",
  low: "bg-gradient-to-r from-amber-500 to-amber-400",
  desirable: "bg-gradient-to-r from-sky-500 to-indigo-500",
  required: "bg-gradient-to-r from-emerald-500 to-emerald-400",
}

/**
 * Expanded, presentational details for a single extracted claim.
 * Self-contained: no data fetching, all strings localized via useLanguage().
 */
export function ClaimDetailsCard({ claim }: { claim: Claim }) {
  const { t } = useLanguage()
  const c = t.claims

  const percent = Math.round((claim.checkworthiness_score ?? 0) * 100)
  const bucketLabel = c.buckets[claim.checkworthiness_bucket] ?? claim.checkworthiness_bucket
  const typeLabel = c.typeLabels[claim.claim_type] ?? claim.claim_type
  const modalityLabel = c.modalityLabels[claim.source_modality] ?? claim.source_modality
  const hasTimestamps =
    claim.timestamp_start !== null && claim.timestamp_start !== undefined

  return (
    <motion.div
      className="rounded-2xl border border-border/60 bg-muted/20 p-4 space-y-4"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
    >
      {/* Header: type + risk */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-border/60 bg-background/70 px-2.5 py-0.5 text-xs font-medium text-muted-foreground">
          <Layers className="h-3 w-3" />
          {typeLabel}
        </span>
        <ClaimRiskBadge risk={claim.risk_level} />
        {claim.brand && (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
            <Tag className="h-3 w-3" />
            {claim.brand}
          </span>
        )}
      </div>

      {/* Raw text */}
      <div className="space-y-1">
        <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
          <FileText className="h-3 w-3" />
          {c.rawText}
        </p>
        <p className="text-sm leading-relaxed text-foreground">{claim.raw_text}</p>
      </div>

      {/* Normalized claim */}
      {claim.normalized_claim && (
        <div className="space-y-1">
          <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
            <Sparkles className="h-3 w-3" />
            {c.normalized}
          </p>
          <p className="text-sm leading-relaxed text-muted-foreground">
            {claim.normalized_claim}
          </p>
        </div>
      )}

      {/* Checkworthiness bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
            {c.checkworthiness}
          </span>
          <span className="font-mono text-xs font-bold">
            {percent}% · {bucketLabel}
          </span>
        </div>
        <div className="relative h-2 overflow-hidden rounded-full border border-border/10 bg-muted">
          <motion.div
            className={`h-full rounded-full ${BUCKET_COLOR[claim.checkworthiness_bucket] ?? BUCKET_COLOR.low}`}
            initial={{ width: 0 }}
            animate={{ width: `${percent}%` }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Meta grid */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <ScanSearch className="h-3.5 w-3.5 shrink-0" />
          <span className="font-medium text-foreground/80">{c.source}:</span>
          <span>{modalityLabel}</span>
        </div>
        {hasTimestamps && (
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <Clock className="h-3.5 w-3.5 shrink-0" />
            <span className="font-medium text-foreground/80">{c.timestamp}:</span>
            <span className="tabular-nums">
              {formatTime(claim.timestamp_start as number)}
              {claim.timestamp_end !== null && claim.timestamp_end !== undefined
                ? `–${formatTime(claim.timestamp_end)}`
                : ""}
            </span>
          </div>
        )}
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <ShieldAlert className="h-3.5 w-3.5 shrink-0" />
          <span className="font-medium text-foreground/80">{c.checkable}:</span>
          <span>{claim.is_checkable ? c.yes : c.no}</span>
        </div>
        {claim.evidence_needed && (
          <div className="flex items-center gap-1.5 text-amber-600">
            <ShieldAlert className="h-3.5 w-3.5 shrink-0" />
            <span className="font-medium">{c.evidenceNeeded}</span>
          </div>
        )}
      </div>
    </motion.div>
  )
}
