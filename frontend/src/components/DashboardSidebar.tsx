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
  Zap
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
  free: { label: "Free", icon: User, color: "text-muted-foreground" },
  starter: { label: "Starter", icon: Zap, color: "text-green-500" },
  pro: { label: "Pro", icon: Zap, color: "text-blue-500" },
  business: { label: "Business", icon: Crown, color: "text-amber-500" },
  enterprise: { label: "Enterprise", icon: Crown, color: "text-purple-500" },
}

export function DashboardSidebar({ className, showBorder = true }: { className?: string, showBorder?: boolean }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, signOut } = useAuth()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const [isSigningOut, setIsSigningOut] = useState(false)

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

      {!isCollapsed && user && (
        <div className="border-t px-3 py-3">
          <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-2">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <User className="h-4 w-4 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {user.email?.split('@')[0] || "User"}
              </p>
              <div className="flex items-center gap-1">
                <planInfo.icon className={cn("h-3 w-3", planInfo.color)} />
                <span className={cn("text-xs", planInfo.color)}>
                  {planInfo.label}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="border-t p-4">
        <button 
          onClick={handleSignOut}
          disabled={isSigningOut}
          className={cn(
            "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-50",
            isCollapsed && "justify-center px-2"
          )}
          title={isCollapsed ? "Sign out" : ""}
        >
          <LogOut className={cn("h-4 w-4 shrink-0", isSigningOut && "animate-pulse")} />
          {!isCollapsed && <span>{isSigningOut ? "Signing out..." : "Sign out"}</span>}
        </button>
      </div>
    </motion.div>
  )
}
