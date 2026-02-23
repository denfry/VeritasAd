/**
 * Keyboard Shortcuts - BigTech Standard
 * Аналог keyboard shortcuts в Linear, Vercel, GitHub
 * 
 * Global shortcuts:
 * - g + d = Go to Dashboard
 * - g + u = Go to Users
 * - g + a = Go to Analytics
 * - g + l = Go to Audit Logs
 * - ? = Show shortcuts help
 * - t = Toggle theme
 * - / = Focus search
 */
"use client"

import { useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

type ShortcutHandler = () => void

type Shortcut = {
  keys: string[]
  handler: ShortcutHandler
  description: string
  category: string
}

type UseKeyboardShortcutsOptions = {
  enabled?: boolean
  ignoreInputFields?: boolean
}

export function useKeyboardShortcuts(
  options: UseKeyboardShortcutsOptions = {}
) {
  const {
    enabled = true,
    ignoreInputFields = true,
  } = options
  
  const router = useRouter()
  
  // Track if we're in a sequence (e.g., pressed 'g' waiting for next key)
  const sequence = useCallback(() => {
    let pendingKey: string | null = null
    let timeout: NodeJS.Timeout | null = null
    
    const clearSequence = () => {
      pendingKey = null
      if (timeout) {
        clearTimeout(timeout)
        timeout = null
      }
    }
    
    return {
      set: (key: string) => {
        pendingKey = key
        timeout = setTimeout(clearSequence, 1000) // 1 second timeout
      },
      get: () => pendingKey,
      clear: clearSequence,
    }
  }, [])
  
  const sequenceState = sequence()
  
  useEffect(() => {
    if (!enabled) return
    
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in input/textarea
      if (ignoreInputFields) {
        const target = e.target as HTMLElement
        if (
          target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable
        ) {
          return
        }
      }
      
      // Handle sequences (g + [key])
      if (sequenceState.get() === "g") {
        const key = e.key.toLowerCase()
        
        if (key === "d") {
          e.preventDefault()
          router.push("/admin")
          toast.success("Navigated to Dashboard")
          sequenceState.clear()
          return
        }
        
        if (key === "u") {
          e.preventDefault()
          router.push("/admin#users")
          toast.success("Navigated to Users")
          sequenceState.clear()
          return
        }
        
        if (key === "a") {
          e.preventDefault()
          router.push("/admin#analytics")
          toast.success("Navigated to Analytics")
          sequenceState.clear()
          return
        }
        
        if (key === "l") {
          e.preventDefault()
          router.push("/admin/audit-logs")
          toast.success("Navigated to Audit Logs")
          sequenceState.clear()
          return
        }
        
        // Clear sequence if no match
        sequenceState.clear()
      }
      
      // Single key shortcuts
      const key = e.key.toLowerCase()
      
      // g - start sequence
      if (key === "g") {
        e.preventDefault()
        sequenceState.set("g")
        return
      }
      
      // ? - show help (would open modal in full implementation)
      if (key === "?" || (e.shiftKey && e.key === "/")) {
        e.preventDefault()
        toast.info("Keyboard shortcuts help (coming soon)")
        return
      }
      
      // / - focus search
      if (key === "/") {
        e.preventDefault()
        const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement
        if (searchInput) {
          searchInput.focus()
          toast.success("Search focused")
        }
        return
      }
      
      // t - toggle theme (if theme context exists)
      if (key === "t" && !e.metaKey && !e.ctrlKey) {
        // Would toggle theme here
        return
      }
      
      // Escape - close modals
      if (key === "escape") {
        // Close any open modals
        const modal = document.querySelector('[role="dialog"]')
        if (modal) {
          (modal as HTMLElement).querySelector("button")?.click()
        }
      }
    }
    
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [enabled, ignoreInputFields, router, sequenceState])
}


// Shortcuts help modal component
export function ShortcutsHelpModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null
  
  const shortcuts = [
    { category: "Navigation", items: [
      { keys: ["g", "d"], description: "Go to Dashboard" },
      { keys: ["g", "u"], description: "Go to Users" },
      { keys: ["g", "a"], description: "Go to Analytics" },
      { keys: ["g", "l"], description: "Go to Audit Logs" },
    ]},
    { category: "Actions", items: [
      { keys: ["Cmd+K"], description: "Open Command Palette" },
      { keys: ["/"], description: "Focus Search" },
      { keys: ["?"], description: "Show Help" },
      { keys: ["Escape"], description: "Close Modal" },
    ]},
  ]
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative bg-background border rounded-xl shadow-2xl p-6 max-w-lg w-full mx-4">
        <h2 className="text-xl font-semibold mb-4">Keyboard Shortcuts</h2>
        
        <div className="space-y-6">
          {shortcuts.map((group) => (
            <div key={group.category}>
              <h3 className="text-sm font-medium text-muted-foreground mb-2">
                {group.category}
              </h3>
              <div className="space-y-2">
                {group.items.map((shortcut) => (
                  <div
                    key={shortcut.description}
                    className="flex items-center justify-between"
                  >
                    <span className="text-sm">{shortcut.description}</span>
                    <div className="flex items-center gap-1">
                      {shortcut.keys.map((key, i) => (
                        <kbd
                          key={i}
                          className="h-6 min-w-[24px] rounded border bg-muted px-1.5 font-mono text-xs font-medium"
                        >
                          {key}
                        </kbd>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        <button
          onClick={onClose}
          className="btn btn-outline w-full mt-6"
        >
          Close
        </button>
      </div>
    </div>
  )
}


// Hook to show shortcuts help
export function useShortcutsHelp() {
  const [isOpen, setIsOpen] = useState(false)
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "?" || (e.shiftKey && e.key === "/")) {
        const target = e.target as HTMLElement
        if (
          target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable
        ) {
          return
        }
        
        e.preventDefault()
        setIsOpen(true)
      }
    }
    
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])
  
  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
  }
}

import { useState } from "react"
