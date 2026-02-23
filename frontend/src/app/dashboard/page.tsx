"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Activity, Clock, ShieldCheck, TrendingUp, ChevronRight, PlayCircle, FileText, AlertCircle } from "lucide-react"
import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import { SiteShell } from "@/components/SiteShell"
import { StatCard } from "@/components/StatCard"
import { Skeleton, SkeletonTable } from "@/components/ui/Skeleton"
import { useAuth } from "@/contexts/auth-context"
import { fetchAnalysisHistory } from "@/lib/api-client"
import type { AnalysisHistoryItem } from "@/types/api"

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
  const { user, loading: authLoading } = useAuth()
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadDashboardData() {
      if (!user) return
      
      try {
        const data = await fetchAnalysisHistory({ limit: 5 })
        setHistory(data)
      } catch (error) {
        console.error("Failed to load dashboard data:", error)
      } finally {
        setLoading(false)
      }
    }

    if (!authLoading && user) {
      loadDashboardData()
    }
  }, [user, authLoading])

  if (authLoading || (loading && !user)) {
    return (
      <SiteShell>
        <section className="container mx-auto max-w-6xl px-4 section space-y-10">
          <div className="space-y-4">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-10 w-48" />
            <Skeleton className="h-4 w-96" />
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
          <div className="card p-6">
            <SkeletonTable rows={5} />
          </div>
        </section>
      </SiteShell>
    )
  }

  const avgConfidence = history.length > 0 
    ? history.reduce((acc, curr) => acc + (curr.confidence_score || 0), 0) / history.length
    : 0

  return (
    <SiteShell>
      <section className="container mx-auto max-w-6xl px-4 section space-y-10">
        {/* Header */}
        <motion.div
          className="flex flex-col gap-3"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.p
            className="text-sm text-muted-foreground"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            Overview
          </motion.p>
          <motion.h1
            className="text-3xl font-semibold"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            Dashboard
          </motion.h1>
          <motion.p
            className="text-sm text-muted-foreground max-w-2xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Welcome back, {user?.email}. Track your video analysis history and platform usage.
          </motion.p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-4"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <StatCard
            label="Total analyses"
            value={user?.total_analyses.toString() || "0"}
            helper="All time"
            icon={<TrendingUp className="h-5 w-5" />}
          />
          <StatCard
            label="Daily Usage"
            value={`${user?.daily_used || 0}/${user?.daily_limit || 0}`}
            helper="Resets daily"
            icon={<Activity className="h-5 w-5" />}
          />
          <StatCard
            label="Avg. confidence"
            value={avgConfidence.toFixed(2)}
            helper="Latest analyses"
            icon={<ShieldCheck className="h-5 w-5" />}
          />
          <StatCard
            label="Current Plan"
            value={user?.plan.toUpperCase() || "FREE"}
            helper={user?.role === "admin" ? "Administrator" : "Standard user"}
            icon={<Clock className="h-5 w-5" />}
          />
        </motion.div>

        {/* Recent Analyses */}
        <div className="grid gap-6 lg:grid-cols-3">
          <motion.div
            className="lg:col-span-2 card p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Recent analyses</h2>
              <Link href="/history" className="text-sm text-primary hover:underline flex items-center gap-1">
                View all <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
            
            {loading ? (
              <SkeletonTable rows={3} />
            ) : history.length > 0 ? (
              <div className="divide-y divide-border">
                {history.map((analysis) => (
                  <div
                    key={analysis.id}
                    className="flex flex-col md:flex-row md:items-center md:justify-between py-4 group"
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1 p-2 rounded-lg bg-primary/10 text-primary">
                        <PlayCircle className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium line-clamp-1">{analysis.video_id || "Untitled Analysis"}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                    <div className="mt-3 md:mt-0 flex items-center gap-4">
                      <span className={`badge ${
                        analysis.status === "completed" ? "badge-success" : 
                        analysis.status === "failed" ? "badge-destructive" : ""
                      }`}>
                        {analysis.status}
                      </span>
                      {analysis.confidence_score !== null && (
                        <span className="text-sm font-medium">
                          {(analysis.confidence_score * 100).toFixed(0)}%
                        </span>
                      )}
                      <Link 
                        href={`/analyze/result?taskId=${analysis.task_id}`}
                        className="p-1 hover:bg-muted rounded"
                      >
                        <ChevronRight className="h-5 w-5 text-muted-foreground" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center space-y-3">
                <FileText className="h-12 w-12 text-muted-foreground/30 mx-auto" />
                <p className="text-muted-foreground">No analyses found yet.</p>
                <Link href="/analyze" className="btn btn-primary btn-sm">
                  Start your first analysis
                </Link>
              </div>
            )}
          </motion.div>

          <motion.div
            className="space-y-6"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="card p-6 bg-primary text-primary-foreground">
              <h3 className="text-lg font-semibold mb-2">Upgrade to Pro</h3>
              <p className="text-sm opacity-90 mb-4">
                Get higher daily limits, faster processing, and detailed PDF reports.
              </p>
              <Link href="/pricing" className="btn bg-white text-primary hover:bg-white/90 w-full">
                Upgrade Now
              </Link>
            </div>

            <div className="card p-6">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
                Platform Status
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    Analysis Engine
                  </span>
                  <span className="text-muted-foreground">Operational</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    API Gateway
                  </span>
                  <span className="text-muted-foreground">Operational</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-yellow-500" />
                    Report Generation
                  </span>
                  <span className="text-muted-foreground">Delayed</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </SiteShell>
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
