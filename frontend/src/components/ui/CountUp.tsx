"use client"

import { useEffect, useRef } from "react"
import { animate, useInView, useMotionValue, useReducedMotion } from "framer-motion"

interface CountUpProps {
  end: number
  start?: number
  decimals?: number
  duration?: number
  delay?: number
}

export function CountUp({
  end,
  start = 0,
  decimals = 0,
  duration = 2,
  delay = 0,
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null)
  const motionValue = useMotionValue(start)
  const isInView = useInView(ref, { once: true, margin: "-100px" })
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    if (!isInView) return

    if (reduceMotion) {
      motionValue.set(end)
      return
    }

    const timeout = window.setTimeout(() => {
      const controls = animate(motionValue, end, {
        duration,
        ease: [0.22, 1, 0.36, 1],
      })
      return () => controls.stop()
    }, delay * 1000)

    return () => window.clearTimeout(timeout)
  }, [isInView, end, delay, duration, motionValue, reduceMotion])

  useEffect(() => {
    const unsubscribe = motionValue.on("change", (latest) => {
      if (!ref.current) return
      ref.current.textContent = latest.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })
    })

    return () => unsubscribe()
  }, [decimals, motionValue])

  return <span ref={ref}>{start}</span>
}
