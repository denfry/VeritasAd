"use client"

import { type ReactNode } from "react"
import { motion } from "framer-motion"
import { CountUp } from "./ui/CountUp"

export function StatCard({
  label,
  value,
  icon,
  helper,
  animateValue = true,
  progress,
}: {
  label: string
  value: string | number
  icon?: ReactNode
  helper?: string
  animateValue?: boolean
  progress?: number
}) {
  const numericValue = typeof value === "number" ? value : parseFloat(value.replace(/[^0-9.]/g, ""))
  const isNumeric = !Number.isNaN(numericValue) && animateValue

  return (
    <motion.div
      className="card group relative overflow-hidden p-5 transition-all duration-500 hover:-translate-y-1 hover:shadow-[0_8px_40px_rgba(0,0,0,0.2)]"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Background ambient glow effect */}
      <div className="absolute -inset-1 rounded-3xl bg-gradient-to-br from-primary/20 via-transparent to-primary/5 opacity-0 mix-blend-overlay blur-xl transition-opacity duration-700 group-hover:opacity-100" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,hsl(var(--primary)/0.15),transparent_50%)] opacity-0 transition-opacity duration-700 group-hover:opacity-100 pointer-events-none" />

      {/* Subtle grid pattern inside card */}
      <div className="absolute inset-0 bg-grid opacity-[0.03] pointer-events-none mix-blend-overlay" />

      <div className="relative z-10">
        <div className="flex items-center justify-between gap-3">
          <p className="text-[13px] text-muted-foreground/80 font-medium tracking-wide uppercase">{label}</p>
          {icon ? (
            <motion.div
              className="text-primary p-2.5 rounded-[0.8rem] bg-primary/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] border border-primary/20 group-hover:bg-primary/20 group-hover:scale-110 group-hover:shadow-[0_0_20px_hsl(var(--primary)/0.3)] transition-all duration-300"
              whileHover={{ rotate: 5, scale: 1.15 }}
            >
              {icon}
            </motion.div>
          ) : null}
        </div>

        <div className="mt-4 flex items-baseline gap-2">
          {isNumeric ? (
            <motion.p
              className="text-3xl font-bold tracking-tighter text-foreground drop-shadow-sm group-hover:text-primary transition-colors duration-300"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <CountUp end={numericValue} decimals={value.toString().includes(".") ? 2 : 0} />
            </motion.p>
          ) : (
            <motion.p
              className="text-3xl font-bold tracking-tighter text-foreground drop-shadow-sm group-hover:text-primary transition-colors duration-300"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {value}
            </motion.p>
          )}
        </div>

        {helper ? (
          <motion.p
            className="mt-2 text-[11px] text-muted-foreground/70 font-medium tracking-wide"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {helper}
          </motion.p>
        ) : null}

        {progress !== undefined && (
          <div className="mt-4 h-[6px] rounded-full bg-muted/30 shadow-[inset_0_1px_2px_rgba(0,0,0,0.2)] overflow-hidden">
            <motion.div
              className="relative h-full rounded-full bg-gradient-to-r from-cyan-400 via-primary to-blue-500 shadow-[0_0_10px_hsl(var(--primary)/0.5)]"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(progress, 100)}%` }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }} // smooth ease out
            >
              <div className="absolute top-0 right-0 bottom-0 w-8 bg-gradient-to-r from-transparent to-white/30" />
            </motion.div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
