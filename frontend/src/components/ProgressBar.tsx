"use client"

import { motion } from "framer-motion"
import { CloudUpload, FileText, SearchCheck, Video } from "lucide-react"
import { useMemo, type ComponentType } from "react"

type StageKey =
  | "upload"
  | "analyze"
  | "brand_detection"
  | "report"
  | "complete"
  | "processing"
  | "idle"
  | "prepare"

interface Stage {
  key: StageKey
  label: string
  minProgress: number
  maxProgress: number
  icon: ComponentType<{ className?: string }>
}

const STAGES: Stage[] = [
  { key: "upload", label: "File upload", minProgress: 0, maxProgress: 20, icon: CloudUpload },
  { key: "analyze", label: "Video analysis", minProgress: 20, maxProgress: 55, icon: Video },
  { key: "brand_detection", label: "Brand recognition", minProgress: 55, maxProgress: 85, icon: SearchCheck },
  { key: "report", label: "Report generation", minProgress: 85, maxProgress: 100, icon: FileText },
]

function stageIndexFromProgress(progress: number): number {
  if (progress >= 100) return STAGES.length - 1
  return Math.max(
    0,
    STAGES.findIndex((stage) => progress >= stage.minProgress && progress < stage.maxProgress),
  )
}

export function ProgressBar({
  value,
  label,
  stage,
  showPercentage = true,
}: {
  value: number
  label?: string
  stage?: string
  showPercentage?: boolean
}) {
  const clampedValue = Math.min(100, Math.max(0, value))

  const currentStageIndex = useMemo(() => {
    const stageKey = (stage ?? "idle") as StageKey
    if (stageKey === "complete") return STAGES.length - 1
    const byKey = STAGES.findIndex((s) => s.key === stageKey)
    if (byKey >= 0) return byKey
    return stageIndexFromProgress(clampedValue)
  }, [clampedValue, stage])

  const currentStage = STAGES[currentStageIndex]
  const currentStageProgress = useMemo(() => {
    const range = currentStage.maxProgress - currentStage.minProgress || 1
    const local = clampedValue - currentStage.minProgress
    return Math.max(0, Math.min(100, (local / range) * 100))
  }, [clampedValue, currentStage])

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {STAGES.map((stageItem, idx) => {
          const Icon = stageItem.icon
          const isActive = idx === currentStageIndex && clampedValue < 100
          const isComplete = clampedValue >= stageItem.maxProgress || clampedValue >= 100
          return (
            <div
              key={stageItem.key}
              className={`rounded-lg border px-2 py-1.5 text-[11px] transition-all ${
                isActive
                  ? "border-primary/50 bg-primary/10"
                  : isComplete
                    ? "border-emerald-500/30 bg-emerald-500/10"
                    : "border-border/60 bg-muted/30"
              }`}
            >
              <div className="flex items-center gap-1.5">
                <Icon className={`h-3.5 w-3.5 ${isActive ? "text-primary" : isComplete ? "text-emerald-500" : "text-muted-foreground"}`} />
                <span className="truncate text-muted-foreground">{stageItem.label}</span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex items-center justify-between text-xs">
        <p className="text-sm font-medium text-foreground">{label || currentStage.label}</p>
        {showPercentage && <span className="text-xs font-semibold tabular-nums">{clampedValue}%</span>}
      </div>

      <div className="relative h-3 w-full overflow-hidden rounded-[10px] bg-muted/80 border border-border/50 shadow-inner">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-[10px] bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400"
          initial={{ width: 0 }}
          animate={{ width: `${clampedValue}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{currentStage.label}</span>
        <span className="tabular-nums">{currentStageProgress.toFixed(0)}% of stage</span>
      </div>
    </div>
  )
}
