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
      className="card card-hover p-5 group relative overflow-hidden"
      whileHover={{ y: -4, scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="absolute inset-0 rounded-[1.25rem] bg-gradient-to-br from-primary/8 via-cyan-400/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      <div className="relative">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm text-muted-foreground font-medium">{label}</p>
          {icon ? (
            <motion.div
              className="text-primary p-2 rounded-full bg-primary/10 group-hover:bg-primary/15 group-hover:scale-110 transition-all duration-300"
              whileHover={{ rotate: 5 }}
            >
              {icon}
            </motion.div>
          ) : null}
        </div>

        <div className="mt-3 flex items-baseline gap-2">
          {isNumeric ? (
            <motion.p
              className="text-2xl font-semibold tracking-tight"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <CountUp end={numericValue} decimals={value.toString().includes(".") ? 2 : 0} />
            </motion.p>
          ) : (
            <motion.p
              className="text-2xl font-semibold tracking-tight"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              {value}
            </motion.p>
          )}
        </div>

        {helper ? (
          <motion.p
            className="mt-2 text-xs text-muted-foreground"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {helper}
          </motion.p>
        ) : null}

        {progress !== undefined && (
          <div className="mt-3 h-1.5 rounded-full bg-muted/80 overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(progress, 100)}%` }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />
          </div>
        )}
      </div>
    </motion.div>
  )
}
