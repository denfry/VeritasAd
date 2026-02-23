"use client"

import { useEffect, useRef } from "react"
import { useInView, useMotionValue, useSpring } from "framer-motion"

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
  
  // Плавное значение с spring анимацией
  const springValue = useSpring(motionValue, {
    damping: 25,
    stiffness: 100,
    duration: duration * 1000,
  })
  
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  useEffect(() => {
    if (isInView) {
      const timeout = setTimeout(() => {
        motionValue.set(end)
      }, delay)
      
      return () => clearTimeout(timeout)
    }
  }, [isInView, end, delay, motionValue])

  useEffect(() => {
    const unsubscribe = springValue.on("change", (latest) => {
      if (ref.current) {
        const formatted = latest.toLocaleString(undefined, {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        })
        ref.current.textContent = formatted
      }
    })
    
    return () => unsubscribe()
  }, [springValue, decimals])

  return <span ref={ref}>{start}</span>
}
