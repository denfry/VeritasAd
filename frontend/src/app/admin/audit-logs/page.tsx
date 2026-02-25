"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { AppShell } from "@/components/AppShell"
import { useAuth } from "@/contexts/auth-context"
import { listAuditLogs, getAuditStats } from "@/lib/api-client"
import type { AuditLogListItem, CursorPaginationResponse } from "@/types/api"
import { toast } from "sonner"
import { 
  Loader2, Shield, Search, Filter, ChevronDown, 
  ChevronUp, Calendar, Download, Key, LogOut, 
  AlertTriangle, UserPlus, Ban, CheckCircle2, 
  RefreshCw, CreditCard, Eye, List, Edit, BarChart3,
  Lock, Unlock, FileText, ArrowLeft
} from "lucide-react"
import { formatDistanceToNow, format } from "date-fns"
import { ru } from "date-fns/locale"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"

type SortOrder = "asc" | "desc"

// Event type icons and colors
const EVENT_TYPE_CONFIG: Record<string, { icon: any; color: string }> = {
  // Auth
  login: { icon: Key, color: "text-blue-500" },
  logout: { icon: LogOut, color: "text-gray-500" },
  login_failed: { icon: AlertTriangle, color: "text-yellow-500" },

  // User
  "user.created": { icon: UserPlus, color: "text-green-500" },
  "user.updated": { icon: Edit, color: "text-blue-500" },
  "user.deleted": { icon: Ban, color: "text-red-500" },
  "user.banned": { icon: Ban, color: "text-red-500" },
  "user.unbanned": { icon: CheckCircle2, color: "text-green-500" },
  "role.changed": { icon: RefreshCw, color: "text-purple-500" },
  "plan.changed": { icon: CreditCard, color: "text-amber-500" },

  // Admin
  "admin.login": { icon: Shield, color: "text-indigo-500" },
  "admin.user.view": { icon: Eye, color: "text-blue-400" },
  "admin.user.list": { icon: List, color: "text-blue-400" },
  "admin.user.update": { icon: Edit, color: "text-amber-500" },
  "admin.analytics.view": { icon: BarChart3, color: "text-cyan-500" },

  // Security
  "session.revoked": { icon: Lock, color: "text-red-500" },
  "api_key.created": { icon: Key, color: "text-green-500" },
  "api_key.revoked": { icon: Unlock, color: "text-red-500" },
}

const STATUS_CONFIG: Record<string, { color: string; bg: string }> = {
  success: { color: "text-emerald-600", bg: "bg-emerald-500/10" },
  failure: { color: "text-red-600", bg: "bg-red-500/10" },
  denied: { color: "text-amber-600", bg: "bg-amber-500/10" },
}

