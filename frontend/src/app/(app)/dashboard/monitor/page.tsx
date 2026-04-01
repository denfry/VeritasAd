"use client"

import { motion } from "framer-motion"
import { Activity, Construction } from "lucide-react"

export default function MonitorPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="h-20 w-20 rounded-3xl bg-muted/50 border-2 border-dashed border-border/50 flex items-center justify-center"
      >
        <Construction className="h-10 w-10 text-muted-foreground/50" />
      </motion.div>

      <div className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">Brand Intelligence</h1>
        <p className="text-muted-foreground max-w-md">
          This feature is under development. Soon you&apos;ll be able to proactively monitor keywords and brands across social platforms.
        </p>
      </div>

      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Activity className="h-4 w-4 animate-pulse" />
        <span>Coming soon</span>
      </div>
    </div>
  )
}
