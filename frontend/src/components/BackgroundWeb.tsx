'use client'

import { useEffect, useRef, useCallback } from 'react'

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
}

interface MousePosition {
  x: number
  y: number
}

export function BackgroundWeb() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const mouseRef = useRef<MousePosition>({ x: -1000, y: -1000 })
  const animationFrameRef = useRef<number>()

  // Configuration
  const PARTICLE_COUNT = 80
  const CONNECTION_DISTANCE = 120
  const MOUSE_RADIUS = 100
  const PARTICLE_SPEED = 0.3

  const createParticles = useCallback((width: number, height: number) => {
    const particles: Particle[] = []
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * PARTICLE_SPEED,
        vy: (Math.random() - 0.5) * PARTICLE_SPEED,
      })
    }
    return particles
  }, [])

  const draw = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number, isDark: boolean) => {
    ctx.clearRect(0, 0, width, height)

    const particles = particlesRef.current
    const mouse = mouseRef.current

    // Colors based on theme
    const lineColor = isDark 
      ? 'rgba(148, 163, 184, 0.15)'  // slate-400 with low transparency
      : 'rgba(71, 85, 105, 0.2)'     // slate-600 with better visibility
    const particleColor = isDark
      ? 'rgba(148, 163, 184, 0.3)'
      : 'rgba(71, 85, 105, 0.35)'

    // Update and draw particles
    particles.forEach((particle, i) => {
      // Update position
      particle.x += particle.vx
      particle.y += particle.vy

      // Bounce off walls
      if (particle.x < 0 || particle.x > width) particle.vx *= -1
      if (particle.y < 0 || particle.y > height) particle.vy *= -1

      // Mouse interaction - push particles away
      const dx = mouse.x - particle.x
      const dy = mouse.y - particle.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < MOUSE_RADIUS) {
        const force = (MOUSE_RADIUS - distance) / MOUSE_RADIUS
        const pushX = (dx / distance) * force * 2
        const pushY = (dy / distance) * force * 2
        particle.x -= pushX
        particle.y -= pushY
      }

      // Draw particle
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, 1.5, 0, Math.PI * 2)
      ctx.fillStyle = particleColor
      ctx.fill()

      // Draw connections
      for (let j = i + 1; j < particles.length; j++) {
        const other = particles[j]
        const connectionDx = particle.x - other.x
        const connectionDy = particle.y - other.y
        const connectionDistance = Math.sqrt(connectionDx * connectionDx + connectionDy * connectionDy)

        // Check if line should be broken by mouse
        let isBroken = false
        if (distance < MOUSE_RADIUS || 
            Math.sqrt((mouse.x - other.x) ** 2 + (mouse.y - other.y) ** 2) < MOUSE_RADIUS) {
          // Check if mouse is close to the line
          const lineLength = connectionDistance
          if (lineLength > 0) {
            // Distance from point to line segment
            const t = Math.max(0, Math.min(1, 
              ((mouse.x - particle.x) * connectionDx + (mouse.y - particle.y) * connectionDy) / (lineLength * lineLength)
            ))
            const closestX = particle.x + t * connectionDx
            const closestY = particle.y + t * connectionDy
            const distToLine = Math.sqrt((mouse.x - closestX) ** 2 + (mouse.y - closestY) ** 2)
            
            if (distToLine < MOUSE_RADIUS * 0.6) {
              isBroken = true
            }
          }
        }

        if (connectionDistance < CONNECTION_DISTANCE && !isBroken) {
          const alpha = (1 - connectionDistance / CONNECTION_DISTANCE) * 0.5
          ctx.beginPath()
          ctx.moveTo(particle.x, particle.y)
          ctx.lineTo(other.x, other.y)
          ctx.strokeStyle = lineColor.replace(/[\d.]+\)$/g, `${alpha})`)
          ctx.lineWidth = 0.8
          ctx.stroke()
        }
      }
    })
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      particlesRef.current = createParticles(canvas.width, canvas.height)
    }

    resizeCanvas()

    // Check theme
    const isDark = document.documentElement.classList.contains('dark')

    // Animation loop
    const animate = () => {
      draw(ctx, canvas.width, canvas.height, isDark)
      animationFrameRef.current = requestAnimationFrame(animate)
    }
    animate()

    // Mouse move handler
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY }
    }

    // Mouse leave handler - reset mouse position
    const handleMouseLeave = () => {
      mouseRef.current = { x: -1000, y: -1000 }
    }

    // Handle theme changes
    const handleThemeChange = () => {
      // Re-read theme state
    }

    window.addEventListener('resize', resizeCanvas)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseleave', handleMouseLeave)
    document.addEventListener('theme-change', handleThemeChange)

    // Observe theme changes via MutationObserver
    const observer = new MutationObserver(() => {
      // Theme changed, will be picked up on next draw
    })
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    })

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseleave', handleMouseLeave)
      document.removeEventListener('theme-change', handleThemeChange)
      observer.disconnect()
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [createParticles, draw])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ touchAction: 'none' }}
      aria-hidden="true"
    />
  )
}
