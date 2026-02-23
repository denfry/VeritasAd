"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { listAuditLogs, getAuditStats } from "@/lib/api-client"
import type { AuditLogListItem, CursorPaginationResponse } from "@/types/api"
import { toast } from "sonner"
import { Loader2, Shield, Search, Filter, ChevronDown, ChevronUp, Calendar, Download, * as Icons } from "lucide-react"
import { formatDistanceToNow, format } from "date-fns"
import { ru } from "date-fns/locale"

type SortOrder = "asc" | "desc"

// Event type icons and colors
const EVENT_TYPE_CONFIG: Record<string, { icon: string; color: string }> = {
  // Auth
  login: { icon: "key", color: "text-blue-500" },
  logout: { icon: "log-out", color: "text-gray-500" },
  login_failed: { icon: "alert-triangle", color: "text-yellow-500" },

  // User
  "user.created": { icon: "user-plus", color: "text-green-500" },
  "user.updated": { icon: "user-edit", color: "text-blue-500" },
  "user.deleted": { icon: "user-x", color: "text-red-500" },
  "user.banned": { icon: "ban", color: "text-red-500" },
  "user.unbanned": { icon: "check-circle", color: "text-green-500" },
  "role.changed": { icon: "refresh-cw", color: "text-purple-500" },
  "plan.changed": { icon: "credit-card", color: "text-amber-500" },

  // Admin
  "admin.login": { icon: "shield", color: "text-indigo-500" },
  "admin.user.view": { icon: "eye", color: "text-blue-400" },
  "admin.user.list": { icon: "list", color: "text-blue-400" },
  "admin.user.update": { icon: "edit", color: "text-amber-500" },
  "admin.analytics.view": { icon: "bar-chart", color: "text-cyan-500" },

  // Security
  "session.revoked": { icon: "lock", color: "text-red-500" },
  "api_key.created": { icon: "key", color: "text-green-500" },
  "api_key.revoked": { icon: "unlock", color: "text-red-500" },
}

const STATUS_CONFIG: Record<string, { color: string; bg: string }> = {
  success: { color: "text-green-600", bg: "bg-green-50" },
  failure: { color: "text-red-600", bg: "bg-red-50" },
  denied: { color: "text-amber-600", bg: "bg-amber-50" },
}

