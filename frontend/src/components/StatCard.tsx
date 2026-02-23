"use client"

import { ReactNode } from "react"
import { motion } from "framer-motion"
import { CountUp } from "./ui/CountUp"

export function StatCard({
  label,
  value,
  icon,
  helper,
  animateValue = true,
}: {
  label: string
  value: string | number
  icon?: ReactNode
  helper?: string
  animateValue?: boolean
}) {
  // Пытаемся извлечь числовое значение для анимации
  const numericValue = typeof value === "number" ? value : parseFloat(value.replace(/[^0-9.]/g, ""))
  const isNumeric = !isNaN(numericValue) && animateValue

  return (
    <motion.div
      className="card card-hover p-5 group"
      whileHover={{ 
        y: -4,
        scale: 1.02,
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Background gradient on hover */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-primary opacity-0 group-hover:opacity-[0.03] transition-opacity duration-500 pointer-events-none" />
      
      <div className="relative">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground font-medium">{label}</p>
          {icon ? (
            <motion.div
              className="text-primary p-2 rounded-lg bg-primary/5 group-hover:bg-primary/10 group-hover:scale-110 transition-all duration-300"
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
      </div>
    </motion.div>
  )
}
