"use client"

import dynamic from "next/dynamic"
import { type ReactNode } from "react"

const ThreeSceneFallback = () => (
  <div className="fixed inset-0 z-0 pointer-events-none bg-gradient-to-br from-primary/5 via-transparent to-cyan-500/5" />
)

export function ThreeScene({
  children,
  intensity = "medium",
  type = "neural",
}: {
  children?: ReactNode
  intensity?: "light" | "medium" | "heavy"
  type?: "neural" | "particles"
}) {
  const NeuralNetworkBackground = dynamic(
    () =>
      import("@/components/three/NeuralNetworkBackground").then(
        (mod) => mod.NeuralNetworkBackground,
      ),
    {
      ssr: false,
      loading: () => <ThreeSceneFallback />,
    },
  )

  const FloatingParticles = dynamic(
    () =>
      import("@/components/three/NeuralNetworkBackground").then(
        (mod) => mod.FloatingParticles,
      ),
    {
      ssr: false,
      loading: () => <ThreeSceneFallback />,
    },
  )

  if (typeof window === "undefined") {
    return <>{children}</>
  }

  if (type === "neural") {
    return (
      <NeuralNetworkBackground intensity={intensity}>
        {children}
      </NeuralNetworkBackground>
    )
  }

  return (
    <div className="relative">
      <FloatingParticles
        density={intensity}
        color="#3b82f6"
      />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
