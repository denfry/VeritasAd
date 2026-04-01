"use client"

import { useEffect, useState, useCallback, type ReactNode, type FormEvent } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { 
  getCurrentUserProfile, 
  getUserCredits, 
  getCreditHistory, 
  updateCurrentUserProfile,
  listUserSessions,
  revokeUserSession,
  getTwoFactorStatus,
  UserSession
} from "@/lib/api-client"
import type { UserProfile } from "@/types/api"
import type { UserCreditsResponse, CreditTransactionItem } from "@/lib/api-client"
import { toast } from "sonner"
import { 
  Loader2, LogOut, User as UserIcon, BarChart3, Zap, 
  Calendar, History, Shield, Mail, BadgeCheck, 
  ArrowUpRight, CreditCard, ChevronRight,
  Monitor, Smartphone, Globe, Trash2, ShieldCheck,
  Lock, Save
} from "lucide-react"
import Link from "next/link"
import { format, formatDistanceToNow } from "date-fns"
import { motion, AnimatePresence } from "framer-motion"
import { Skeleton } from "@/components/ui/Skeleton"

type AccountTab = "overview" | "profile" | "security" | "billing"

export default function AccountPage() {
  const router = useRouter()
  const { user, signOut, loading: authLoading } = useAuth()
  const [activeTab, setActiveTab] = useState<AccountTab>("overview")
  
  // Data state
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [credits, setCredits] = useState<UserCreditsResponse | null>(null)
  const [creditHistory, setCreditHistory] = useState<CreditTransactionItem[]>([])
  const [sessions, setSessions] = useState<UserSession[]>([])
  const [is2faEnabled, setIs2faEnabled] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  
  // Form state
  const [emailInput, setEmailInput] = useState("")
  const [isUpdating, setIsUpdating] = useState(false)

  const loadAllData = useCallback(async () => {
    setLoading(true)
    setLoadError(null)
    try {
      const [profileData, creditsData, historyData] = await Promise.all([
        getCurrentUserProfile(),
        getUserCredits(),
        getCreditHistory({ limit: 5 }),
      ])
      
      setProfile(profileData)
      setEmailInput(profileData.email || "")
      setCredits(creditsData)
      setCreditHistory(historyData.transactions)
      
      // Load sessions and 2FA if tab is security
      if (activeTab === "security") {
        const [sessionData, twoFactorData] = await Promise.all([
          listUserSessions(),
          getTwoFactorStatus().catch(() => ({ enabled: false })),
        ])
        setSessions(sessionData.sessions)
        setIs2faEnabled(twoFactorData.enabled)
      }
    } catch (error: unknown) {
      console.warn("Failed to load account data:", error)
      setLoadError(error instanceof Error ? error.message : "Failed to load account data")
    } finally {
      setLoading(false)
    }
  }, [activeTab, user])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
      return
    }

    if (user) {
      loadAllData()
    }
  }, [user, authLoading, router, loadAllData])

  // Reload security data when switching to security tab
  useEffect(() => {
    if (activeTab === "security" && profile) {
      listUserSessions().then(data => setSessions(data.sessions))
      getTwoFactorStatus().then(data => setIs2faEnabled(data.enabled)).catch(() => {})
    }
  }, [activeTab, profile])

  const handleUpdateProfile = async (e: FormEvent) => {
    e.preventDefault()
    setIsUpdating(true)
    try {
      const updated = await updateCurrentUserProfile({ email: emailInput })
      setProfile(updated)
      toast.success("Profile updated successfully")
    } catch {
      toast.error("Failed to update profile")
    } finally {
      setIsUpdating(false)
    }
  }

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await revokeUserSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      toast.success("Session revoked")
    } catch {
      toast.error("Failed to revoke session")
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
      toast.success("Signed out successfully")
      router.push("/")
    } catch {
      toast.error("Failed to sign out")
    }
  }

  const getUsagePercentage = () => {
    if (!profile || profile.daily_limit <= 0) return 0
    return Math.min((profile.daily_used / profile.daily_limit) * 100, 100)
  }

  const getPlanBadgeStyles = (plan: string) => {
    const styles: Record<string, string> = {
      free: "bg-slate-500/10 text-slate-500 border-slate-500/20",
      starter: "bg-blue-500/10 text-blue-500 border-blue-500/20",
      pro: "bg-purple-500/10 text-purple-600 border-purple-500/20",
      business: "bg-amber-500/10 text-amber-600 border-amber-500/20",
      enterprise: "bg-red-500/10 text-red-600 border-red-500/20",
    }
    return styles[plan.toLowerCase()] || styles.free
  }

  if (authLoading || loading) {
    return (
      
        
          <section className="container mx-auto max-w-7xl px-4 py-12 space-y-10 lg:py-16">
          {/* Profile Header skeleton */}
          <div className="surface p-8">
            <div className="flex flex-col md:flex-row md:items-center gap-8">
              <Skeleton className="h-24 w-24 rounded-2xl" />
              <div className="flex-1 space-y-3">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-5 w-32" />
              </div>
            </div>
          </div>
          
          {/* Tabs skeleton */}
          <div className="flex gap-4 border-b">
            {[1, 2, 3, 4].map(i => (
              <Skeleton key={i} className="h-10 w-24 rounded-t-lg" />
            ))}
          </div>
          
          {/* Content skeleton */}
          <div className="surface p-6 space-y-6">
            <Skeleton className="h-6 w-32" />
            <div className="grid gap-4 md:grid-cols-2">
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
            </div>
          </div>
        </section>
      
      
    )
  }

  if (loadError && !profile) {
    return (
      
        
          <section className="container mx-auto max-w-7xl px-4 py-12">
            <div className="surface p-8 space-y-4">
              <h1 className="text-2xl font-semibold">Account unavailable</h1>
              <p className="text-sm text-muted-foreground">{loadError}</p>
              <button className="btn btn-primary h-11 px-5 rounded-full" onClick={loadAllData}>
                Retry
              </button>
            </div>
          </section>
        
      
    )
  }

  if (!profile) return null

  return (
    
      
      <section className="container mx-auto max-w-7xl px-4 py-12 space-y-10 lg:py-16">
        {/* Profile Header Card */}
        <motion.div 
          className="surface p-8 relative overflow-hidden group"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
            <Shield className="h-40 w-40" />
          </div>
          <div className="absolute -bottom-24 -left-24 h-64 w-64 bg-primary/5 rounded-full blur-3xl" />
          
          <div className="flex flex-col md:flex-row md:items-center gap-8 relative z-10">
            <div className="h-24 w-24 rounded-[1.5rem] gradient-premium flex items-center justify-center text-primary-foreground shadow-xl shadow-primary/20">
              <UserIcon className="h-12 w-12" />
            </div>
            
            <div className="flex-1 space-y-2">
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-3xl font-semibold tracking-tight">{profile.email?.split('@')[0]}</h1>
                <span className={`px-3 py-1 rounded-full text-[10px] font-semibold uppercase border tracking-[0.22em] ${getPlanBadgeStyles(profile.plan)}`}>
                  {profile.plan} Plan
                </span>
                {profile.role === 'admin' && (
                  <span className="bg-primary text-primary-foreground px-2 py-0.5 rounded-full text-[10px] font-semibold flex items-center gap-1 shadow-sm">
                    <BadgeCheck className="h-3 w-3" /> ADMIN
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground font-bold">
                <span className="flex items-center gap-1.5"><Mail className="h-4 w-4" /> {profile.email}</span>
                <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4" /> Joined {format(new Date(profile.created_at || Date.now()), "MMM yyyy")}</span>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button onClick={handleSignOut} className="btn btn-outline gap-2 h-11 px-6 rounded-full border-red-500/20 text-red-500 hover:bg-red-500/10 font-semibold transition-all">
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 p-1 bg-muted/50 rounded-full w-fit">
           <TabButton active={activeTab === "overview"} onClick={() => setActiveTab("overview")} label="Overview" icon={<BarChart3 className="h-4 w-4" />} />
           <TabButton active={activeTab === "profile"} onClick={() => setActiveTab("profile")} label="Profile" icon={<UserIcon className="h-4 w-4" />} />
           <TabButton active={activeTab === "security"} onClick={() => setActiveTab("security")} label="Security" icon={<Lock className="h-4 w-4" />} />
           <TabButton active={activeTab === "billing"} onClick={() => setActiveTab("billing")} label="Billing" icon={<CreditCard className="h-4 w-4" />} />
        </div>

        <AnimatePresence mode="wait">
          {activeTab === "overview" && (
            <motion.div 
              key="overview"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="grid gap-8 lg:grid-cols-3"
            >
              <div className="lg:col-span-2 space-y-8">
                {/* Usage Stats */}
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="surface p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                        <BarChart3 className="h-5 w-5" />
                      </div>
                      <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Daily Quota</span>
                    </div>
                    <div>
                      <div className="flex items-end gap-2 mb-1">
                        <span className="text-3xl font-bold">{profile.daily_used}</span>
                        <span className="text-muted-foreground mb-1 font-medium">/ {profile.daily_limit} used</span>
                      </div>
                      <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                        <motion.div 
                          className={`h-full ${getUsagePercentage() > 90 ? 'bg-red-500' : 'bg-primary'}`}
                          initial={{ width: 0 }}
                          animate={{ width: `${getUsagePercentage()}%` }}
                          transition={{ duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="surface p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="h-10 w-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-600">
                        <Zap className="h-5 w-5" />
                      </div>
                      <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Total Impact</span>
                    </div>
                    <div>
                      <div className="flex items-end gap-2 mb-1">
                        <span className="text-3xl font-bold">{profile.total_analyses}</span>
                        <span className="text-muted-foreground mb-1 font-medium">analyses completed</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Credits Balance */}
                <div className="surface p-8 space-y-6 bg-gradient-to-br from-card to-primary/5">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <h2 className="text-xl font-bold">Credits Balance</h2>
                      <p className="text-sm text-muted-foreground font-medium">Pre-paid credits for premium analyses</p>
                    </div>
                    <Link href="/pricing" className="btn btn-primary h-11 px-6 rounded-full shadow-lg shadow-primary/20 gap-2 font-semibold transition-all hover:scale-105">
                      Top up <ArrowUpRight className="h-4 w-4" />
                    </Link>
                  </div>

                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="p-4 bg-background/50 border rounded-2xl text-center space-y-1 backdrop-blur-sm">
                       <p className="text-2xl font-semibold">{credits?.credits ?? 0}</p>
                       <p className="text-[10px] uppercase font-semibold text-muted-foreground tracking-[0.22em]">Available</p>
                    </div>
                    <div className="p-4 bg-background/50 border rounded-2xl text-center space-y-1 text-muted-foreground backdrop-blur-sm">
                       <p className="text-2xl font-semibold">{credits?.total_purchased ?? 0}</p>
                       <p className="text-[10px] uppercase font-semibold tracking-[0.22em]">Purchased</p>
                    </div>
                    <div className="p-4 bg-background/50 border rounded-2xl text-center space-y-1 text-muted-foreground backdrop-blur-sm">
                       <p className="text-2xl font-semibold">{credits?.total_used ?? 0}</p>
                       <p className="text-[10px] uppercase font-semibold tracking-[0.22em]">Lifetime Use</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-8">
                {/* Quick Actions */}
                <div className="surface p-6 space-y-4">
                  <h3 className="text-[10px] font-semibold uppercase tracking-[0.22em] text-muted-foreground mb-2">Quick Settings</h3>
                  <div className="space-y-1">
                     <SettingsLink icon={<UserIcon className="h-4 w-4" />} label="Update Profile" onClick={() => setActiveTab("profile")} />
                     <SettingsLink icon={<Lock className="h-4 w-4" />} label="Security & Access" onClick={() => setActiveTab("security")} />
                     <SettingsLink icon={<CreditCard className="h-4 w-4" />} label="Manage Billing" onClick={() => setActiveTab("billing")} />
                     {profile.role === 'admin' && (
                       <Link href="/admin" className="flex items-center justify-between p-3 rounded-xl hover:bg-primary/5 transition-all group">
                         <div className="flex items-center gap-3">
                           <Shield className="h-4 w-4 text-primary" />
                           <span className="text-sm font-bold text-foreground">Admin Dashboard</span>
                         </div>
                         <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                       </Link>
                     )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === "profile" && (
            <motion.div 
              key="profile"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="max-w-2xl mx-auto w-full"
            >
              <div className="surface p-8 space-y-8">
                <div className="border-b border-border/50 pb-6">
                  <h2 className="text-2xl font-semibold">Profile Settings</h2>
                  <p className="text-sm text-muted-foreground font-medium">Update your account identity and email address.</p>
                </div>

                <form onSubmit={handleUpdateProfile} className="space-y-6">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">Email Address</label>
                    <div className="relative">
                      <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <input 
                        type="email" 
                        value={emailInput}
                        onChange={(e) => setEmailInput(e.target.value)}
                        className="input-field pl-12 h-12 font-medium"
                        placeholder="your@email.com"
                        required
                      />
                    </div>
                    <p className="text-[10px] text-muted-foreground font-medium">This email will be used for all billing and security notifications.</p>
                  </div>

                  <div className="pt-4">
                    <button 
                      type="submit" 
                      disabled={isUpdating || emailInput === profile.email}
                      className="btn btn-primary w-full h-12 rounded-full font-semibold gap-2 shadow-lg shadow-primary/20 disabled:opacity-50 disabled:grayscale transition-all"
                    >
                      {isUpdating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                      Save Profile Changes
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          )}

          {activeTab === "security" && (
            <motion.div 
              key="security"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-8 max-w-4xl mx-auto w-full"
            >
              {/* 2FA Section */}
              <div className="surface p-8 space-y-6">
                <div className="flex items-center justify-between border-b border-border/50 pb-6">
                  <div className="space-y-1">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      <ShieldCheck className="h-5 w-5 text-primary" />
                      Two-Factor Authentication
                    </h2>
                    <p className="text-sm text-muted-foreground font-medium">Add an extra layer of security to your account.</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-[10px] font-semibold uppercase tracking-[0.22em] border ${is2faEnabled ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-muted text-muted-foreground border-border/50'}`}>
                    {is2faEnabled ? "PROTECTED" : "NOT ENABLED"}
                  </div>
                </div>

                <div className="flex flex-col md:flex-row items-center gap-6 p-6 rounded-[1.5rem] bg-muted/20 border border-dashed border-border/50">
                   <div className="h-16 w-16 rounded-[1.5rem] bg-background border flex items-center justify-center text-primary shadow-sm">
                      <Smartphone className="h-8 w-8" />
                   </div>
                   <div className="flex-1 space-y-1 text-center md:text-left">
                      <h3 className="font-bold">Authenticator App</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed max-w-md">Use apps like Google Authenticator or 1Password to generate secure verification codes.</p>
                   </div>
                   <button 
                    onClick={() => toast.info("2FA setup will be available after admin approval")}
                    className={`btn ${is2faEnabled ? 'btn-outline' : 'btn-primary'} rounded-full font-semibold px-6 h-11`}
                   >
                      {is2faEnabled ? "Disable 2FA" : "Enable 2FA"}
                   </button>
                </div>
              </div>

              {/* Active Sessions */}
              <div className="surface p-8 space-y-6">
                <div className="border-b border-border/50 pb-6">
                  <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Monitor className="h-5 w-5 text-primary" />
                    Active Access Nodes
                  </h2>
                  <p className="text-sm text-muted-foreground font-medium">Devices currently authorized to access your neural cluster.</p>
                </div>

                <div className="space-y-4">
                  {sessions.length > 0 ? (
                    sessions.map((session) => (
                      <div key={session.id} className="flex items-center justify-between p-4 rounded-2xl bg-muted/20 border border-border/50 hover:bg-muted/30 transition-all group">
                        <div className="flex items-center gap-4">
                          <div className="h-10 w-10 rounded-xl bg-background border flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors shadow-sm">
                             {session.user_agent.toLowerCase().includes('mobile') ? <Smartphone className="h-5 w-5" /> : <Monitor className="h-5 w-5" />}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-bold text-foreground truncate w-40 sm:w-auto">
                                {session.user_agent.split('(')[0] || "Unknown Browser"}
                              </p>
                              {session.is_current && (
                                <span className="bg-emerald-500/10 text-emerald-500 text-[8px] font-semibold px-1.5 py-0.5 rounded uppercase tracking-tighter shadow-sm border border-emerald-500/20">CURRENT</span>
                              )}
                            </div>
                            <div className="flex items-center gap-3 text-[10px] text-muted-foreground font-bold uppercase tracking-tighter">
                               <span className="flex items-center gap-1"><Globe className="h-3 w-3" /> {session.ip_address}</span>
                               <span className="flex items-center gap-1"><History className="h-3 w-3" /> Active {formatDistanceToNow(new Date(session.last_active), { addSuffix: true })}</span>
                            </div>
                          </div>
                        </div>
                        {!session.is_current && (
                          <button 
                            onClick={() => handleRevokeSession(session.id)}
                            className="p-2.5 rounded-xl hover:bg-red-500/10 text-muted-foreground hover:text-red-500 transition-all opacity-0 group-hover:opacity-100"
                            title="Revoke Access"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="py-10 text-center">
                       <Loader2 className="h-6 w-6 animate-spin mx-auto text-muted-foreground mb-4" />
                       <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Retrieving node data...</p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === "billing" && (
            <motion.div 
              key="billing"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-8 max-w-4xl mx-auto w-full"
            >
              <div className="surface p-8 space-y-8">
                <div className="flex items-center justify-between border-b border-border/50 pb-6">
                  <div className="space-y-1">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      <CreditCard className="h-5 w-5 text-primary" />
                      Plan & Billing
                    </h2>
                    <p className="text-sm text-muted-foreground font-medium">Manage your subscription tier and payment history.</p>
                  </div>
                  <Link href="/pricing" className="btn btn-primary h-10 px-5 rounded-full text-xs font-semibold shadow-lg shadow-primary/20">
                    Switch Plan
                  </Link>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                   <div className="p-6 rounded-[1.5rem] gradient-premium text-primary-foreground shadow-xl shadow-primary/20">
                      <div className="flex justify-between items-start mb-8">
                         <div className="space-y-1">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] opacity-70">Current Deployment</p>
                            <h3 className="text-2xl font-semibold capitalize">{profile.plan} Node</h3>
                         </div>
                         <Shield className="h-8 w-8 opacity-20" />
                      </div>
                      <div className="flex justify-between items-end">
                         <div className="space-y-1">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] opacity-70">Daily Analysis Cap</p>
                            <p className="text-lg font-semibold">{profile.daily_limit} Ops/Day</p>
                         </div>
                         <div className="text-right">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] opacity-70">Next Cycle</p>
                            <p className="text-xs font-semibold">{format(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), "MMM dd, yyyy")}</p>
                         </div>
                      </div>
                   </div>

                   <div className="p-6 rounded-[1.5rem] border-2 border-dashed border-border/50 flex flex-col justify-center items-center text-center space-y-4 group hover:border-primary/30 transition-all cursor-pointer">
                      <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-all">
                         <ArrowUpRight className="h-6 w-6" />
                      </div>
                      <div>
                         <h4 className="font-bold">Upgrade Deployment</h4>
                         <p className="text-xs text-muted-foreground leading-relaxed max-w-[180px]">Need more compute power? Scale your node clusters instantly.</p>
                      </div>
                   </div>
                </div>
              </div>

              {/* Transaction Archive */}
              <div className="surface p-8 space-y-6 overflow-hidden">
                <div className="border-b border-border/50 pb-6">
                  <h2 className="text-xl font-semibold flex items-center gap-2">
                    <History className="h-5 w-5 text-primary" />
                    Transaction Archive
                  </h2>
                  <p className="text-sm text-muted-foreground font-medium">Historical record of all resource purchases and node renewals.</p>
                </div>

                <div className="overflow-x-auto -mx-8 px-8">
                  <table className="w-full text-left">
                    <thead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground border-b border-border/50 bg-muted/10">
                      <tr>
                        <th className="px-4 py-3">Event</th>
                        <th className="px-4 py-3">Timestamp</th>
                        <th className="px-4 py-3">Vector</th>
                        <th className="px-4 py-3 text-right">Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {creditHistory.map((tx) => (
                        <tr key={tx.id} className="text-sm hover:bg-muted/30 transition-colors group">
                          <td className="px-4 py-4 font-bold capitalize">{tx.description || tx.transaction_type}</td>
                          <td className="px-4 py-4 text-muted-foreground text-xs">{format(new Date(tx.created_at), "MMM dd, HH:mm")}</td>
                          <td className="px-4 py-4">
                             <span className="px-2 py-0.5 rounded text-[8px] font-black uppercase border border-border/50 bg-background">{tx.package_type || "System"}</span>
                          </td>
                          <td className={`px-4 py-4 text-right font-black ${tx.credits > 0 ? 'text-emerald-500' : 'text-foreground'}`}>
                             {tx.credits > 0 ? '+' : ''}{tx.credits}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    
    
  )
}

function TabButton({ active, onClick, label, icon }: { active: boolean, onClick: () => void, label: string, icon: ReactNode }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all ${
        active 
          ? "bg-background text-primary shadow-sm" 
          : "text-muted-foreground hover:text-foreground hover:bg-background/50"
      }`}
    >
      {icon}
      {label}
    </button>
  )
}

function SettingsLink({ icon, label, onClick }: { icon: ReactNode, label: string, onClick?: () => void }) {
  return (
    <button 
      onClick={onClick}
      className="flex items-center justify-between w-full p-3 rounded-xl hover:bg-muted transition-all group text-left"
    >
      <div className="flex items-center gap-3">
        <span className="text-muted-foreground group-hover:text-primary transition-colors">{icon}</span>
        <span className="text-sm font-bold text-muted-foreground group-hover:text-foreground transition-colors">{label}</span>
      </div>
      <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
    </button>
  )
}
