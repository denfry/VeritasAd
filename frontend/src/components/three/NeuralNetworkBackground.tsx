"use client"

import { useRef, useMemo, type ReactNode } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Float, MeshDistortMaterial } from "@react-three/drei"
import * as THREE from "three"

function AnimatedSphere({
  position,
  scale,
  speed,
  color,
  distort,
}: {
  position: [number, number, number]
  scale: number
  speed: number
  color: string
  distort: number
}) {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * speed * 0.3
      meshRef.current.rotation.y = state.clock.elapsedTime * speed * 0.2
    }
  })

  return (
    <Float speed={speed * 2} rotationIntensity={0.5} floatIntensity={1}>
      <mesh ref={meshRef} position={position} scale={scale}>
        <icosahedronGeometry args={[1, 4]} />
        <MeshDistortMaterial
          color={color}
          attach="material"
          distort={distort}
          speed={speed * 3}
          roughness={0.2}
          metalness={0.8}
          transparent
          opacity={0.6}
        />
      </mesh>
    </Float>
  )
}

function ParticleField({ count = 200 }: { count?: number }) {
  const meshRef = useRef<THREE.Points>(null!)

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 20
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20
    }
    return pos
  }, [count])

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.02
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.01
    }
  })

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.03}
        color="#3b82f6"
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  )
}

function NeuralNetwork({ nodeCount = 40 }: { nodeCount?: number }) {
  const groupRef = useRef<THREE.Group>(null!)

  const { nodes, lines } = useMemo(() => {
    const n: [number, number, number][] = []
    const l: [number, number][] = []
    for (let i = 0; i < nodeCount; i++) {
      n.push([
        (Math.random() - 0.5) * 16,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 8,
      ])
    }
    for (let i = 0; i < nodeCount; i++) {
      for (let j = i + 1; j < nodeCount; j++) {
        const dist = Math.sqrt(
          (n[i][0] - n[j][0]) ** 2 +
            (n[i][1] - n[j][1]) ** 2 +
            (n[i][2] - n[j][2]) ** 2,
        )
        if (dist < 5) {
          l.push([i, j])
        }
      }
    }
    return { nodes: n, lines: l }
  }, [nodeCount])

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.03
    }
  })

  return (
    <group ref={groupRef}>
      {nodes.map((pos, i) => (
        <mesh key={i} position={pos} scale={0.06}>
          <sphereGeometry args={[1, 8, 8]} />
          <meshStandardMaterial
            color="#06b6d4"
            emissive="#06b6d4"
            emissiveIntensity={0.5}
            transparent
            opacity={0.8}
          />
        </mesh>
      ))}
      {lines.map(([a, b], i) => (
        <line key={i}>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              args={[new Float32Array([...nodes[a], ...nodes[b]]), 3]}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#06b6d4" transparent opacity={0.15} />
        </line>
      ))}
    </group>
  )
}

export function NeuralNetworkBackground({
  children,
  intensity = "medium",
}: {
  children?: ReactNode
  intensity?: "light" | "medium" | "heavy"
}) {
  const config = {
    light: { nodes: 20, particles: 100, spheres: 1 },
    medium: { nodes: 40, particles: 200, spheres: 2 },
    heavy: { nodes: 60, particles: 400, spheres: 3 },
  }[intensity]

  return (
    <div className="relative">
      <div className="fixed inset-0 z-0 pointer-events-none">
        <Canvas
          camera={{ position: [0, 0, 10], fov: 60 }}
          dpr={[1, 1.5]}
          gl={{ alpha: true, antialias: true }}
        >
          <ambientLight intensity={0.3} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#f97316" />
          <NeuralNetwork nodeCount={config.nodes} />
          <ParticleField count={config.particles} />
          {config.spheres >= 1 && (
            <AnimatedSphere
              position={[4, 2, -3]}
              scale={0.8}
              speed={0.5}
              color="#3b82f6"
              distort={0.4}
            />
          )}
          {config.spheres >= 2 && (
            <AnimatedSphere
              position={[-4, -2, -2]}
              scale={0.6}
              speed={0.7}
              color="#06b6d4"
              distort={0.3}
            />
          )}
          {config.spheres >= 3 && (
            <AnimatedSphere
              position={[0, 3, -4]}
              scale={0.5}
              speed={0.6}
              color="#f97316"
              distort={0.5}
            />
          )}
        </Canvas>
      </div>
      <div className="relative z-10">{children}</div>
    </div>
  )
}

export function FloatingParticles({
  density = "medium",
  color = "#3b82f6",
}: {
  density?: "light" | "medium" | "heavy"
  color?: string
}) {
  const count = { light: 80, medium: 200, heavy: 400 }[density]

  return (
    <div className="fixed inset-0 z-0 pointer-events-none">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        dpr={[1, 1.2]}
        gl={{ alpha: true, antialias: false }}
      >
        <ambientLight intensity={0.2} />
        <ParticleField count={count} />
        <mesh>
          <sphereGeometry args={[0.1, 8, 8]} />
          <meshStandardMaterial color={color} transparent opacity={0.3} />
        </mesh>
      </Canvas>
    </div>
  )
}
