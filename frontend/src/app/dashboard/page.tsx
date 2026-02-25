"use client"

import { useEffect, useState, useMemo } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Activity, Clock, ShieldCheck, TrendingUp, History, 
  ArrowRight, ExternalLink, RefreshCw, FileText, Zap, Settings 
} from "lucide-react"
import Link from "next/link"
import { StatCard } from "@/components/StatCard"
import { Skeleton, SkeletonTable } from "@/components/ui/Skeleton"
import { fetchAnalysisHistory } from "@/lib/api-client"
import type { AnalysisHistoryItem } from "@/types/api"
import { toast, Toaster } from "sonner"
import { formatDistanceToNow } from "date-fns"
import { useAuth } from "@/contexts/auth-context"

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4 },
  },
}

export default function DashboardPage() {
  const { user, loading: authLoading, updateMockUser } = useAuth()
  const router = useRouter()
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const loadData = async () => {
    if (!user) return
    setIsLoading(true)
    try {
      const data = await fetchAnalysisHistory({ limit: 5 })
      setHistory(data)
    } catch (error) {
      console.error("Failed to fetch dashboard history:", error)
      // Fallback to empty history if API fails
      setHistory([])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      loadData()
    }
  }, [user])

  const stats = useMemo(() => {
    if (history.length === 0) {
      return {
        total: 128, // Mock default
        avgScore: 0.78,
        activeTasks: 3,
        avgTime: "47s"
      }
    }

    const completed = history.filter(h => h.status === 'completed')
    const rawAvgScore = completed.length > 0 
      ? completed.reduce((acc, curr) => acc + (curr.confidence_score || 0), 0) / completed.length 
      : 0.78

    // Defensive check to ensure rawAvgScore is a number
    const finalAvgScore = typeof rawAvgScore === 'number' && !isNaN(rawAvgScore) ? rawAvgScore : 0.78

    return {
      total: history.length,
      avgScore: Number(finalAvgScore.toFixed(2)),
      activeTasks: history.filter(h => h.status === 'processing' || h.status === 'queued').length,
      avgTime: "42s" // Still mock for now as we don't have duration in history yet
    }
  }, [history])

  if (authLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Activity className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="space-y-10">
      <Toaster position="top-right" richColors />
      
      {/* DEV SANDBOX - Only in Development */}
      {process.env.NODE_ENV === 'development' && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20 relative overflow-hidden group"
        >
          <div className="absolute top-0 right-0 p-2 bg-amber-500 text-amber-950 text-[10px] font-black uppercase tracking-widest">
            Dev Sandbox
          </div>
          <div className="flex flex-wrap items-center gap-6">
            <div className="space-y-1">
              <p className="text-[10px] font-black uppercase tracking-widest text-amber-500/60">Current Plan</p>
              <div className="flex gap-2">
                {['starter', 'pro', 'business', 'enterprise'].map((p) => (
                  <button
                    key={p}
                    onClick={() => updateMockUser({ plan: p })}
                    className={`px-3 py-1 rounded-lg text-xs font-bold capitalize transition-all ${
                      user.plan === p ? 'bg-amber-500 text-amber-950' : 'bg-amber-500/10 text-amber-500 hover:bg-amber-500/20'
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-[10px] font-black uppercase tracking-widest text-amber-500/60">Role</p>
              <div className="flex gap-2">
                {['user', 'admin'].map((r) => (
                  <button
                    key={r}
                    onClick={() => updateMockUser({ role: r })}
                    className={`px-3 py-1 rounded-lg text-xs font-bold capitalize transition-all ${
                      user.role === r ? 'bg-amber-500 text-amber-950' : 'bg-amber-500/10 text-amber-500 hover:bg-amber-500/20'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            <div className="ml-auto flex items-center gap-4">
              <div className="text-right">
                <p className="text-[10px] font-black uppercase tracking-widest text-amber-500/60">Simulated User</p>
                <p className="text-sm font-bold truncate max-w-[150px]">{user.email}</p>
              </div>
              <div className="h-10 w-10 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-500">
                <Settings className="h-5 w-5 animate-spin-slow" />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <motion.div
          className="flex flex-col gap-3"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.p
            className="text-xs font-bold text-primary uppercase tracking-widest"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            Control Center
          </motion.p>
          <motion.h1
            className="text-4xl font-bold tracking-tight"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            System Dashboard
          </motion.h1>
          <motion.p
            className="text-sm text-muted-foreground max-w-2xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Real-time compliance monitoring, signal strength analysis, and historical oversight of your content pipeline.
          </motion.p>
        </motion.div>

        <motion.div
          className="flex gap-2"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
           <button 
            onClick={loadData}
            className="btn btn-outline h-10 w-10 p-0 rounded-xl"
            title="Refresh data"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <Link href="/analyze" className="btn btn-primary px-5 rounded-xl gap-2 shadow-lg shadow-primary/20">
            <Activity className="h-4 w-4" />
            New Analysis
          </Link>
        </motion.div>
      </div>

      {/* Stats Grid */}
      <motion.div
        className="grid gap-6 md:grid-cols-2 lg:grid-cols-4"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <StatCard
          label="Total analyses"
          value={stats.total}
          helper="Historical volume"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <StatCard
          label="Avg. confidence"
          value={stats.avgScore}
          helper="Signal strength"
          icon={<ShieldCheck className="h-5 w-5" />}
        />
        <StatCard
          label="Avg. processing"
          value={stats.avgTime}
          helper="Throughput speed"
          icon={<Clock className="h-5 w-5" />}
        />
        <StatCard
          label="Active tasks"
          value={stats.activeTasks}
          helper="Current pipeline"
          icon={<Activity className="h-5 w-5" />}
        />
      </motion.div>

      {/* Main Content Area */}
      <div className="grid gap-8">
        {/* Recent Analyses Table - Expanded */}
        <motion.div
          className="card p-8 overflow-hidden relative shadow-2xl shadow-black/5 border-border/40"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 text-primary">
                <History className="h-5 w-5" />
              </div>
              <h2 className="text-2xl font-black tracking-tight">System Activity</h2>
            </div>
            <Link
              href="/history"
              className="btn btn-ghost btn-sm gap-2 text-primary font-bold hover:bg-primary/5"
            >
              Access Archive
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
          
          <div className="divide-y divide-border/40">
            {isLoading ? (
              <div className="space-y-6 py-2">
                {[1, 2, 3, 4, 5].map(i => (
                  <div key={i} className="flex items-center justify-between py-5">
                    <div className="flex items-center gap-4">
                      <Skeleton className="h-12 w-12 rounded-xl" />
                      <div className="space-y-2">
                        <Skeleton className="h-5 w-64" />
                        <Skeleton className="h-3 w-32" />
                      </div>
                    </div>
                    <Skeleton className="h-10 w-28 rounded-xl" />
                  </div>
                ))}
              </div>
            ) : history.length > 0 ? (
              history.map((analysis, index) => (
                <motion.div
                  key={analysis.task_id}
                  className="flex items-center justify-between py-5 hover:bg-muted/30 -mx-8 px-8 transition-all group cursor-pointer"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <div className="flex-1 min-w-0 flex items-center gap-5">
                    <div className={`h-12 w-12 rounded-2xl flex items-center justify-center border border-border/50 bg-background shadow-sm ${
                      analysis.status === 'completed' ? 'text-emerald-500' : 
                      analysis.status === 'failed' ? 'text-red-500' : 'text-primary'
                    }`}>
                      {analysis.status === 'completed' ? <ShieldCheck className="h-6 w-6" /> : <Activity className="h-6 w-6" />}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-bold truncate text-base">
                          {analysis.source_type.toUpperCase()} NODE • {analysis.task_id.slice(0, 8)}
                        </p>
                        {analysis.has_advertising && (
                           <span className="text-[9px] font-black bg-red-500/10 text-red-500 px-2 py-0.5 rounded-full border border-red-500/20 uppercase tracking-widest shadow-sm">Ad Detected</span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center gap-2 font-medium uppercase tracking-tighter">
                        <Clock className="h-3 w-3" />
                        Processed {formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-8">
                    <div className="text-right hidden sm:block">
                      <p className={`text-lg font-black ${analysis.confidence_score && analysis.confidence_score > 0.7 ? 'text-emerald-500' : 'text-primary'}`}>
                        {analysis.confidence_score ? (analysis.confidence_score * 100).toFixed(0) + '%' : '--'}
                      </p>
                      <p className="text-[9px] text-muted-foreground uppercase font-black tracking-widest opacity-60">Confidence</p>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all ${
                        analysis.status === 'completed' ? 'bg-emerald-500/5 text-emerald-500 border-emerald-500/20' :
                        analysis.status === 'failed' ? 'bg-red-500/5 text-red-500 border-red-500/20' :
                        'bg-primary/5 text-primary border-primary/20 animate-pulse'
                      }`}>
                        {analysis.status}
                      </span>
                      <div className="h-10 w-10 rounded-xl bg-muted/50 flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all">
                        <ExternalLink className="h-4 w-4" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="py-24 text-center space-y-6">
                <div className="bg-muted h-24 w-24 rounded-[2.5rem] flex items-center justify-center mx-auto mb-4 border-2 border-dashed border-border/50 rotate-12 transition-transform hover:rotate-0">
                  <History className="h-10 w-10 text-muted-foreground/40" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-black">No Operations Logged</h3>
                  <p className="text-sm text-muted-foreground max-w-xs mx-auto font-medium">
                    Initialize your first content analysis to see neural network results here.
                  </p>
                </div>
                <Link href="/analyze" className="btn btn-primary h-12 px-8 rounded-2xl font-bold uppercase tracking-widest text-xs shadow-xl shadow-primary/20">
                  Execute Analysis
                </Link>
              </div>
            )}
          </div>
        </motion.div>

        {/* Quick Pipeline Status - Horizontal */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
           <StatusCard label="Vision OCR" status="operational" />
           <StatusCard label="Audio Sync" status="operational" />
           <StatusCard label="Logo API" status="operational" />
           <StatusCard label="LLM Reasoning" status="degraded" />
        </div>
      </div>
    </div>
  )
}

function StatusCard({ label, status }: { label: string, status: 'operational' | 'degraded' | 'down' }) {
  const colors = {
    operational: 'bg-emerald-500 text-emerald-500',
    degraded: 'bg-amber-500 text-amber-500',
    down: 'bg-red-500 text-red-500'
  }
  
  return (
    <div className="card p-4 flex flex-col gap-3 border-border/40 shadow-sm">
      <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{label}</p>
      <div className="flex items-center justify-between">
        <span className={`text-[10px] font-black uppercase tracking-tighter ${colors[status].split(' ')[1]}`}>{status}</span>
        <div className={`h-2 w-2 rounded-full ${colors[status].split(' ')[0]} shadow-lg animate-pulse`} />
      </div>
    </div>
  )
}

function StatusItem({ label, status }: { label: string, status: 'operational' | 'degraded' | 'down' }) {
  const colors = {
    operational: 'bg-emerald-500',
    degraded: 'bg-amber-500',
    down: 'bg-red-500'
  }
  
  return (
    <div className="flex items-center justify-between group">
      <span className="text-sm font-bold text-muted-foreground group-hover:text-foreground transition-colors">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-[10px] uppercase font-bold text-muted-foreground/60">{status}</span>
        <div className={`h-2.5 w-2.5 rounded-full ${colors[status]} shadow-[0_0_8px_rgba(0,0,0,0.1)] group-hover:scale-125 transition-transform`} />
      </div>
    </div>
  )
}

function QuickLink({ href, label, icon }: { href: string, label: string, icon?: ReactNode }) {
  return (
    <Link 
      href={href} 
      className="flex items-center justify-center gap-2 text-xs font-bold p-3 rounded-xl bg-muted/50 hover:bg-primary/10 hover:text-primary transition-all text-center border border-transparent hover:border-primary/20"
    >
      {icon}
      {label}
    </Link>
  )
}

function SkeletonCard() {
  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-8 rounded-lg" />
      </div>
      <Skeleton className="h-8 w-32" />
      <Skeleton className="h-3 w-40" />
    </div>
  )
}
