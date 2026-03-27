"use client"

import { useCallback, useEffect, useState, useMemo } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { 
  Activity, Clock, ShieldCheck, TrendingUp, History, 
  ArrowRight, RefreshCw, BarChart3, CheckCircle2, XCircle,
  Zap, FileVideo
} from "lucide-react"
import Link from "next/link"
import { Skeleton } from "@/components/ui/Skeleton"
import { StatCard } from "@/components/StatCard"
import { fetchAnalysisHistory } from "@/lib/api-client"
import type { AnalysisHistoryItem } from "@/types/api"
import { Toaster } from "sonner"
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

const PAGE_SIZE = 5

export default function DashboardPage() {
  const { user, loading: authLoading, updateMockUser } = useAuth()
  const router = useRouter()
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)

  const loadData = useCallback(async (page: number = 0) => {
    if (!user) return
    setIsLoading(true)
    setLoadError(null)
    try {
      const data = await fetchAnalysisHistory({ limit: PAGE_SIZE, offset: page * PAGE_SIZE })
      if (page === 0) {
        setHistory(data)
      } else {
        setHistory(prev => [...prev, ...data])
      }
      setHasMore(data.length === PAGE_SIZE)
    } catch (error) {
      console.error("Failed to fetch dashboard history:", error)
      if (page === 0) setHistory([])
      setLoadError(error instanceof Error ? error.message : "Failed to load dashboard data")
    } finally {
      setIsLoading(false)
    }
  }, [user])

  const loadMore = useCallback(() => {
    if (!isLoading && hasMore) {
      const nextPage = currentPage + 1
      setCurrentPage(nextPage)
      loadData(nextPage)
    }
  }, [isLoading, hasMore, currentPage, loadData])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      loadData(0)
    }
  }, [user, loadData])

  const stats = useMemo(() => {
    const completed = history.filter(h => h.status === 'completed')
    const rawAvgScore = completed.length > 0 
      ? completed.reduce((acc, curr) => acc + (curr.confidence_score || 0), 0) / completed.length 
      : 0

    const finalAvgScore = typeof rawAvgScore === 'number' && !isNaN(rawAvgScore) ? rawAvgScore : 0

    const dailyUsed = user?.daily_used || 0
    const dailyLimit = user?.daily_limit || 100
    const dailyPercentage = dailyLimit > 0 ? (dailyUsed / dailyLimit) * 100 : 0

    return {
      total: history.length,
      avgScore: Number(finalAvgScore.toFixed(2)),
      activeTasks: history.filter(h => h.status === 'processing' || h.status === 'queued').length,
      avgTime: "45s",
      dailyUsed,
      dailyLimit,
      dailyPercentage,
      totalAnalyses: user?.total_analyses || 0
    }
  }, [history, user])

  if (authLoading) {
    return (
      <div className="space-y-8 p-6">
        {/* Header skeleton */}
        <div className="space-y-4">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-5 w-80" />
        </div>
        
        {/* Stats Grid skeleton */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="card p-5 space-y-3">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-3 w-20" />
            </div>
          ))}
        </div>
        
        {/* Pipeline skeleton */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="card p-4 space-y-2">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-3 w-20" />
            </div>
          ))}
        </div>
        
        {/* Recent Analyses skeleton */}
        <div className="card overflow-hidden">
          <div className="p-5 border-b">
            <Skeleton className="h-6 w-36" />
          </div>
          <div className="p-6 space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex items-center gap-4">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!user) return null

  if (loadError && history.length === 0) {
    return (
      <div className="space-y-6">
        <div className="card p-6 border border-red-500/20 bg-red-500/5">
          <h2 className="text-lg font-semibold">Dashboard unavailable</h2>
          <p className="mt-2 text-sm text-muted-foreground">{loadError}</p>
          <button className="btn btn-primary mt-4" onClick={() => loadData(0)}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-10">
      <Toaster position="top-right" richColors />
      
      {/* DEV SANDBOX - Only in Development */}
      {process.env.NODE_ENV === 'development' && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 px-2 py-1 bg-amber-500 text-amber-950 text-[10px] font-black uppercase">
            Dev
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex gap-2">
              {['starter', 'pro', 'business', 'enterprise'].map((p) => (
                <button
                  key={p}
                  onClick={() => updateMockUser({ plan: p })}
                  className={`px-2 py-1 rounded-md text-xs font-medium transition-all ${
                    user.plan === p ? 'bg-amber-500 text-amber-950' : 'bg-amber-500/10 text-amber-500 hover:bg-amber-500/20'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
            <span className="text-xs text-amber-500/60">{user.email}</span>
          </div>
        </motion.div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <motion.div
          className="flex flex-col gap-2"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.p
            className="text-xs font-semibold text-primary uppercase tracking-widest"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            Welcome back
          </motion.p>
          <motion.h1
            className="text-3xl font-semibold tracking-tight lg:text-4xl"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            Dashboard
          </motion.h1>
          <motion.p
            className="text-sm text-muted-foreground"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Monitor your content analysis and compliance status.
          </motion.p>
        </motion.div>

        <motion.div
          className="flex gap-2"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
           <button 
            onClick={() => loadData(0)}
            className="btn btn-outline h-10 w-10 p-0 rounded-lg"
            title="Refresh data"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <Link href="/analyze" className="btn btn-primary px-4 rounded-full gap-2">
            <BarChart3 className="h-4 w-4" />
            New Analysis
          </Link>
        </motion.div>
      </div>

      {/* Stats Grid */}
      <motion.div
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <StatCard
          label="Total analyses"
          value={stats.totalAnalyses}
          helper="All time"
          icon={<TrendingUp className="h-4 w-4" />}
        />
        <StatCard
          label="Confidence"
          value={stats.avgScore}
          helper="Avg. score"
          icon={<ShieldCheck className="h-4 w-4" />}
        />
        <StatCard
          label="Daily limit"
          value={`${stats.dailyUsed}/${stats.dailyLimit}`}
          helper={`${stats.dailyPercentage.toFixed(0)}% used`}
          icon={<Zap className="h-4 w-4" />}
          progress={stats.dailyPercentage}
        />
        <StatCard
          label="Active"
          value={stats.activeTasks}
          helper="Processing"
          icon={<Activity className="h-4 w-4" />}
        />
      </motion.div>

      {/* Pipeline Status */}
      <motion.div
        className="grid grid-cols-2 md:grid-cols-4 gap-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <PipelineCard 
          label="Video Analysis" 
          status={history.some(h => h.status === 'processing') ? 'active' : 'operational'}
          description="Content scanning"
        />
        <PipelineCard 
          label="Brand Detection" 
          status="operational"
          description="Logo recognition"
        />
        <PipelineCard 
          label="Audio Analysis" 
          status="operational"
          description="Speech recognition"
        />
        <PipelineCard 
          label="LLM Detection" 
          status={stats.avgScore > 0 ? 'operational' : 'degraded'}
          description="AI analysis"
        />
      </motion.div>

      {/* Recent Analyses */}
      <motion.div
        className="surface overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="flex items-center justify-between p-5 border-b border-border/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              <History className="h-4 w-4" />
            </div>
            <h2 className="font-semibold">Recent analyses</h2>
          </div>
          <Link
            href="/history"
            className="text-sm text-primary hover:underline flex items-center gap-1"
          >
            View all <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
        
        <div className="divide-y">
          {isLoading && history.length === 0 ? (
            <div className="p-6 space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="flex items-center gap-4">
                  <Skeleton className="h-10 w-10 rounded-lg" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                </div>
              ))}
            </div>
          ) : history.length > 0 ? (
            <>
              {history.map((analysis, index) => (
                <AnalysisRow key={analysis.task_id} analysis={analysis} index={index} />
              ))}
              
              {/* Pagination */}
              {hasMore && (
                <div className="p-4 flex justify-center border-t border-border/60">
                  <button
                    onClick={loadMore}
                    disabled={isLoading}
                    className="btn btn-outline text-sm"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                        Loading...
                      </>
                    ) : (
                      <>
                        Load more
                      </>
                    )}
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="p-12 text-center">
              <div className="w-16 h-16 rounded-2xl bg-muted/60 flex items-center justify-center mx-auto mb-4">
                <FileVideo className="h-8 w-8 text-muted-foreground/50" />
              </div>
              <h3 className="font-semibold mb-1">No analyses yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Start by analyzing your first video or post.
              </p>
              <Link href="/analyze" className="btn btn-primary text-sm">
                Start Analysis
              </Link>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}

function AnalysisRow({ analysis, index }: { analysis: AnalysisHistoryItem; index: number }) {
  const statusIcon = {
    completed: <CheckCircle2 className="h-4 w-4 text-emerald-500" />,
    failed: <XCircle className="h-4 w-4 text-red-500" />,
    processing: <Activity className="h-4 w-4 text-primary animate-pulse" />,
    queued: <Clock className="h-4 w-4 text-amber-500" />,
  }[analysis.status || 'queued']

  const statusColor = {
    completed: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20',
    failed: 'bg-red-500/10 text-red-600 border-red-500/20',
    processing: 'bg-primary/10 text-primary border-primary/20',
    queued: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
  }[analysis.status || 'queued']

  return (
    <motion.div
      className="flex items-center justify-between p-4 hover:bg-muted/25 transition-colors"
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.05 * index }}
    >
      <div className="flex items-center gap-4 min-w-0">
        <div className="h-10 w-10 rounded-xl bg-muted/60 flex items-center justify-center shrink-0">
          {statusIcon}
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-medium truncate">
              {analysis.source_type?.toUpperCase() || 'VIDEO'}
            </p>
            {analysis.has_advertising && (
            <span className="text-[10px] font-medium bg-red-500/10 text-red-500 px-2 py-0.5 rounded-full border border-red-500/20">
              Ad
            </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true })}
          </p>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="text-right hidden sm:block">
          <p className="font-semibold text-sm">
            {analysis.confidence_score ? (analysis.confidence_score * 100).toFixed(0) + '%' : '--'}
          </p>
          <p className="text-[10px] text-muted-foreground">Confidence</p>
        </div>
        
        <span className={`px-3 py-1 rounded-lg text-[10px] font-medium border ${statusColor}`}>
          {analysis.status}
        </span>
      </div>
    </motion.div>
  )
}

function PipelineCard({ 
  label, 
  status, 
  description 
}: { 
  label: string
  status: 'operational' | 'degraded' | 'active' | 'down'
  description: string
}) {
  const colors = {
    operational: 'bg-emerald-500',
    degraded: 'bg-amber-500',
    active: 'bg-primary',
    down: 'bg-red-500'
  }
  
  const labels = {
    operational: 'Operational',
    degraded: 'Degraded',
    active: 'Active',
    down: 'Down'
  }

  return (
    <div className="card p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">{label}</p>
        <div className={`h-2 w-2 rounded-full ${colors[status]} ${status === 'active' ? 'animate-pulse' : ''}`} />
      </div>
      <p className="text-xs text-muted-foreground">{description}</p>
      <p className={`text-[10px] font-medium ${colors[status].replace('bg-', 'text-')}`}>
        {labels[status]}
      </p>
    </div>
  )
}
