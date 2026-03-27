"use client"

import { useEffect, useRef } from "react"
import { motion, useReducedMotion } from "framer-motion"
import { cn } from "@/lib/utils"

export function PremiumBackdrop({ className }: { className?: string }) {
  const rootRef = useRef<HTMLDivElement>(null)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    if (reduceMotion) return
    const root = rootRef.current
    if (!root) return

    const handleMove = (event: MouseEvent) => {
      const rect = root.getBoundingClientRect()
      const x = ((event.clientX - rect.left) / rect.width) * 100
      const y = ((event.clientY - rect.top) / rect.height) * 100
      root.style.setProperty("--pointer-x", `${x}%`)
      root.style.setProperty("--pointer-y", `${y}%`)
    }

    window.addEventListener("mousemove", handleMove, { passive: true })
    return () => window.removeEventListener("mousemove", handleMove)
  }, [reduceMotion])

  return (
    <div ref={rootRef} className={cn("pointer-events-none fixed inset-0 overflow-hidden", className)}>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,hsl(var(--primary)/0.16),transparent_25%),radial-gradient(circle_at_80%_12%,hsl(191_95%_50%/0.08),transparent_22%),radial-gradient(circle_at_60%_85%,hsl(var(--foreground)/0.04),transparent_30%)]" />
      <div className="absolute inset-0 bg-grid opacity-[0.18] [mask-image:radial-gradient(circle_at_center,black,transparent_74%)]" />
      <motion.div
        className="absolute inset-0 opacity-70"
        animate={
          reduceMotion
            ? undefined
            : {
                x: [0, 18, 0],
                y: [0, -12, 0],
              }
        }
        transition={
          reduceMotion
            ? undefined
            : {
                duration: 18,
                repeat: Number.POSITIVE_INFINITY,
                ease: "easeInOut",
              }
        }
      >
        <div
          className="absolute left-[10%] top-[8%] h-56 w-56 rounded-full bg-sky-400/15 blur-3xl"
          style={{
            transform: reduceMotion ? "none" : "translate3d(0, 0, 0)",
          }}
        />
        <div className="absolute right-[12%] top-[16%] h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute bottom-[10%] left-[42%] h-80 w-80 rounded-full bg-blue-500/10 blur-3xl" />
      </motion.div>
      <div
        className="absolute inset-0 opacity-60"
        style={{
          background:
            "radial-gradient(circle at var(--pointer-x, 50%) var(--pointer-y, 50%), rgba(255,255,255,0.06), transparent 18%)",
        }}
      />
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent,rgba(255,255,255,0.02))]" />
    </div>
  )
}
