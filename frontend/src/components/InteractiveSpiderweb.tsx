"use client"

import React, { useEffect, useRef } from "react"

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
}

export function InteractiveSpiderweb() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mouseRef = useRef({ x: 0, y: 0, active: false })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animationFrameId: number
    let particles: Particle[] = []
    const particleCount = 80
    const connectionDistance = 150
    const mouseRadius = 150

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      initParticles()
    }

    const initParticles = () => {
      particles = []
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 1.5 + 0.5,
        })
      }
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Get theme-aware color
      const isDark = document.documentElement.classList.contains("dark")
      const color = isDark ? "255, 255, 255" : "71, 85, 105" // slate-600 for light mode
      
      ctx.fillStyle = isDark ? `rgba(${color}, 0.15)` : `rgba(${color}, 0.25)`
      ctx.strokeStyle = isDark ? `rgba(${color}, 0.08)` : `rgba(${color}, 0.15)`
      ctx.lineWidth = 0.5

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i]

        // Move
        p.x += p.vx
        p.y += p.vy

        // Bounce
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1

        // Mouse interaction (repel)
        if (mouseRef.current.active) {
          const dx = p.x - mouseRef.current.x
          const dy = p.y - mouseRef.current.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          
          if (dist < mouseRadius) {
            const force = (mouseRadius - dist) / mouseRadius
            p.x += dx * force * 0.05
            p.y += dy * force * 0.05
          }
        }

        // Draw particle
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()

        // Draw connections
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j]
          const dx = p.x - p2.x
          const dy = p.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < connectionDistance) {
            // "Break" line if mouse is nearby
            let opacity = (1 - dist / connectionDistance) * 0.5
            
            if (mouseRef.current.active) {
              const mdx = (p.x + p2.x) / 2 - mouseRef.current.x
              const mdy = (p.y + p2.y) / 2 - mouseRef.current.y
              const mdist = Math.sqrt(mdx * mdx + mdy * mdy)
              if (mdist < 50) opacity *= 0.1 // Break effect
            }

            ctx.strokeStyle = `rgba(${color}, ${opacity})`
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.stroke()
          }
        }
      }

      animationFrameId = requestAnimationFrame(draw)
    }

    const onMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY, active: true }
    }

    const onMouseLeave = () => {
      mouseRef.current.active = false
    }

    window.addEventListener("resize", resize)
    window.addEventListener("mousemove", onMouseMove)
    window.addEventListener("mouseleave", onMouseLeave)
    
    resize()
    draw()

    return () => {
      window.removeEventListener("resize", resize)
      window.removeEventListener("mousemove", onMouseMove)
      window.removeEventListener("mouseleave", onMouseLeave)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none opacity-60 dark:opacity-40 transition-opacity duration-1000"
      style={{ mixBlendMode: 'normal' }}
    />
  )
}
