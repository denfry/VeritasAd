"use client"

import { useEffect, useRef } from "react"
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion"
import { cn } from "@/lib/utils"

export function PremiumBackdrop({ className }: { className?: string }) {
  const rootRef = useRef<HTMLDivElement>(null)
  const reduceMotion = useReducedMotion()
  const { scrollYProgress } = useScroll()
  const slowOrbit = useTransform(scrollYProgress, [0, 1], [0, -120])
  const fastOrbit = useTransform(scrollYProgress, [0, 1], [0, 180])
  const gridShift = useTransform(scrollYProgress, [0, 1], [0, 80])

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
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_16%_12%,hsl(var(--primary)/0.22),transparent_28%),radial-gradient(circle_at_78%_10%,hsl(182_88%_56%/0.16),transparent_24%),radial-gradient(circle_at_50%_86%,hsl(26_93%_61%/0.1),transparent_30%),linear-gradient(180deg,hsl(var(--background)),hsl(var(--background)))]" />
      <motion.div
        className="absolute inset-0 bg-grid opacity-[0.16] [mask-image:radial-gradient(circle_at_center,black,transparent_74%)]"
        style={{ y: reduceMotion ? 0 : gridShift }}
      />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.08),transparent_42%)] opacity-70" />
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
        <motion.div
          className="absolute left-[8%] top-[6%] h-72 w-72 rounded-full bg-sky-400/14 blur-3xl"
          style={{ y: reduceMotion ? 0 : slowOrbit }}
        />
        <motion.div
          className="absolute right-[8%] top-[14%] h-96 w-96 rounded-full bg-cyan-400/12 blur-3xl"
          style={{ y: reduceMotion ? 0 : fastOrbit }}
        />
        <motion.div
          className="absolute bottom-[2%] left-[35%] h-[28rem] w-[28rem] rounded-full bg-orange-400/10 blur-3xl"
          style={{ y: reduceMotion ? 0 : slowOrbit }}
        />
        <motion.div
          className="absolute left-[22%] top-[28%] h-40 w-40 rounded-full border border-white/10 bg-white/5 blur-2xl"
          style={{ y: reduceMotion ? 0 : fastOrbit }}
        />
      </motion.div>
      <div
        className="absolute inset-0 opacity-60"
        style={{
          background:
            "radial-gradient(circle at var(--pointer-x, 50%) var(--pointer-y, 50%), rgba(255,255,255,0.06), transparent 18%)",
        }}
      />
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent,rgba(255,255,255,0.03))]" />
      <div className="absolute inset-0 opacity-[0.08] [background-image:linear-gradient(120deg,transparent_0%,rgba(255,255,255,0.8)_48%,transparent_52%)] [background-size:240px_240px]" />
    </div>
  )
}
