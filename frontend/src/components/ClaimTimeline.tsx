"use client"

import { useMemo, useState } from "react"
import { motion } from "framer-motion"
import { Clock } from "lucide-react"
import { ClaimRiskBadge } from "@/components/ClaimRiskBadge"
import { useLanguage } from "@/contexts/language-context"
import type { Claim, RiskLevel } from "@/types/api"

// Marker dot color by risk level (matches ClaimRiskBadge semantics).
const RISK_DOT: Record<RiskLevel, string> = {
  low: "bg-emerald-500 border-emerald-600",
  medium: "bg-amber-500 border-amber-600",
  high: "bg-red-500 border-red-600",
  critical: "bg-red-700 border-red-800",
}

function formatTime(seconds: number) {
  const safe = Math.max(0, Math.floor(seconds))
  const mins = Math.floor(safe / 60)
  const secs = safe % 60
  return `${mins}:${secs.toString().padStart(2, "0")}`
}

function hasStart(claim: Claim): claim is Claim & { timestamp_start: number } {
  return claim.timestamp_start !== null && claim.timestamp_start !== undefined
}

/**
 * Horizontal timeline of timed claims, colored by risk level, with a hover
 * tooltip (raw_text + type). Claims without a start timestamp are listed below.
 * Gracefully degrades when duration is missing/0. Presentational only.
 */
export function ClaimTimeline({
  claims,
  duration,
}: {
  claims: Claim[]
  duration?: number
}) {
  const { t } = useLanguage()
  const c = t.claims
  const [hovered, setHovered] = useState<string | null>(null)

  const timed = useMemo(() => claims.filter(hasStart), [claims])
  const untimed = useMemo(() => claims.filter((claim) => !hasStart(claim)), [claims])

  const hasUsableDuration = typeof duration === "number" && duration > 0
  const safeDuration = hasUsableDuration ? (duration as number) : 1

  if (claims.length === 0) {
    return (
      <p className="py-3 text-center text-sm text-muted-foreground">{c.empty}</p>
    )
  }

  return (
    <div className="space-y-4">
      {/* Timeline (only when we have a duration and timed claims) */}
      {hasUsableDuration && timed.length > 0 ? (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{formatTime(0)}</span>
            <span>{formatTime(safeDuration)}</span>
          </div>
          <motion.div
            className="relative h-6 overflow-visible rounded-full border border-border/50 bg-muted shadow-inner"
            initial={{ opacity: 0, scaleY: 0.5 }}
            animate={{ opacity: 1, scaleY: 1 }}
            transition={{ duration: 0.4 }}
          >
            {[0, 25, 50, 75, 100].map((pos) => (
              <div
                key={pos}
                className="absolute top-0 bottom-0 w-px bg-border/50"
                style={{ left: `${pos}%` }}
              />
            ))}

            {timed.map((claim, index) => {
              const left = Math.min(
                95,
                Math.max(5, (claim.timestamp_start / safeDuration) * 100),
              )
              return (
                <motion.div
                  key={claim.id}
                  className={`absolute -top-1 h-8 w-2.5 cursor-pointer rounded-full border shadow-md transition-shadow hover:shadow-lg ${RISK_DOT[claim.risk_level]}`}
                  style={{ left: `${left}%`, transform: "translateX(-50%)" }}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2 + index * 0.03, duration: 0.2 }}
                  whileHover={{ scale: 1.4, zIndex: 10 }}
                  onMouseEnter={() => setHovered(claim.id)}
                  onMouseLeave={() => setHovered(null)}
                >
                  <motion.div
                    className="absolute -top-2 left-1/2 z-20 min-w-[160px] max-w-[240px] -translate-x-1/2 -translate-y-full rounded-lg bg-foreground px-3 py-2 text-xs text-background shadow-lg"
                    animate={{
                      opacity: hovered === claim.id ? 1 : 0,
                      y: hovered === claim.id ? -4 : 0,
                    }}
                    transition={{ duration: 0.2 }}
                    style={{ pointerEvents: "none" }}
                  >
                    <div className="font-semibold leading-snug">{claim.raw_text}</div>
                    <div className="mt-1 text-[10px] text-background/70">
                      {c.typeLabels[claim.claim_type] ?? claim.claim_type} ·{" "}
                      {formatTime(claim.timestamp_start)}
                    </div>
                  </motion.div>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      ) : timed.length > 0 ? (
        // Have timed claims but no usable duration: explain instead of a broken bar.
        <p className="py-2 text-center text-sm text-muted-foreground">
          {c.noDuration}
        </p>
      ) : null}

      {/* Untimed claims list */}
      {untimed.length > 0 && (
        <div className="space-y-2">
          <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
            <Clock className="h-3 w-3" />
            {c.untimed}
          </p>
          <div className="space-y-1.5">
            {untimed.map((claim, index) => (
              <motion.div
                key={claim.id}
                className="flex items-center gap-2 rounded-xl border border-border/50 bg-muted/20 p-2.5"
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: Math.min(index * 0.03, 0.3) }}
              >
                <ClaimRiskBadge risk={claim.risk_level} />
                <span className="min-w-0 flex-1 truncate text-xs text-muted-foreground">
                  {claim.raw_text}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
