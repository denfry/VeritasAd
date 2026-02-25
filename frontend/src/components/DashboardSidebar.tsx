"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  LayoutDashboard, 
  BarChart3, 
  History, 
  CreditCard, 
  Settings, 
  LogOut,
  ShieldCheck,
  Activity,
  Key,
  ChevronLeft,
  ChevronRight
} from "lucide-react"
import { cn } from "@/lib/utils"
import { motion, AnimatePresence } from "framer-motion"

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Monitor", href: "/dashboard/monitor", icon: Activity },
  { name: "Analyze", href: "/analyze", icon: BarChart3 },
  { name: "History", href: "/history", icon: History },
  { name: "Billing", href: "/payment", icon: CreditCard },
  { name: "API Access", href: "/dashboard/settings/api", icon: Key },
  { name: "Settings", href: "/account", icon: Settings },
]

export function DashboardSidebar({ className, showBorder = true }: { className?: string, showBorder?: boolean }) {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem("dashboard-sidebar-collapsed")
    if (saved) {
      setIsCollapsed(saved === "true")
    }
    setIsMounted(true)
  }, [])

  const toggleSidebar = () => {
    const newState = !isCollapsed
    setIsCollapsed(newState)
    localStorage.setItem("dashboard-sidebar-collapsed", String(newState))
  }

  if (!isMounted) {
    return <div className={cn("h-full w-64 border-r bg-card/50", className)} />
  }

  return (
    <motion.div 
      initial={false}
      animate={{ width: isCollapsed ? 80 : 256 }}
      className={cn(
        "relative flex h-full flex-col bg-card transition-all duration-300 ease-in-out z-20",
        showBorder && "border-r",
        className
      )}
    >
      <div className="flex h-14 items-center justify-between border-b px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold overflow-hidden whitespace-nowrap">
          <ShieldCheck className="h-6 w-6 shrink-0" />
          {!isCollapsed && (
            <motion.span 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="gradient-text"
            >
              VeritasAd
            </motion.span>
          )}
        </Link>
        <button 
          onClick={toggleSidebar}
          className="absolute -right-3 top-20 hidden md:flex h-6 w-6 items-center justify-center rounded-full border bg-background shadow-md hover:bg-accent"
        >
          {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="grid gap-1 px-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                title={isCollapsed ? item.name : ""}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground group",
                  isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground",
                  isCollapsed && "justify-center px-2"
                )}
              >
                <item.icon className={cn("h-4 w-4 shrink-0", isActive ? "text-primary" : "group-hover:text-foreground")} />
                {!isCollapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="truncate"
                  >
                    {item.name}
                  </motion.span>
                )}
              </Link>
            )
          })}
        </nav>
      </div>

      <div className="border-t p-4">
        <button 
          className={cn(
            "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
            isCollapsed && "justify-center px-2"
          )}
          title={isCollapsed ? "Sign out" : ""}
        >
          <LogOut className="h-4 w-4 shrink-0" />
          {!isCollapsed && <span>Sign out</span>}
        </button>
      </div>
    </motion.div>
  )
}
