"use client"

import { ReactNode, useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { 
  LayoutDashboard, 
  Search, 
  History, 
  User, 
  Settings, 
  ShieldCheck, 
  Menu, 
  X, 
  LogOut,
  Zap,
  CreditCard,
  Sparkles,
  ChevronLeft,
  ChevronRight
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { ThemeToggle } from "./ThemeToggle"
import { CurrencySelectorCompact } from "./SiteHeader"
import { cn } from "@/lib/utils"

interface AppShellProps {
  children: ReactNode
}

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/analyze", label: "Analyze", icon: Search },
  { href: "/history", label: "History", icon: History },
  { href: "/pricing", label: "Pricing", icon: Zap },
  { href: "/account", label: "Account", icon: User },
]

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname()
  const { user, signOut } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem("app-sidebar-collapsed")
    if (saved) {
      setIsCollapsed(saved === "true")
    }
    setIsMounted(true)
  }, [])

  const toggleSidebar = () => {
    const newState = !isCollapsed
    setIsCollapsed(newState)
    localStorage.setItem("app-sidebar-collapsed", String(newState))
  }

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Sidebar - Desktop */}
      <motion.aside 
        initial={false}
        animate={{ width: isCollapsed ? 80 : 256 }}
        className="hidden md:flex flex-col border-r border-border/40 bg-card/30 backdrop-blur-2xl sticky top-0 h-screen transition-all duration-300 overflow-visible z-30"
      >
        <div className="p-5 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 font-bold text-xl group px-2 overflow-hidden whitespace-nowrap">
            <motion.div
              className="h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-primary text-primary-foreground shadow-lg shadow-primary/20 flex"
              whileHover={{ scale: 1.05, rotate: 5 }}
            >
              <ShieldCheck className="h-4 w-4" />
            </motion.div>
            {!isCollapsed && (
              <motion.span 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="gradient-text tracking-tight text-lg"
              >
                VeritasAd
              </motion.span>
            )}
          </Link>
          
          <button 
            onClick={toggleSidebar}
            className="absolute -right-3 top-16 flex h-6 w-6 items-center justify-center rounded-full border bg-background shadow-md hover:bg-accent z-40"
          >
            {isCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
          </button>
        </div>

        <nav className="flex-1 px-3 space-y-1 mt-6">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                title={isCollapsed ? item.label : ""}
                className={cn(
                  "flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-200 group relative",
                  isActive 
                    ? "bg-primary/10 text-primary font-bold" 
                    : "hover:bg-muted text-muted-foreground hover:text-foreground",
                  isCollapsed && "justify-center px-0"
                )}
              >
                <item.icon className={cn("h-4.5 w-4.5 shrink-0", isActive ? "text-primary" : "group-hover:scale-110 transition-transform")} />
                {!isCollapsed && (
                  <motion.span 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-sm truncate"
                  >
                    {item.label}
                  </motion.span>
                )}
                {isActive && !isCollapsed && (
                  <motion.div 
                    layoutId="activeTabIndicator"
                    className="absolute left-0 w-1 h-5 bg-primary rounded-r-full"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 mt-auto border-t border-border/40 space-y-4">
          <div className={cn(
            "flex items-center justify-between px-2 bg-muted/50 py-2 rounded-xl",
            isCollapsed && "flex-col gap-2 py-4"
          )}>
            <ThemeToggle />
            {!isCollapsed && <div className="h-4 w-px bg-border/50" />}
            <CurrencySelectorCompact />
          </div>
          
          <button 
            onClick={() => signOut()}
            title={isCollapsed ? "Sign out" : ""}
            className={cn(
              "flex items-center gap-3 w-full px-4 py-2.5 rounded-xl text-muted-foreground hover:bg-red-500/10 hover:text-red-500 transition-all group",
              isCollapsed && "justify-center px-0"
            )}
          >
            <LogOut className="h-4 w-4 shrink-0 group-hover:translate-x-1 transition-transform" />
            {!isCollapsed && <span className="text-xs font-bold uppercase tracking-widest">Sign out</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-h-screen relative">
        {/* Mobile Header */}
        <header className="md:hidden sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-md px-4 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <span>VeritasAd</span>
          </Link>
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg bg-muted text-foreground"
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </header>

        {/* Mobile Navigation Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-b border-border/50 bg-card px-4 py-4 space-y-1 overflow-hidden"
            >
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    pathname === item.href ? "bg-primary text-primary-foreground font-bold" : "hover:bg-muted"
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Page Content */}
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  )
}