export default function AuditLogsPage() {
  const router = useRouter()
  const { user, loading: authLoading, signOut } = useAuth()
  
  // Data state
  const [logsResponse, setLogsResponse] = useState<CursorPaginationResponse<AuditLogListItem> | null>(null)
  const [stats, setStats] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  
  // Pagination state
  const [cursor, setCursor] = useState<string | null>(null)
  const [history, setHistory] = useState<string[]>([])
  
  // Filters state
  const [search, setSearch] = useState("")
  const [searchDebounce, setSearchDebounce] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [dateRange, setDateRange] = useState<string>("30")

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchDebounce(search)
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  // Load data
  const loadData = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoading(true)
    else setRefreshing(true)
    
    try {
      const [logsData, statsData] = await Promise.all([
        listAuditLogs({
          limit: 20,
          cursor: cursor || undefined,
          event_category: categoryFilter || undefined,
          actor_email: searchDebounce || undefined,
          status: statusFilter || undefined,
        }),
        getAuditStats({ days: parseInt(dateRange) }),
      ])
      setLogsResponse(logsData)
      setStats(statsData)
    } catch (error: any) {
      console.error("Audit Logs Error:", error)
      if (error.response?.status === 403) {
        toast.error("Admin access required")
        router.push("/dashboard")
      }
      
      // Fallback for Dev
      if (process.env.NODE_ENV === 'development') {
        setStats({
          total_events: 1540,
          period_days: 30,
          events_by_category: [
            { category: "auth", count: 850 },
            { category: "user", count: 320 },
            { category: "admin", count: 150 },
            { category: "security", count: 220 },
          ]
        })
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [cursor, categoryFilter, searchDebounce, statusFilter, dateRange, router])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login")
      return
    }
    if (user) loadData()
  }, [user, authLoading, loadData, router])

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
      <AppShell>
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-sm font-bold text-muted-foreground uppercase tracking-widest animate-pulse">Decrypting Security Logs...</p>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <section className="container mx-auto max-w-7xl px-4 py-10 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <Link href="/admin" className="p-2 rounded-xl hover:bg-muted transition-colors mr-2">
                 <ArrowLeft className="h-5 w-5" />
              </Link>
              <Shield className="h-6 w-6 text-primary" />
              <h1 className="text-3xl font-extrabold tracking-tight">Security Archive</h1>
            </div>
            <p className="text-muted-foreground font-medium ml-12">Comprehensive audit trail of all platform events and administrative actions.</p>
          </div>
          
          <div className="flex items-center gap-3">
            <button onClick={handleExport} className="btn btn-outline h-11 px-6 rounded-xl gap-2 font-bold transition-all hover:bg-muted">
              <Download className="h-4 w-4" />
              Export .CSV
            </button>
            <button onClick={() => loadData(true)} className="btn btn-primary h-11 px-6 rounded-xl gap-2 font-bold shadow-lg shadow-primary/20">
               <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
               Sync Logs
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 grid-cols-2 md:grid-cols-5">
          <div className="card p-5 bg-gradient-to-br from-card to-muted/20">
            <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Total Vector Events</p>
            <p className="text-2xl font-black mt-1">{stats?.total_events}</p>
          </div>
          {stats?.events_by_category.slice(0, 4).map((cat: any) => (
            <div key={cat.category} className="card p-5">
              <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{cat.category}</p>
              <p className="text-2xl font-black mt-1">{cat.count}</p>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="card p-6 bg-muted/30 border-dashed border-2">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative md:col-span-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Filter by actor..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-field pl-10 h-11 bg-background text-sm font-bold"
              />
            </div>
            
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="input-field h-11 bg-background text-sm font-bold"
            >
              <option value="">All Vectors</option>
              <option value="auth">Authentication</option>
              <option value="user">User Ops</option>
              <option value="admin">Admin Root</option>
              <option value="security">Security Layer</option>
            </select>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field h-11 bg-background text-sm font-bold"
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
              <option value="denied">Access Denied</option>
            </select>
            
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="input-field h-11 bg-background text-sm font-bold"
            >
              <option value="7">Last Cycle (7d)</option>
              <option value="30">Standard Range (30d)</option>
              <option value="90">Quarterly Range (90d)</option>
            </select>
          </div>
        </div>

        {/* Logs Table */}
        <div className="card overflow-hidden border-border/50 shadow-2xl shadow-black/5">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground bg-muted/10 border-b border-border/50">
                <tr>
                  <th className="px-6 py-4 w-12">Class</th>
                  <th className="px-6 py-4">Action Detail</th>
                  <th className="px-6 py-4">Origin Identity</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50 bg-card">
                <AnimatePresence mode="popLayout">
                  {logsResponse?.data.map((log, idx) => {
                    const config = EVENT_TYPE_CONFIG[log.event_type] || { icon: FileText, color: "text-muted-foreground" }
                    const statusConfig = STATUS_CONFIG[log.status] || { color: "text-gray-600", bg: "bg-muted" }
                    const IconComp = config.icon
                    
                    return (
                      <motion.tr 
                        key={log.id} 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: idx * 0.01 }}
                        className="hover:bg-muted/30 transition-colors group"
                      >
                        <td className="px-6 py-5">
                           <div className={`h-10 w-10 rounded-xl flex items-center justify-center border border-border/50 bg-background shadow-sm ${config.color}`}>
                              <IconComp className="h-5 w-5" />
                           </div>
                        </td>
                        <td className="px-6 py-5">
                          <div className="space-y-1">
                            <p className="font-bold text-foreground leading-none">{log.description}</p>
                            <p className="text-[10px] font-black uppercase tracking-tighter text-muted-foreground">
                              {log.event_category} • <span className="font-mono">{log.event_type}</span>
                            </p>
                          </div>
                        </td>
                        <td className="px-6 py-5">
                          {log.actor_email ? (
                            <div className="space-y-0.5">
                              <p className="font-bold text-sm">{log.actor_email}</p>
                              <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest flex items-center gap-1">
                                <Globe className="h-2 w-2" /> {log.actor_ip}
                              </p>
                            </div>
                          ) : (
                            <span className="text-muted-foreground font-black text-[10px]">SYSTEM</span>
                          )}
                        </td>
                        <td className="px-6 py-5">
                          <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest border ${statusConfig.bg} ${statusConfig.color} border-current/10`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="px-6 py-5 text-right">
                          <div className="space-y-0.5">
                            <p className="text-xs font-bold">{formatDistanceToNow(new Date(log.created_at), { addSuffix: true, locale: ru })}</p>
                            <p className="text-[10px] font-bold text-muted-foreground uppercase">{format(new Date(log.created_at), "MMM dd, HH:mm:ss")}</p>
                          </div>
                        </td>
                      </motion.tr>
                    )
                  })}
                </AnimatePresence>
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-6 py-4 bg-muted/10 border-t border-border/50 flex items-center justify-between">
            <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
              Node Entries: {logsResponse?.total_count || 0}
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrevPage}
                disabled={history.length === 0}
                className="btn btn-outline btn-sm h-9 px-4 rounded-lg font-bold disabled:opacity-30"
              >
                Prev
              </button>
              <button
                onClick={handleNextPage}
                disabled={!logsResponse?.has_more}
                className="btn btn-outline btn-sm h-9 px-4 rounded-lg font-bold disabled:opacity-30"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </section>
    </AppShell>
  )
}

function Globe({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="12" cy="12" r="10"/>
      <line x1="2" y1="12" x2="22" y2="12"/>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    </svg>
  )
}