export default function AuditLogsPage() {
  const router = useRouter()
  const { user, loading: authLoading, signOut } = useAuth()
  
  // Data state
  const [logsResponse, setLogsResponse] = useState<CursorPaginationResponse<AuditLogListItem> | null>(null)
  const [stats, setStats] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  
  // Pagination state
  const [cursor, setCursor] = useState<string | null>(null)
  const [history, setHistory] = useState<string[]>([])
  
  // Filters state
  const [search, setSearch] = useState("")
  const [searchDebounce, setSearchDebounce] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("")
  const [dateRange, setDateRange] = useState<string>("30")

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchDebounce(search)
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  // Load data
  const loadData = useCallback(async () => {
    try {
      const [logsData, statsData] = await Promise.all([
        listAuditLogs({
          limit: 20,
          cursor: cursor || undefined,
          event_type: eventTypeFilter || undefined,
          event_category: categoryFilter || undefined,
          actor_email: searchDebounce || undefined,
          status: statusFilter || undefined,
        }),
        getAuditStats({ days: parseInt(dateRange) }),
      ])
      setLogsResponse(logsData)
      setStats(statsData)
      setErrorMessage(null)
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error("Session expired. Please sign in again.")
        await signOut()
        router.push("/auth/login")
        setErrorMessage("Session expired. Please sign in again.")
      } else if (error.response?.status === 403) {
        toast.error("Admin access required")
        router.push("/account")
        setErrorMessage("Admin access required.")
      } else {
        toast.error("Failed to load audit logs")
        setErrorMessage("Failed to load audit logs. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }, [cursor, eventTypeFilter, categoryFilter, searchDebounce, statusFilter, dateRange, router, signOut])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
      return
    }

    if (user) {
      loadData()
    }
  }, [user, authLoading, loadData, router])

  // Handle pagination
  const handleNextPage = () => {
    if (logsResponse?.next_cursor) {
      setHistory([...history, cursor || ""])
      setCursor(logsResponse.next_cursor)
    }
  }

  const handlePrevPage = () => {
    if (history.length > 0) {
      const prevCursor = history[history.length - 1]
      setHistory(history.slice(0, -1))
      setCursor(prevCursor || null)
    }
  }

  // Export logs
  const handleExport = () => {
    const data = logsResponse?.data || []
    const csv = [
      ["ID", "Event Type", "Category", "Description", "Actor", "Target", "Status", "Created At"].join(","),
      ...data.map(log => [
        log.id,
        log.event_type,
        log.event_category,
        `"${log.description.replace(/"/g, '""')}"`,
        log.actor_email || "",
        log.target_email || "",
        log.status,
        log.created_at,
      ].join(","))
    ].join("\n")
    
    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `audit-logs-${format(new Date(), "yyyy-MM-dd")}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast.success("Audit logs exported")
  }

  if (authLoading || loading) {
    return (
      <SiteShell>
        <section className="container mx-auto max-w-7xl px-4 section">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        </section>
      </SiteShell>
    )
  }

  if (errorMessage) {
    return (
      <SiteShell>
        <section className="container mx-auto max-w-4xl px-4 section">
          <div className="card p-6 space-y-4 text-center">
            <h1 className="text-xl font-semibold">Audit Logs unavailable</h1>
            <p className="text-sm text-muted-foreground">{errorMessage}</p>
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => {
                  setLoading(true)
                  loadData()
                }}
                className="btn btn-primary"
              >
                Retry
              </button>
              <button onClick={() => router.push("/admin")} className="btn btn-outline">
                Go to Admin Dashboard
              </button>
            </div>
          </div>
        </section>
      </SiteShell>
    )
  }

  return (
    <SiteShell>
      <section className="container mx-auto max-w-7xl px-4 section space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <h1 className="text-3xl font-semibold">Audit Logs</h1>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Track all admin actions and security events
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleExport} className="btn btn-outline btn-sm">
              <Download className="h-4 w-4 mr-1" />
              Export
            </button>
            <Link href="/admin" className="btn btn-outline">
              Back to Admin
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <div className="card card-hover p-5">
              <p className="text-sm text-muted-foreground">Total Events</p>
              <p className="mt-2 text-2xl font-semibold">{stats.total_events}</p>
              <p className="text-xs text-muted-foreground">Last {stats.period_days} days</p>
            </div>
            
            {stats.events_by_category.slice(0, 4).map((cat: any) => (
              <div key={cat.category} className="card card-hover p-5">
                <p className="text-sm text-muted-foreground capitalize">{cat.category}</p>
                <p className="mt-2 text-2xl font-semibold">{cat.count}</p>
              </div>
            ))}
          </div>
        )}

        {/* Filters */}
        <div className="card p-4">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Filters</span>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="relative md:col-span-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by actor email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-field pl-9 text-sm"
              />
            </div>
            
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="input-field text-sm"
            >
              <option value="">All Categories</option>
              <option value="auth">Authentication</option>
              <option value="user">User Management</option>
              <option value="admin">Admin Actions</option>
              <option value="security">Security</option>
              <option value="data">Data Operations</option>
              <option value="system">System</option>
            </select>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field text-sm"
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
              <option value="denied">Denied</option>
            </select>
            
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="input-field text-sm"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="60">Last 60 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>
          
          {(categoryFilter || statusFilter || search) && (
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setCategoryFilter("")
                  setStatusFilter("")
                  setSearch("")
                }}
                className="btn btn-sm btn-ghost"
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>

        {/* Logs Table */}
        <div className="card p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left">
                <tr>
                  <th className="px-4 py-3 w-10">Event</th>
                  <th className="px-4 py-3">Description</th>
                  <th className="px-4 py-3">Actor</th>
                  <th className="px-4 py-3">Target</th>
                  <th className="px-4 py-3">IP Address</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {logsResponse?.data.map((log) => {
                  const config = EVENT_TYPE_CONFIG[log.event_type] || { icon: "file-text", color: "text-gray-500" }
                  const statusConfig = STATUS_CONFIG[log.status] || { color: "text-gray-600", bg: "bg-gray-50" }
                  
                  return (
                    <tr key={log.id} className="hover:bg-muted/20">
                      <td className="px-4 py-3">
                        {(() => {
                          const IconComponent = Icons[config.icon as keyof typeof Icons]
                          return IconComponent ? (
                            <IconComponent className={`h-5 w-5 ${config.color}`} />
                          ) : null
                        })()}
                      </td>
                      <td className="px-4 py-3">
                        <div className="space-y-1">
                          <p className="font-medium">{log.description}</p>
                          <p className="text-xs text-muted-foreground">
                            <span className="capitalize">{log.event_category}</span>
                            {" • "}
                            <span className="font-mono">{log.event_type}</span>
                          </p>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        {log.actor_email ? (
                          <div>
                            <p className="font-medium">{log.actor_email}</p>
                            {log.actor_user_id && (
                              <p className="text-xs text-muted-foreground">ID: {log.actor_user_id}</p>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {log.target_email ? (
                          <div>
                            <p className="font-medium">{log.target_email}</p>
                            {log.target_type && (
                              <p className="text-xs text-muted-foreground capitalize">{log.target_type}</p>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs">
                        {log.actor_ip || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`badge text-xs ${statusConfig.bg} ${statusConfig.color}`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="space-y-1">
                          <p className="text-sm">{formatDistanceToNow(new Date(log.created_at), { addSuffix: true, locale: ru })}</p>
                          <p className="text-xs text-muted-foreground">
                            {format(new Date(log.created_at), "MMM d, HH:mm")}
                          </p>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              {logsResponse?.data.length || 0} of {logsResponse?.total_count || 0} events
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrevPage}
                disabled={history.length === 0}
                className="btn btn-sm btn-outline"
              >
                Previous
              </button>
              <button
                onClick={handleNextPage}
                disabled={!logsResponse?.has_more}
                className="btn btn-sm btn-outline"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </section>
    </SiteShell>
  )
}

// Add Link import
import Link from "next/link"
