"use client"

import { motion } from "framer-motion"
import { AudioLines, Check, CloudDownload, Eye, FileText, Loader2, type LucideIcon } from "lucide-react"
import { useMemo } from "react"
import { useLanguage } from "@/contexts/language-context"

interface Step {
  key: "download" | "visual" | "audio" | "report"
  label: string
  hint: string
  start: number
  end: number
  icon: LucideIcon
}

/**
 * Steps are driven by the progress value (which is monotonic and reliable),
 * not by the backend `stage` string — the backend reuses stage="analyze" at
 * several different progress points, so keying off it made steps light up out
 * of order. Thresholds mirror the real pipeline in video_analysis.py:
 *   0–20  download, 20–64 video+brands, 64–94 audio+disclosure, 94–100 report.
 */
export function ProgressBar({
  value,
  label,
  showPercentage = true,
}: {
  value: number
  label?: string
  stage?: string
  showPercentage?: boolean
}) {
  const { t } = useLanguage()
  const a = t.analyze
  const clamped = Math.min(100, Math.max(0, value))

  const steps: Step[] = useMemo(
    () => [
      { key: "download", label: a.steps.download, hint: a.stepHintDownload, start: 0, end: 20, icon: CloudDownload },
      { key: "visual", label: a.steps.visual, hint: a.stepHintVisual, start: 20, end: 64, icon: Eye },
      { key: "audio", label: a.steps.audio, hint: a.stepHintAudio, start: 64, end: 94, icon: AudioLines },
      { key: "report", label: a.steps.report, hint: a.stepHintReport, start: 94, end: 100, icon: FileText },
    ],
    [a],
  )

  const activeIndex = useMemo(() => {
    if (clamped >= 100) return steps.length - 1
    const idx = steps.findIndex((s) => clamped >= s.start && clamped < s.end)
    return idx === -1 ? 0 : idx
  }, [clamped, steps])

  const isComplete = clamped >= 100
  const activeStep = steps[activeIndex]

  return (
    <div className="space-y-4">
      {/* Stepper */}
      <div className="relative">
        {/* connector track */}
        <div className="absolute left-0 right-0 top-5 mx-[12.5%] h-0.5 bg-border/70" aria-hidden />
        <motion.div
          className="absolute left-0 top-5 mx-[12.5%] h-0.5 bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400"
          aria-hidden
          initial={{ width: 0 }}
          animate={{ width: `${(clamped / 100) * 75}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
        <div className="relative grid grid-cols-4">
          {steps.map((step, idx) => {
            const Icon = step.icon
            const done = isComplete || idx < activeIndex || clamped >= step.end
            const active = !done && idx === activeIndex
            return (
              <div key={step.key} className="flex flex-col items-center gap-2 text-center">
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors duration-300 ${
                    done
                      ? "border-emerald-500 bg-emerald-500 text-white"
                      : active
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border bg-muted/40 text-muted-foreground"
                  }`}
                >
                  {done ? (
                    <Check className="h-5 w-5" />
                  ) : active ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <div className="space-y-0.5">
                  <p
                    className={`text-[11px] font-semibold leading-tight ${
                      done ? "text-emerald-600" : active ? "text-foreground" : "text-muted-foreground"
                    }`}
                  >
                    {step.label}
                  </p>
                  <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground/70">
                    {done ? a.stepDone : active ? `${clamped}%` : a.stepWaiting}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Overall bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-3 text-xs">
          <p className="truncate font-medium text-foreground">{label || activeStep.hint}</p>
          {showPercentage && <span className="shrink-0 font-mono font-semibold tabular-nums">{clamped}%</span>}
        </div>
        <div className="relative h-2.5 w-full overflow-hidden rounded-full border border-border/50 bg-muted/80 shadow-inner">
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400"
            initial={{ width: 0 }}
            animate={{ width: `${clamped}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
        {!isComplete && <p className="text-[11px] leading-snug text-muted-foreground/80">{a.etaNote}</p>}
      </div>
    </div>
  )
}
