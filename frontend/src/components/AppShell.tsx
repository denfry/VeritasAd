"use client"

import { ReactNode, useState, useEffect } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { 
  LayoutDashboard, 
  Search, 
  History, 
  User, 
  ShieldCheck, 
  Menu, 
  X, 
  LogOut,
  Zap,
  Crown,
  ChevronLeft,
  ChevronRight
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { ThemeToggle } from "./ThemeToggle"
import { CurrencySelectorCompact } from "./SiteHeader"
import { cn } from "@/lib/utils"
import { toast } from "sonner"

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

const planConfig = {
  free: { label: "Free", icon: User, color: "text-muted-foreground" },
  starter: { label: "Starter", icon: Zap, color: "text-green-500" },
  pro: { label: "Pro", icon: Zap, color: "text-blue-500" },
  business: { label: "Business", icon: Crown, color: "text-amber-500" },
  enterprise: { label: "Enterprise", icon: Crown, color: "text-purple-500" },
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, signOut } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isSigningOut, setIsSigningOut] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem("app-sidebar-collapsed")
    if (saved) {
      setIsCollapsed(saved === "true")
    }
  }, [])

  const toggleSidebar = () => {
    const newState = !isCollapsed
    setIsCollapsed(newState)
    localStorage.setItem("app-sidebar-collapsed", String(newState))
  }

  const handleSignOut = async () => {
    try {
      setIsSigningOut(true)
      await signOut()
      toast.success("Signed out successfully")
      router.push("/auth/login")
    } catch (error) {
      toast.error("Failed to sign out")
      console.error("Sign out error:", error)
    } finally {
      setIsSigningOut(false)
    }
  }

  const userPlan = user?.plan || "free"
  const planInfo = planConfig[userPlan as keyof typeof planConfig] || planConfig.free

  return (
    <div className="relative flex min-h-screen overflow-hidden text-foreground">
      <div className="pointer-events-none absolute inset-0 z-0">
        <div className="absolute -left-24 top-[-180px] h-[460px] w-[460px] rounded-full bg-sky-500/10 blur-3xl" />
        <div className="absolute -right-24 bottom-[-180px] h-[520px] w-[520px] rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,hsl(var(--border)/0.08)_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--border)/0.08)_1px,transparent_1px)] bg-[size:44px_44px]" />
      </div>
      
      {/* Sidebar - Desktop */}
      <motion.aside 
        initial={false}
        animate={{ width: isCollapsed ? 80 : 256 }}
        className="hidden md:flex flex-col border-r border-border/50 bg-card/55 backdrop-blur-2xl sticky top-0 h-screen transition-all duration-300 overflow-visible z-30"
      >
        <div className="p-4 flex items-center justify-between border-b border-border/20">
          <Link href="/" className="flex items-center gap-3 font-bold text-xl group px-2 overflow-hidden whitespace-nowrap">
            <motion.div
            className="h-8 w-8 shrink-0 items-center justify-center rounded-full gradient-premium text-primary-foreground shadow-lg shadow-primary/20 flex"
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

        <nav className="flex-1 px-3 py-4 space-y-1 mt-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                title={isCollapsed ? item.label : ""}
                className={cn(
                  "flex items-center gap-3 px-4 py-2.5 rounded-2xl transition-all duration-200 group relative",
                  isActive 
                    ? "bg-primary/10 text-primary font-semibold" 
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

        {/* User Profile Section */}
        {!isCollapsed && user && (
          <div className="px-3 py-3 border-t border-border/20">
            <div className="flex items-center gap-3 rounded-xl bg-muted/50 p-2">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <User className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium">
                  {user.email?.split('@')[0] || "User"}
                </p>
                <div className="flex items-center gap-1">
                  <planInfo.icon className={cn("h-3 w-3", planInfo.color)} />
                  <span className={cn("text-[10px]", planInfo.color)}>
                    {planInfo.label}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="p-3 mt-auto border-t border-border/20 space-y-2">
          <div className={cn(
            "flex items-center justify-between px-2 bg-muted/50 py-2 rounded-xl",
            isCollapsed && "flex-col gap-2 py-3"
          )}>
            <ThemeToggle />
            {!isCollapsed && <div className="h-4 w-px bg-border/50" />}
            <CurrencySelectorCompact />
          </div>
          
          <button 
            onClick={handleSignOut}
            disabled={isSigningOut}
            title={isCollapsed ? "Sign out" : ""}
            className={cn(
                  "flex items-center gap-3 w-full px-4 py-2.5 rounded-2xl text-muted-foreground hover:bg-red-500/10 hover:text-red-500 transition-all group disabled:opacity-50",
              isCollapsed && "justify-center px-0"
            )}
          >
            <LogOut className={cn("h-4 w-4 shrink-0", isSigningOut && "animate-pulse")} />
            {!isCollapsed && <span className="text-xs font-medium">Sign out</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="relative z-10 flex min-h-screen flex-1 flex-col">
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
              {user && (
                <div className="flex items-center gap-3 px-4 py-3 mb-2 rounded-xl bg-muted/50">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium">
                      {user.email?.split('@')[0] || "User"}
                    </p>
                    <div className="flex items-center gap-1">
                      <planInfo.icon className={cn("h-3 w-3", planInfo.color)} />
                      <span className={cn("text-[10px]", planInfo.color)}>
                        {planInfo.label}
                      </span>
                    </div>
                  </div>
                </div>
              )}
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    pathname === item.href ? "bg-primary text-primary-foreground font-semibold" : "hover:bg-muted"
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              ))}
              
              <div className="border-t pt-2 mt-2">
                <button
                  onClick={() => {
                    handleSignOut()
                    setIsMobileMenuOpen(false)
                  }}
                  className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-muted-foreground hover:bg-red-500/10 hover:text-red-500"
                >
                  <LogOut className="h-5 w-5" />
                  <span>Sign out</span>
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Page Content */}
        <main className="flex-1 pb-20 md:pb-0">
          {children}
        </main>
        
        {/* Mobile Bottom Navigation */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur-md border-t border-border/50 z-50 px-2 py-2">
          <div className="flex justify-around items-center">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors",
                    isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <item.icon className={cn("h-5 w-5", isActive && "fill-primary/20")} />
                  <span className="text-[10px] font-medium">{item.label}</span>
                </Link>
              )
            })}
          </div>
        </nav>
      </div>
    </div>
  )
}
