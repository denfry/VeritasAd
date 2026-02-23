/**
 * Command Palette - BigTech Standard
 * Аналог Command Menu в Vercel, Linear, Raycast
 * 
 * Usage: Press Cmd+K (or Ctrl+K) to open
 */
"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { Command } from "lucide-react"
import { createPortal } from "react-dom"

type CommandItem = {
  id: string
  label: string
  shortcut?: string
  icon?: React.ReactNode
  action: () => void
  category?: string
}

type CommandPaletteProps = {
  isOpen: boolean
  onClose: () => void
  commands: CommandItem[]
}

export function CommandPalette({ isOpen, onClose, commands }: CommandPaletteProps) {
  const [search, setSearch] = useState("")
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  // Filter commands based on search
  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.id.toLowerCase().includes(search.toLowerCase())
  )

  // Focus input on open
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Reset state on open
  useEffect(() => {
    if (isOpen) {
      setSearch("")
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault()
      setSelectedIndex(prev => 
        prev < filteredCommands.length - 1 ? prev + 1 : 0
      )
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      setSelectedIndex(prev => 
        prev > 0 ? prev - 1 : filteredCommands.length - 1
      )
    } else if (e.key === "Enter") {
      e.preventDefault()
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action()
        onClose()
      }
    } else if (e.key === "Escape") {
      onClose()
    }
  }, [filteredCommands, selectedIndex, onClose])

  // Execute command
  const executeCommand = (cmd: CommandItem) => {
    cmd.action()
    onClose()
  }

  if (!isOpen) return null

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Command Palette */}
      <div className="relative w-full max-w-xl bg-background border rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Search Input */}
        <div className="flex items-center border-b px-4 py-3">
          <Command className="h-5 w-5 text-muted-foreground mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command or search..."
            className="flex-1 bg-transparent outline-none text-sm placeholder:text-muted-foreground"
          />
          <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
            <span className="text-xs">ESC</span>
          </kbd>
        </div>
        
        {/* Results */}
        <div 
          ref={listRef}
          className="max-h-[400px] overflow-y-auto py-2"
        >
          {filteredCommands.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              No results found for "{search}"
            </div>
          ) : (
            <div className="space-y-1">
              {filteredCommands.map((cmd, index) => (
                <button
                  key={cmd.id}
                  onClick={() => executeCommand(cmd)}
                  className={`w-full px-4 py-2.5 text-left flex items-center justify-between gap-2 transition-colors ${
                    index === selectedIndex
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {cmd.icon && (
                      <span className="text-muted-foreground">
                        {cmd.icon}
                      </span>
                    )}
                    <div>
                      <div className="text-sm font-medium">{cmd.label}</div>
                      {cmd.category && (
                        <div className="text-xs text-muted-foreground opacity-70">
                          {cmd.category}
                        </div>
                      )}
                    </div>
                  </div>
                  {cmd.shortcut && (
                    <kbd className="hidden sm:inline-flex h-6 items-center gap-1 rounded border bg-muted/50 px-2 font-mono text-[10px] font-medium text-muted-foreground">
                      {cmd.shortcut}
                    </kbd>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="border-t px-4 py-2 text-xs text-muted-foreground flex items-center justify-between">
          <span>{filteredCommands.length} commands</span>
          <div className="flex items-center gap-2">
            <span>Navigate</span>
            <kbd className="h-4 w-4 rounded border bg-muted/50 flex items-center justify-center text-[9px]">↑</kbd>
            <kbd className="h-4 w-4 rounded border bg-muted/50 flex items-center justify-center text-[9px]">↓</kbd>
            <span>Select</span>
            <kbd className="h-4 w-4 rounded border bg-muted/50 flex items-center justify-center text-[9px]">↵</kbd>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}


// Command Palette Trigger Hook
export function useCommandPalette(commands: CommandItem[]) {
  const [isOpen, setIsOpen] = useState(false)

  // Keyboard shortcut to open
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K or Ctrl+K
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setIsOpen(prev => !prev)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen(prev => !prev),
    Component: (
      <CommandPalette
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        commands={commands}
      />
    ),
  }
}


// Default admin commands
export function useAdminCommands() {
  const router = useRouter()
  
  const commands: CommandItem[] = [
    // Navigation
    {
      id: "dashboard",
      label: "Go to Dashboard",
      shortcut: "G D",
      category: "Navigation",
      action: () => router.push("/admin"),
    },
    {
      id: "users",
      label: "View Users",
      shortcut: "G U",
      category: "Navigation",
      action: () => router.push("/admin#users"),
    },
    {
      id: "analytics",
      label: "View Analytics",
      shortcut: "G A",
      category: "Navigation",
      action: () => router.push("/admin#analytics"),
    },
    {
      id: "audit-logs",
      label: "Audit Logs",
      shortcut: "G L",
      category: "Navigation",
      action: () => router.push("/admin/audit-logs"),
    },
    {
      id: "account",
      label: "My Account",
      category: "Navigation",
      action: () => router.push("/account"),
    },
    
    // Actions
    {
      id: "new-user",
      label: "Create New User",
      category: "Actions",
      action: () => router.push("/admin/users/new"),
    },
    {
      id: "export-users",
      label: "Export Users",
      category: "Actions",
      action: () => router.push("/admin?export=users"),
    },
    {
      id: "export-analyses",
      label: "Export Analyses",
      category: "Actions",
      action: () => router.push("/admin?export=analyses"),
    },
    
    // Settings
    {
      id: "security",
      label: "Security Settings",
      category: "Settings",
      action: () => router.push("/security"),
    },
    {
      id: "2fa",
      label: "Two-Factor Auth",
      category: "Settings",
      action: () => router.push("/security#2fa"),
    },
    {
      id: "sessions",
      label: "Active Sessions",
      category: "Settings",
      action: () => router.push("/security#sessions"),
    },
  ]
  
  return commands
}
