"use client"

import { Badge } from "@/components/ui/Badge"
import { useLanguage } from "@/contexts/language-context"
import { cn } from "@/lib/utils"
import type { RiskLevel } from "@/types/api"

/**
 * Localized, color-coded badge for a claim's risk level.
 * low -> success/emerald, medium -> warning/amber, high -> destructive/red,
 * critical -> a stronger red-700 emphasis.
 */
export function ClaimRiskBadge({
  risk,
  className,
}: {
  risk: RiskLevel
  className?: string
}) {
  const { t } = useLanguage()
  const c = t.claims

  const config: Record<
    RiskLevel,
    { variant: "success" | "warning" | "destructive"; label: string; className?: string }
  > = {
    low: { variant: "success", label: c.riskLow },
    medium: { variant: "warning", label: c.riskMedium },
    high: { variant: "destructive", label: c.riskHigh },
    critical: {
      variant: "destructive",
      label: c.riskCritical,
      className: "bg-red-700/15 text-red-700 border border-red-700/30 font-semibold",
    },
  }

  const { variant, label, className: riskClassName } = config[risk]

  return (
    <Badge variant={variant} className={cn(riskClassName, className)}>
      {label}
    </Badge>
  )
}
