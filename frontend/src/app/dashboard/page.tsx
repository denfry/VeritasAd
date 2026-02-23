"use client"

import { motion } from "framer-motion"
import { Activity, Clock, ShieldCheck, TrendingUp } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"
import { StatCard } from "@/components/StatCard"
import { Skeleton, SkeletonTable } from "@/components/ui/Skeleton"

const recentAnalyses = [
  {
    id: "analysis-1",
    title: "YouTube - influencer integration",
    status: "Completed",
    score: 0.83,
    createdAt: "2 hours ago",
  },
  {
    id: "analysis-2",
    title: "Telegram post - promo code",
    status: "Completed",
    score: 0.62,
    createdAt: "Yesterday",
  },
  {
    id: "analysis-3",
    title: "Instagram story - brand mention",
    status: "Processing",
    score: 0.0,
    createdAt: "Just now",
  },
]

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
            Track analysis throughput, quality signals, and ongoing tasks across the compliance
            pipeline.
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
            label="Monthly analyses"
            value="128"
            helper="+14% vs last month"
            icon={<TrendingUp className="h-5 w-5" />}
          />
          <StatCard
            label="Avg. confidence"
            value="0.78"
            helper="Across 30 latest reports"
            icon={<ShieldCheck className="h-5 w-5" />}
          />
          <StatCard
            label="Avg. processing time"
            value="47s"
            helper="For 2-min videos"
            icon={<Clock className="h-5 w-5" />}
          />
          <StatCard
            label="Active tasks"
            value="3"
            helper="Currently running"
            icon={<Activity className="h-5 w-5" />}
          />
        </motion.div>

        {/* Recent Analyses Table */}
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <div className="flex items-center justify-between">
            <motion.h2
              className="text-xl font-semibold"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              Recent analyses
            </motion.h2>
            <motion.button
              className="text-sm text-primary hover:underline"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              View all
            </motion.button>
          </div>
          
          <motion.div
            className="mt-6 divide-y divide-border"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {recentAnalyses.map((analysis, index) => (
              <motion.div
                key={analysis.id}
                className="flex flex-col md:flex-row md:items-center md:justify-between py-4"
                variants={itemVariants}
                whileHover={{ 
                  backgroundColor: "hsl(var(--muted) / 0.3)",
                  x: 4,
                }}
                transition={{ duration: 0.2 }}
              >
                <div>
                  <p className="font-medium">{analysis.title}</p>
                  <p className="text-sm text-muted-foreground">{analysis.createdAt}</p>
                </div>
                <div className="mt-3 md:mt-0 flex items-center gap-4">
                  <motion.span
                    className="badge"
                    whileHover={{ scale: 1.05 }}
                  >
                    {analysis.status}
                  </motion.span>
                  <span className="text-sm text-muted-foreground">
                    Score: {analysis.score.toFixed(2)}
                  </span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Loading State Example (for demonstration) */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <p className="text-xs text-muted-foreground uppercase tracking-wider">
            Loading states (for reference)
          </p>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-4 w-20" />
            </div>
            <SkeletonTable rows={4} />
          </div>
        </motion.div>
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
