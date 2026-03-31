"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ThreeScene } from "@/components/three/ThreeScene"
import {
  Key,
  Plus,
  Trash2,
  Copy,
  Eye,
  EyeOff,
  BarChart3,
  Clock,
  Shield,
  ExternalLink,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

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

type ApiKey = {
  id: string
  name: string
  key: string
  createdAt: string
  lastUsed: string | null
  requests: number
  active: boolean
}

const initialKeys: ApiKey[] = [
  {
    id: "1",
    name: "Production Key",
    key: "va_prod_••••••••••••••••••••x8k2",
    createdAt: "2026-01-15T08:30:00Z",
    lastUsed: "2026-03-30T14:22:00Z",
    requests: 12847,
    active: true,
  },
  {
    id: "2",
    name: "Development Key",
    key: "va_dev_••••••••••••••••••••m3p9",
    createdAt: "2026-02-20T11:00:00Z",
    lastUsed: "2026-03-29T09:15:00Z",
    requests: 3421,
    active: true,
  },
  {
    id: "3",
    name: "Testing Key",
    key: "va_test_••••••••••••••••••••q7w1",
    createdAt: "2026-03-01T16:45:00Z",
    lastUsed: null,
    requests: 0,
    active: false,
  },
]

export default function ApiSettingsPage() {
  const [keys, setKeys] = useState<ApiKey[]>(initialKeys)
  const [showKey, setShowKey] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newKeyName, setNewKeyName] = useState("")

  const handleCopy = (key: string) => {
    navigator.clipboard.writeText(key)
    toast.success("API key copied to clipboard")
  }

  const handleRevoke = (id: string) => {
    setKeys((prev) => prev.filter((k) => k.id !== id))
    toast.success("API key revoked")
  }

  const handleCreate = () => {
    if (!newKeyName.trim()) {
      toast.error("Please enter a key name")
      return
    }
    const newKey: ApiKey = {
      id: String(Date.now()),
      name: newKeyName,
      key: `va_new_${Math.random().toString(36).slice(2, 10)}••••••••••••••••${Math.random().toString(36).slice(2, 6)}`,
      createdAt: new Date().toISOString(),
      lastUsed: null,
      requests: 0,
      active: true,
    }
    setKeys((prev) => [newKey, ...prev])
    setNewKeyName("")
    setShowCreateModal(false)
    toast.success("API key created successfully")
  }

  const totalRequests = keys.reduce((sum, k) => sum + k.requests, 0)
  const activeKeys = keys.filter((k) => k.active).length

  return (
    <ThreeScene type="neural" intensity="light">
      <motion.div
        initial="hidden"
        animate="show"
        variants={container}
        className="space-y-6"
      >
        <motion.div variants={item}>
          <h1 className="text-3xl font-bold tracking-tight">API Keys</h1>
          <p className="text-muted-foreground mt-1">Manage your API keys and monitor usage.</p>
        </motion.div>

        <motion.div variants={item} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={<Key className="h-5 w-5" />}
            label="Active Keys"
            value={String(activeKeys)}
            color="text-primary"
          />
          <StatCard
            icon={<BarChart3 className="h-5 w-5" />}
            label="Total Requests"
            value={totalRequests.toLocaleString()}
            color="text-cyan-500"
          />
          <StatCard
            icon={<Clock className="h-5 w-5" />}
            label="Rate Limit"
            value="100/min"
            color="text-amber-500"
          />
          <StatCard
            icon={<Shield className="h-5 w-5" />}
            label="Daily Quota"
            value="10,000"
            color="text-emerald-500"
          />
        </motion.div>

        <motion.div variants={item} className="rounded-2xl border bg-card/60 backdrop-blur-sm">
          <div className="flex items-center justify-between p-6 pb-4">
            <div>
              <h2 className="text-lg font-semibold">Your API Keys</h2>
              <p className="text-muted-foreground text-sm">Keys are used to authenticate API requests.</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              <Plus className="h-4 w-4" />
              Create Key
            </button>
          </div>

          <div className="px-6 pb-6">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="pb-3 text-left font-medium">Name</th>
                    <th className="pb-3 text-left font-medium">Key</th>
                    <th className="pb-3 text-left font-medium hidden md:table-cell">Requests</th>
                    <th className="pb-3 text-left font-medium hidden lg:table-cell">Last Used</th>
                    <th className="pb-3 text-left font-medium">Status</th>
                    <th className="pb-3 text-right font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {keys.map((key) => (
                    <tr key={key.id} className="group">
                      <td className="py-3 font-medium">{key.name}</td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <code className="rounded bg-muted px-2 py-0.5 text-xs font-mono">
                            {showKey === key.id ? key.key.replace(/•/g, "•") : key.key}
                          </code>
                          <button
                            onClick={() => setShowKey(showKey === key.id ? null : key.id)}
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            {showKey === key.id ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                          </button>
                          <button
                            onClick={() => handleCopy(key.key)}
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <Copy className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                      <td className="py-3 hidden md:table-cell">{key.requests.toLocaleString()}</td>
                      <td className="py-3 text-muted-foreground hidden lg:table-cell">
                        {key.lastUsed ? formatDate(key.lastUsed) : "Never"}
                      </td>
                      <td className="py-3">
                        <span
                          className={cn(
                            "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
                            key.active
                              ? "bg-emerald-500/10 text-emerald-500"
                              : "bg-muted text-muted-foreground"
                          )}
                        >
                          {key.active ? (
                            <CheckCircle2 className="h-3 w-3" />
                          ) : (
                            <AlertTriangle className="h-3 w-3" />
                          )}
                          {key.active ? "Active" : "Revoked"}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <button
                          onClick={() => handleRevoke(key.id)}
                          className="text-muted-foreground hover:text-destructive transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {keys.length === 0 && (
                <div className="py-12 text-center text-muted-foreground">
                  <Key className="h-8 w-8 mx-auto mb-3 opacity-50" />
                  <p>No API keys yet. Create one to get started.</p>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        <motion.div variants={item} className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border bg-card/60 backdrop-blur-sm p-6">
            <h3 className="font-semibold mb-2">Rate Limits</h3>
            <div className="space-y-3 text-sm">
              <RateLimitRow label="Requests per minute" value="100" />
              <RateLimitRow label="Requests per day" value="10,000" />
              <RateLimitRow label="Max payload size" value="50 MB" />
              <RateLimitRow label="Concurrent requests" value="5" />
            </div>
          </div>

          <div className="rounded-2xl border bg-card/60 backdrop-blur-sm p-6">
            <h3 className="font-semibold mb-2">Documentation</h3>
            <div className="space-y-3">
              <DocLink label="API Reference" href="#" description="Complete endpoint documentation" />
              <DocLink label="Authentication Guide" href="#" description="How to use API keys" />
              <DocLink label="Rate Limiting" href="#" description="Understanding rate limits" />
              <DocLink label="SDKs & Libraries" href="#" description="Official client libraries" />
            </div>
          </div>
        </motion.div>

        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full max-w-md rounded-2xl border bg-card p-6 shadow-xl"
            >
              <h3 className="text-lg font-semibold mb-4">Create New API Key</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Key Name</label>
                  <input
                    type="text"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="e.g. Production Key"
                    className="w-full rounded-xl border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    autoFocus
                  />
                </div>
                <div className="flex gap-3 justify-end">
                  <button
                    onClick={() => {
                      setShowCreateModal(false)
                      setNewKeyName("")
                    }}
                    className="rounded-xl border px-4 py-2 text-sm font-medium transition-colors hover:bg-muted"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreate}
                    className="rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                  >
                    Create Key
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </motion.div>
    </ThreeScene>
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

function RateLimitRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
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

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}
