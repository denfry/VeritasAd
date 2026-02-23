"use client"

import { useEffect, useState } from "react"
import { Download, Filter, RefreshCw } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { fetchAnalysisHistory } from "@/lib/api-client"
import type { AnalysisHistoryItem } from "@/types/api"

function getSourceTypeName(sourceType: string): string {
  const typeMap: Record<string, string> = {
    file: "File Upload",
    url: "URL",
    youtube: "YouTube",
    telegram: "Telegram",
    instagram: "Instagram",
    tiktok: "TikTok",
    vk: "VK",
  }
  return typeMap[sourceType.toLowerCase()] || sourceType
}

function formatDate(isoString: string | null): string {
  if (!isoString) return "-"
  try {
    return new Date(isoString).toLocaleDateString("ru-RU", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  } catch {
    return "-"
  }
}

export default function HistoryPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [limit] = useState(20)
  const [offset] = useState(0)

  useEffect(() => {
    if (!authLoading && !user) {
      toast.error("Please sign in to view history")
      router.push("/auth/login")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      loadHistory()
    }
  }, [user])

  async function loadHistory() {
    setIsLoading(true)
    try {
      const data = await fetchAnalysisHistory({ limit, offset })
      setHistory(data)
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error("Session expired. Please sign in again.")
        router.push("/auth/login")
      } else {
        toast.error("Failed to load analysis history")
        console.error("Failed to load history:", error)
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <SiteShell>
      <section className="container mx-auto max-w-6xl px-4 section space-y-8">
        <div className="flex flex-col gap-3">
          <p className="text-sm text-muted-foreground">Archive</p>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-semibold">Analysis history</h1>
            <button
              onClick={loadHistory}
              disabled={isLoading}
              className="p-2 rounded-lg hover:bg-muted transition-colors disabled:opacity-50"
              title="Refresh"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            </button>
          </div>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Review prior checks, export results, and track platform trends over time.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Filter className="h-4 w-4" />
            <span>Filters will be available in the next release.</span>
          </div>
          <button className="btn btn-outline" disabled={history.length === 0}>
            <Download className="h-4 w-4" />
            Export CSV
          </button>
        </div>

        <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
            <thead className="bg-muted/50 text-left text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Task ID</th>
                <th className="px-4 py-3">Platform</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Score</th>
                <th className="px-4 py-3">Has Ads</th>
                <th className="px-4 py-3">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                    Loading history...
                  </td>
                </tr>
              ) : history.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                    No analysis history yet. Start by analyzing a video!
                  </td>
                </tr>
              ) : (
                history.map((item) => (
                  <tr key={item.task_id}>
                    <td className="px-4 py-3 font-medium truncate max-w-[200px]">
                      {item.task_id.slice(0, 12)}...
                    </td>
                    <td className="px-4 py-3">
                      <span className="badge">{getSourceTypeName(item.source_type)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={item.status} progress={item.progress} />
                    </td>
                    <td className="px-4 py-3">
                      {item.status === "completed" && item.confidence_score !== null
                        ? item.confidence_score.toFixed(2)
                        : "-"}
                    </td>
                    <td className="px-4 py-3">
                      {item.status === "completed" ? (
                        item.has_advertising ? (
                          <span className="text-red-500 font-medium">Yes</span>
                        ) : (
                          <span className="text-green-500 font-medium">No</span>
                        )
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="px-4 py-3">{formatDate(item.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
            </table>
          </div>
        </div>
      </section>
    </SiteShell>
  )
}

function StatusBadge({ status, progress }: { status: string; progress: number }) {
  const statusConfig: Record<string, { label: string; className: string }> = {
    pending: { label: "Pending", className: "bg-gray-100 text-gray-700" },
    queued: { label: "Queued", className: "bg-blue-100 text-blue-700" },
    processing: { label: `Processing ${progress}%`, className: "bg-yellow-100 text-yellow-700" },
    completed: { label: "Completed", className: "bg-green-100 text-green-700" },
    failed: { label: "Failed", className: "bg-red-100 text-red-700" },
  }

  const config = statusConfig[status.toLowerCase()] || { label: status, className: "bg-gray-100 text-gray-700" }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
