"use client"

import type { ReactNode } from "react"
import { motion, useReducedMotion } from "framer-motion"
import { cn } from "@/lib/utils"

export function SectionReveal({
  children,
  className,
  delay = 0,
}: {
  children: ReactNode
  className?: string
  delay?: number
}) {
  const reduceMotion = useReducedMotion()

  return (
    <motion.div
      className={cn(className)}
      initial={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 18 }}
      whileInView={reduceMotion ? { opacity: 1 } : { opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={
        reduceMotion
          ? { duration: 0.2, delay }
          : { duration: 0.45, delay, ease: [0.22, 1, 0.36, 1] }
      }
    >
      {children}
    </motion.div>
  )
}
