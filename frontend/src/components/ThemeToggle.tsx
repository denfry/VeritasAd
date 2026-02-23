"use client"

import { useTheme } from "next-themes"
import { useEffect, useState } from "react"
import { Moon, Sun } from "lucide-react"
import { motion } from "framer-motion"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <button
        className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-background text-muted-foreground hover:text-foreground hover:border-muted-foreground transition-colors"
        aria-label="Toggle theme"
        disabled
      >
        <Sun className="h-5 w-5" />
      </button>
    )
  }

  const isDark = theme === "dark"

  return (
    <motion.button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="relative inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-background text-muted-foreground hover:text-foreground hover:border-primary/50 hover:bg-primary/5 transition-all duration-300 overflow-hidden group"
      aria-label="Toggle theme"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={false}
    >
      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-primary/0 via-primary/0 to-primary/0 group-hover:from-primary/10 group-hover:via-primary/5 group-hover:to-primary/10 transition-all duration-500"
        initial={false}
      />
      
      {/* Icons container */}
      <div className="relative w-5 h-5">
        {/* Sun icon */}
        <motion.div
          className="absolute inset-0"
          initial={false}
          animate={{
            rotate: isDark ? 90 : 0,
            opacity: isDark ? 0 : 1,
            scale: isDark ? 0.5 : 1,
          }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <Sun className="h-5 w-5" />
        </motion.div>
        
        {/* Moon icon */}
        <motion.div
          className="absolute inset-0"
          initial={false}
          animate={{
            rotate: isDark ? 0 : -90,
            opacity: isDark ? 1 : 0,
            scale: isDark ? 1 : 0.5,
          }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <Moon className="h-5 w-5" />
        </motion.div>
      </div>
    </motion.button>
  )
}
