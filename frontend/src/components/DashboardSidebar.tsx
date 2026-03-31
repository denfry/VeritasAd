"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
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
  ChevronRight,
  User,
  Crown,
  Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { useAuth } from "@/contexts/auth-context"
import { toast } from "sonner"

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Monitor", href: "/dashboard/monitor", icon: Activity },
  { name: "Analyze", href: "/analyze", icon: BarChart3 },
  { name: "History", href: "/history", icon: History },
  { name: "Billing", href: "/account?tab=billing", icon: CreditCard },
  { name: "API Access", href: "/dashboard/settings/api", icon: Key },
  { name: "Settings", href: "/account", icon: Settings },
]

const planConfig = {
  free: { label: "Free", icon: User, color: "text-muted-foreground", bg: "bg-muted/60" },
  starter: { label: "Starter", icon: Zap, color: "text-green-500", bg: "bg-green-500/10" },
  pro: { label: "Pro", icon: Zap, color: "text-primary", bg: "bg-primary/10" },
  business: { label: "Business", icon: Crown, color: "text-amber-500", bg: "bg-amber-500/10" },
  enterprise: { label: "Enterprise", icon: Crown, color: "text-purple-500", bg: "bg-purple-500/10" },
}

export function DashboardSidebar({ className, showBorder = true }: { className?: string; showBorder?: boolean }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, signOut } = useAuth()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const [isSigningOut, setIsSigningOut] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem("dashboard-sidebar-collapsed")
    if (saved) setIsCollapsed(saved === "true")
    setIsMounted(true)
  }, [])

  const toggleSidebar = () => {
    const next = !isCollapsed
    setIsCollapsed(next)
    localStorage.setItem("dashboard-sidebar-collapsed", String(next))
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

  if (!isMounted) {
    return <div className={cn("h-full w-64 border-r bg-card/50", className)} />
  }

  return (
    <motion.div
      initial={false}
      animate={{ width: isCollapsed ? 72 : 240 }}
      className={cn(
        "relative flex h-full flex-col bg-card/80 backdrop-blur-xl transition-all duration-300 ease-in-out z-20",
        showBorder && "border-r border-border/60",
        className
      )}
    >
      {/* Header */}
      <div className="flex h-14 items-center justify-between border-b border-border/60 px-4">
        <Link href="/" className="flex items-center gap-2.5 overflow-hidden whitespace-nowrap group min-w-0">
          <span className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full gradient-premium text-primary-foreground shadow-[0_4px_12px_-4px_hsl(var(--primary)/0.5)]">
            <ShieldCheck className="h-3.5 w-3.5" />
          </span>
          {!isCollapsed && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="gradient-text font-semibold text-sm truncate"
            >
              VeritasAd
            </motion.span>
          )}
        </Link>

        {/* Collapse toggle */}
        <button
          onClick={toggleSidebar}
          className="absolute -right-3 top-[4.5rem] hidden md:flex h-6 w-6 items-center justify-center rounded-full border border-border/70 bg-background shadow-sm hover:bg-accent transition-colors z-30"
        >
          {isCollapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronLeft className="h-3 w-3" />
          )}
        </button>
      </div>

      {/* Nav */}
      <div className="flex-1 overflow-y-auto py-3">
        <nav className="grid gap-0.5 px-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && !item.href.includes("?") && pathname.startsWith(item.href))
            return (
              <Link
                key={item.name}
                href={item.href}
                title={isCollapsed ? item.name : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-all duration-150 group",
                  isActive
                    ? "bg-primary/10 text-primary shadow-[inset_0_0_0_1px_hsl(var(--primary)/0.15)]"
                    : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
                  isCollapsed && "justify-center px-2"
                )}
              >
                <item.icon
                  className={cn(
                    "h-4 w-4 shrink-0 transition-colors",
                    isActive ? "text-primary" : "group-hover:text-foreground"
                  )}
                />
                {!isCollapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="truncate"
                  >
                    {item.name}
                  </motion.span>
                )}
                {isActive && !isCollapsed && (
                  <motion.span
                    layoutId="sidebar-active"
                    className="ml-auto h-1.5 w-1.5 rounded-full bg-primary"
                  />
                )}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* User info */}
      {!isCollapsed && user && (
        <div className="border-t border-border/60 px-3 py-3">
          <div className="flex items-center gap-3 rounded-xl bg-muted/40 p-2.5">
            <div className={cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-full", planInfo.bg)}>
              <planInfo.icon className={cn("h-3.5 w-3.5", planInfo.color)} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {user.email?.split("@")[0] || "User"}
              </p>
              <p className={cn("text-xs font-medium", planInfo.color)}>{planInfo.label}</p>
            </div>
          </div>
        </div>
      )}

      {/* Sign out */}
      <div className="border-t border-border/60 p-3">
        <button
          onClick={handleSignOut}
          disabled={isSigningOut}
          title={isCollapsed ? "Sign out" : undefined}
          className={cn(
            "flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-muted-foreground transition-all duration-150 hover:bg-red-500/8 hover:text-red-500 disabled:opacity-50",
            isCollapsed && "justify-center px-2"
          )}
        >
          <LogOut className={cn("h-4 w-4 shrink-0", isSigningOut && "animate-pulse")} />
          {!isCollapsed && (
            <span>{isSigningOut ? "Signing out…" : "Sign out"}</span>
          )}
        </button>
      </div>
    </motion.div>
  )
}
