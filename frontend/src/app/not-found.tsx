"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowLeft, Search, ShieldCheck } from "lucide-react"
import { ThreeScene } from "@/components/three/ThreeScene"

export default function NotFound() {
  return (
    <ThreeScene intensity="light" type="particles">
      <div className="flex min-h-screen flex-col items-center justify-center gap-8 px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-3 mb-4"
        >
          <ShieldCheck className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold gradient-text">VeritasAd</span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-center space-y-6 max-w-lg"
        >
          <div className="relative">
            <h1 className="text-8xl font-black gradient-text tracking-tight">404</h1>
            <div className="absolute inset-0 blur-3xl opacity-30 bg-primary/20 rounded-full" />
          </div>

          <div className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight">Page not found</h2>
            <p className="text-muted-foreground leading-relaxed">
              The page you are looking for does not exist or has been moved. 
              Let&apos;s get you back on track.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
            <Link
              href="/"
              className="btn btn-primary h-12 px-8 gap-2 rounded-full font-semibold shadow-lg shadow-primary/20"
            >
              <ArrowLeft className="h-4 w-4" />
              Go to homepage
            </Link>
            <Link
              href="/analyze"
              className="btn btn-outline h-12 px-8 gap-2 rounded-full font-semibold"
            >
              <Search className="h-4 w-4" />
              Start analysis
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex flex-wrap gap-2 justify-center pt-8"
        >
          {["Dashboard", "History", "Pricing", "Docs"].map((item) => (
            <Link
              key={item}
              href={`/${item.toLowerCase()}`}
              className="px-4 py-2 rounded-full border border-border/50 text-xs font-medium text-muted-foreground hover:text-foreground hover:border-primary/30 hover:bg-primary/5 transition-all"
            >
              {item}
            </Link>
          ))}
        </motion.div>
      </div>
    </ThreeScene>
  )
}
