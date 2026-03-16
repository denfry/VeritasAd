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

  const filteredCommands = commands.filter((cmd) =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.id.toLowerCase().includes(search.toLowerCase())
  )

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  useEffect(() => {
    if (isOpen) {
      setSearch("")
      setSelectedIndex(0)
    }
  }, [isOpen])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault()
      setSelectedIndex((prev) => (prev < filteredCommands.length - 1 ? prev + 1 : 0))
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : filteredCommands.length - 1))
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

  const executeCommand = (cmd: CommandItem) => {
    cmd.action()
    onClose()
  }

  if (!isOpen) return null

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-xl overflow-hidden rounded-xl border bg-background shadow-2xl animate-in fade-in zoom-in duration-200">
        <div className="flex items-center border-b px-4 py-3">
          <Command className="mr-3 h-5 w-5 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command or search..."
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="hidden h-5 items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground sm:inline-flex">
            <span className="text-xs">ESC</span>
          </kbd>
        </div>

        <div ref={listRef} className="max-h-[400px] overflow-y-auto py-2">
          {filteredCommands.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              No results found for &quot;{search}&quot;
            </div>
          ) : (
            <div className="space-y-1">
              {filteredCommands.map((cmd, index) => (
                <button
                  key={cmd.id}
                  onClick={() => executeCommand(cmd)}
                  className={`flex w-full items-center justify-between gap-2 px-4 py-2.5 text-left transition-colors ${
                    index === selectedIndex ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {cmd.icon && <span className="text-muted-foreground">{cmd.icon}</span>}
                    <div>
                      <div className="text-sm font-medium">{cmd.label}</div>
                      {cmd.category && (
                        <div className="text-xs text-muted-foreground opacity-70">{cmd.category}</div>
                      )}
                    </div>
                  </div>
                  {cmd.shortcut && (
                    <kbd className="hidden h-6 items-center gap-1 rounded border bg-muted/50 px-2 font-mono text-[10px] font-medium text-muted-foreground sm:inline-flex">
                      {cmd.shortcut}
                    </kbd>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center justify-between border-t px-4 py-2 text-xs text-muted-foreground">
          <span>{filteredCommands.length} commands</span>
          <div className="flex items-center gap-2">
            <span>Navigate</span>
            <kbd className="flex h-4 w-4 items-center justify-center rounded border bg-muted/50 text-[9px]">&uarr;</kbd>
            <kbd className="flex h-4 w-4 items-center justify-center rounded border bg-muted/50 text-[9px]">&darr;</kbd>
            <span>Select</span>
            <kbd className="flex h-4 w-4 items-center justify-center rounded border bg-muted/50 text-[9px]">&crarr;</kbd>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}

export function useCommandPalette(commands: CommandItem[]) {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setIsOpen((prev) => !prev)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen((prev) => !prev),
    Component: (
      <CommandPalette
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        commands={commands}
      />
    ),
  }
}

export function useAdminCommands() {
  const router = useRouter()

  const commands: CommandItem[] = [
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
