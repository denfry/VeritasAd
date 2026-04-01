"use client"

import { useState, useEffect, useCallback } from "react"
import { motion } from "framer-motion"

import {
  Key,
  Copy,
  Eye,
  EyeOff,
  BarChart3,
  Clock,
  Shield,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  Loader2,
} from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { getApiKey, regenerateApiKey, getApiKeyStats } from "@/lib/api-client"
import { useAuth } from "@/contexts/auth-context"

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
}

export default function ApiSettingsPage() {
  const { user } = useAuth()
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [hasKey, setHasKey] = useState(false)
  const [showKey, setShowKey] = useState(false)
  const [stats, setStats] = useState<{
    total_requests: number
    successful_requests: number
    daily_limit: number
    daily_used: number
    daily_remaining: number
  } | null>(null)
  const [loading, setLoading] = useState(true)

  const loadData = useCallback(async () => {
    try {
      const [keyData, statsData] = await Promise.all([
        getApiKey(),
        getApiKeyStats(),
      ])
      setHasKey(keyData.has_key)
      setStats(statsData)
    } catch {
      toast.error("Failed to load API key data")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleRegenerate = async () => {
    try {
      const result = await regenerateApiKey()
      setApiKey(result.api_key)
      setHasKey(true)
      setShowKey(true)
      toast.success("API key regenerated. Store it securely!")
    } catch {
      toast.error("Failed to regenerate API key")
    }
  }

  const handleCopy = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey)
      toast.success("API key copied to clipboard")
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  const maskedKey = apiKey
    ? apiKey.length > 12
      ? `${apiKey.slice(0, 8)}••••••••••••••••${apiKey.slice(-4)}`
      : "••••••••••••••••"
    : ""

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={container}
      className="space-y-6"
    >
      <motion.div variants={item}>
        <h1 className="text-3xl font-bold tracking-tight">API Keys</h1>
        <p className="text-muted-foreground mt-1">Manage your API key and monitor usage.</p>
      </motion.div>

      <motion.div variants={item} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<Key className="h-5 w-5" />}
          label="API Key"
          value={hasKey ? "Active" : "Not set"}
          color={hasKey ? "text-emerald-500" : "text-amber-500"}
        />
        <StatCard
          icon={<BarChart3 className="h-5 w-5" />}
          label="Total Requests"
          value={stats?.total_requests.toLocaleString() ?? "0"}
          color="text-cyan-500"
        />
        <StatCard
          icon={<Clock className="h-5 w-5" />}
          label="Daily Used"
          value={`${stats?.daily_used ?? 0} / ${stats?.daily_limit ?? 0}`}
          color="text-amber-500"
        />
        <StatCard
          icon={<Shield className="h-5 w-5" />}
          label="Daily Remaining"
          value={stats?.daily_remaining.toLocaleString() ?? "0"}
          color="text-emerald-500"
        />
      </motion.div>

      <motion.div variants={item} className="rounded-2xl border bg-card/60 backdrop-blur-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold">Your API Key</h2>
            <p className="text-muted-foreground text-sm">Use this key to authenticate API requests.</p>
          </div>
          <button
            onClick={handleRegenerate}
            className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            <RefreshCw className="h-4 w-4" />
            Regenerate
          </button>
        </div>

        {hasKey && apiKey ? (
          <div className="flex items-center gap-3 p-4 rounded-xl bg-muted/30 border border-border/50">
            <code className="flex-1 font-mono text-sm truncate">
              {showKey ? apiKey : maskedKey}
            </code>
            <button
              onClick={() => setShowKey(!showKey)}
              className="text-muted-foreground hover:text-foreground transition-colors p-1"
            >
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
            <button
              onClick={handleCopy}
              className="text-muted-foreground hover:text-foreground transition-colors p-1"
            >
              <Copy className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3 p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
            <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0" />
            <p className="text-sm text-muted-foreground">No API key set. Click &quot;Regenerate&quot; to create one.</p>
          </div>
        )}

        {user && (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
              <span className="text-sm text-muted-foreground">Success rate</span>
              <span className="text-sm font-bold">
                {stats && stats.total_requests > 0
                  ? `${((stats.successful_requests / stats.total_requests) * 100).toFixed(0)}%`
                  : "N/A"}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
              <span className="text-sm text-muted-foreground">Plan limit</span>
              <span className="text-sm font-bold">{stats?.daily_limit ?? user.daily_limit} / day</span>
            </div>
          </div>
        )}
      </motion.div>

      <motion.div variants={item} className="rounded-2xl border bg-card/60 backdrop-blur-sm p-6">
        <h3 className="font-semibold mb-4">Documentation</h3>
        <div className="space-y-3">
          <DocLink label="API Reference" href="/docs" description="Complete endpoint documentation" />
          <DocLink label="Authentication Guide" href="/docs" description="How to use API keys" />
          <DocLink label="Rate Limiting" href="/docs" description="Understanding rate limits" />
        </div>
      </motion.div>
    </motion.div>
  )
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: string
  color: string
}) {
  return (
    <div className="rounded-2xl border bg-card/60 backdrop-blur-sm p-4">
      <div className="flex items-center gap-3">
        <div className={cn("p-2 rounded-lg bg-muted/50", color)}>{icon}</div>
        <div>
          <p className="text-muted-foreground text-xs">{label}</p>
          <p className="text-xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  )
}

function DocLink({
  label,
  href,
  description,
}: {
  label: string
  href: string
  description: string
}) {
  return (
    <a
      href={href}
      className="flex items-center justify-between rounded-xl border bg-muted/20 p-3 transition-colors hover:bg-muted/40"
    >
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-muted-foreground text-xs">{description}</p>
      </div>
      <ExternalLink className="h-4 w-4 text-muted-foreground" />
    </a>
  )
}
