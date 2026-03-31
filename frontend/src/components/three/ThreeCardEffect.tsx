"use client"

import { useRef, useState, type ReactNode } from "react"
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion"

interface ThreeCardEffectProps {
  children: ReactNode
  className?: string
  intensity?: number
  glowColor?: string
  onClick?: () => void
}

export function ThreeCardEffect({
  children,
  className = "",
  intensity = 15,
  glowColor = "hsl(var(--primary))",
  onClick,
}: ThreeCardEffectProps) {
  const ref = useRef<HTMLDivElement>(null!)
  const [isHovered, setIsHovered] = useState(false)

  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const mouseXSpring = useSpring(x, { stiffness: 300, damping: 30 })
  const mouseYSpring = useSpring(y, { stiffness: 300, damping: 30 })

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], [`${intensity}deg`, `-${intensity}deg`])
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], [`-${intensity}deg`, `${intensity}deg`])

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const width = rect.width
    const height = rect.height
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top
    const xPct = mouseX / width - 0.5
    const yPct = mouseY / height - 0.5
    x.set(xPct)
    y.set(yPct)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
    setIsHovered(false)
  }

  return (
    <motion.div
      ref={ref}
      style={{
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      className={`relative transition-shadow duration-300 ${
        isHovered ? "shadow-2xl" : "shadow-lg"
      } ${className}`}
    >
      <div
        style={{ transform: "translateZ(40px)" }}
        className="relative"
      >
        {children}
      </div>
      {isHovered && (
        <div
          className="absolute inset-0 rounded-2xl pointer-events-none transition-opacity duration-300"
          style={{
            background: `radial-gradient(600px circle at ${
              (x.get() + 0.5) * 100
            }% ${(y.get() + 0.5) * 100}%, ${glowColor}15, transparent 40%)`,
          }}
        />
      )}
    </motion.div>
  )
}
