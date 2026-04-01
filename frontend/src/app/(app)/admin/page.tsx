"use client"

import { useEffect, useState, useCallback, type ReactNode } from "react"
import { useRouter } from "next/navigation"

import { useAuth } from "@/contexts/auth-context"
import { listUsers, getAnalytics, listAuditLogs, getSystemMetrics, getAnalyticsTrends } from "@/lib/api-client"
import type { UserListItem, CursorPaginationResponse, AuditLogListItem } from "@/types/api"
import type { SystemMetrics, TrendData } from "@/lib/api-client"
import { toast } from "sonner"
import {
  Loader2, Activity, Search, Filter, Shield, RefreshCw,
  ArrowUpRight, ArrowDownRight, Globe, ShieldAlert, Cpu, Settings
} from "lucide-react"
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line
} from 'recharts'
import { formatDistanceToNow } from "date-fns"
import Link from "next/link"

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f43f5e', '#f59e0b']
type AnalyticsData = Awaited<ReturnType<typeof getAnalytics>>
type MetricProps = { label: string; value: string | number; icon: ReactNode; color: string }
type StatCardLargeProps = {
  label: string
  value: string | number
  trend: TrendData | null
  description: string
  chartData: Array<{ time: string; analyses: number; latency: number; load: number }>
  dataKey: "analyses" | "latency" | "load"
  color: string
}

export default function AdminPage() {
  const router = useRouter()
  const { loading: authLoading, user } = useAuth()

  useEffect(() => {
    if (!authLoading && user && user.role !== "admin") {
      router.push("/dashboard")
    }
  }, [authLoading, user, router])

  // Data state
  const [usersResponse, setUsersResponse] = useState<CursorPaginationResponse<UserListItem> | null>(null)
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [auditLogs, setAuditLogs] = useState<AuditLogListItem[]>([])
  const [chartData, setChartData] = useState<Array<{ time: string; analyses: number; latency: number; load: number }>>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [search, setSearch] = useState("")
  const [debouncedSearch, setDebouncedSearch] = useState("")
  const [trends, setTrends] = useState<{
    analyses_today: TrendData | null
    active_users: TrendData | null
    avg_confidence: TrendData | null
    failed_analyses: TrendData | null
  }>({ analyses_today: null, active_users: null, avg_confidence: null, failed_analyses: null })

  // System metrics state
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)

  // Debounce search effect
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search)
    }, 500)
    return () => clearTimeout(handler)
  }, [search])

  const loadData = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoading(true)
    else setRefreshing(true)

    try {
      const [usersData, analyticsData, logsData] = await Promise.all([
        listUsers({ limit: 8, search: debouncedSearch }),
        getAnalytics(),
        listAuditLogs({ limit: 10 }),
      ])
      setUsersResponse(usersData)
      setAnalytics(analyticsData)
      if (analyticsData.chart_data && analyticsData.chart_data.length > 0) {
        setChartData(analyticsData.chart_data)
      }
      setAuditLogs(logsData.data)
    } catch (error: unknown) {
      console.error("Admin Load Error:", error)
      const status = error instanceof Error && "response" in error
        ? (error as { response?: { status?: number } }).response?.status
        : undefined
      if (status === 403) {
        toast.error("Admin access denied")
        router.push("/dashboard")
      } else if (!isSilent) {
        toast.error("Failed to load admin data")
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [router, debouncedSearch])

  const loadTrends = useCallback(async () => {
    try {
      const data = await getAnalyticsTrends()
      setTrends({
        analyses_today: data.analyses_today,
        active_users: data.active_users,
        avg_confidence: data.avg_confidence,
        failed_analyses: data.failed_analyses,
      })
    } catch {
      // Trends are optional, gracefully ignore
    }
  }, [])

  const loadSystemMetrics = useCallback(async () => {
    try {
      const data = await getSystemMetrics()
      setSystemMetrics(data)
    } catch {
      // System metrics are optional
    }
  }, [])

  useEffect(() => {
    loadData()
    loadTrends()
    loadSystemMetrics()
  }, [loadData, loadTrends, loadSystemMetrics])

  // Refresh system metrics every 10 seconds
  useEffect(() => {
    const interval = setInterval(loadSystemMetrics, 10000)
    return () => clearInterval(interval)
  }, [loadSystemMetrics])

  if (authLoading || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-sm font-black text-muted-foreground uppercase tracking-[0.2em] animate-pulse">Neural Root Access...</p>
      </div>
    )
  }

  const cpuValue = systemMetrics?.cpu_percent ?? 0
  const memValue = systemMetrics?.memory_percent ?? 0
  const uptimeValue = systemMetrics?.uptime_seconds ?? 0
  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    return `${h}h ${m}m`
  }

  return (
    <section className="container mx-auto max-w-[1600px] px-4 py-8 space-y-8 lg:py-12">
      {/* Header */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-2xl bg-primary flex items-center justify-center text-white shadow-xl shadow-primary/30">
              <Shield className="h-7 w-7" />
            </div>
            <div>
              <h1 className="text-3xl font-semibold tracking-tight lg:text-4xl">Command Center</h1>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase tracking-widest border border-emerald-500/20">
                  <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  System Live
                </span>
                {systemMetrics && (
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                    Uptime {formatUptime(uptimeValue)}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 bg-muted/20 p-2 rounded-full border border-border/50 backdrop-blur-sm">
           <div className="flex items-center gap-4 px-4 border-r border-border/50">
              <LiveMetric label="CPU" value={`${cpuValue.toFixed(0)}%`} icon={<Cpu className="h-3 w-3" />} color="text-blue-500" />
              <LiveMetric label="MEM" value={`${memValue.toFixed(0)}%`} icon={<Activity className="h-3 w-3" />} color="text-purple-500" />
              <LiveMetric label="UPTIME" value={formatUptime(uptimeValue)} icon={<Globe className="h-3 w-3" />} color="text-emerald-500" />
           </div>
           <div className="flex gap-2">
              <button onClick={() => { loadData(true); loadTrends(); loadSystemMetrics() }} disabled={refreshing} className="btn btn-outline h-10 px-4 rounded-full gap-2 font-semibold text-xs">
                <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
                Sync Core
              </button>
              <Link href="/admin/audit-logs" className="btn btn-primary h-10 px-5 rounded-full gap-2 font-semibold text-xs shadow-lg shadow-primary/20">
                 <ShieldAlert className="h-3.5 w-3.5" />
                 Audit Trail
              </Link>
           </div>
        </div>
      </div>

      {/* Top Analytics Row */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCardLarge
          label="Analyses Today"
          value={analytics?.analyses_today || 0}
          trend={trends.analyses_today}
          description="Across all vectors"
          chartData={chartData.slice(-10)}
          dataKey="analyses"
          color="#3b82f6"
        />
        <StatCardLarge
          label="Active Nodes"
          value={analytics?.active_users_today || 0}
          trend={trends.active_users}
          description="Concurrent sessions"
          chartData={chartData.slice(-10)}
          dataKey="load"
          color="#8b5cf6"
        />
        <StatCardLarge
          label="Avg Confidence"
          value={analytics ? `${(analytics.avg_confidence_score * 100).toFixed(0)}%` : "--"}
          trend={trends.avg_confidence}
          description="Model accuracy"
          chartData={chartData.slice(-10)}
          dataKey="analyses"
          color="#10b981"
        />
        <StatCardLarge
          label="Success Rate"
          value={analytics ? `${((1 - (analytics.failed_analyses || 0) / Math.max(analytics.total_analyses || 1, 1)) * 100).toFixed(1)}%` : "--"}
          trend={trends.failed_analyses ? { value: -trends.failed_analyses.value, up: !trends.failed_analyses.up } : null}
          description="Inference stability"
          chartData={chartData.slice(-10)}
          dataKey="analyses"
          color="#f59e0b"
        />
      </div>

      {/* Charts Section */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Real-time Traffic */}
        <div className="lg:col-span-2 surface p-8 space-y-8 bg-gradient-to-br from-card to-card/50">
          <div className="flex items-center justify-between">
             <div>
              <h2 className="text-xl font-semibold tracking-tight">Neural Traffic Flow</h2>
               <p className="text-xs text-muted-foreground font-semibold uppercase tracking-[0.22em] mt-1">Analysis & load telemetry</p>
             </div>
             <div className="flex gap-6">
                <LegendItem color="#3b82f6" label="Analyses" />
                <LegendItem color="#8b5cf6" label="System Load" />
             </div>
          </div>

          <div className="h-[350px] w-full">
             <ResponsiveContainer width="100%" height="100%">
               <AreaChart data={chartData.length > 0 ? chartData : [{ time: "N/A", analyses: 0, latency: 0, load: 0 }]}>
                  <defs>
                    <linearGradient id="colorAnalyses" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border)/0.3)" />
                  <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "12px",
                      boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
                    }}
                    labelStyle={{ fontWeight: 700, marginBottom: 4 }}
                  />
                  <Area type="monotone" dataKey="analyses" stroke="#3b82f6" fillOpacity={1} fill="url(#colorAnalyses)" strokeWidth={2} />
                  <Area type="monotone" dataKey="load" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorLoad)" strokeWidth={2} />
               </AreaChart>
             </ResponsiveContainer>
          </div>
        </div>

        {/* Plan Distribution */}
        <div className="surface p-8 space-y-6">
          <h2 className="text-xl font-semibold tracking-tight">Plan Distribution</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analytics?.plan_distribution || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {(analytics?.plan_distribution || []).map((_: unknown, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2">
            {(analytics?.plan_distribution || []).map((plan: { name: string; value: number }, i: number) => (
              <div key={plan.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className="font-medium">{plan.name}</span>
                </div>
                <span className="font-bold">{plan.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="surface p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight">User Registry</h2>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search users..."
                className="input-field pl-10 h-10 w-64 text-sm"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <button className="btn btn-outline h-10 px-4 rounded-full gap-2 text-xs">
              <Filter className="h-3.5 w-3.5" />
              Filters
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/30 text-muted-foreground font-black uppercase tracking-widest text-[10px] border-b border-border/50">
              <tr>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Plan</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Usage</th>
                <th className="px-4 py-3">Analyses</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {usersResponse?.data.map((user) => (
                <tr key={user.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3 font-bold">{user.email || "No email"}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-black uppercase bg-primary/10 text-primary border border-primary/20">
                      {user.plan}
                    </span>
                  </td>
                  <td className="px-4 py-3 capitalize">{user.role}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary"
                          style={{ width: `${Math.min((user.daily_used / Math.max(user.daily_limit, 1)) * 100, 100)}%` }}
                        />
                      </div>
                      <span className="text-[10px] font-bold">{user.daily_used}/{user.daily_limit}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-bold">{user.total_analyses}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase ${
                      user.is_active ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground text-xs">
                    {formatDistanceToNow(new Date(user.created_at), { addSuffix: true })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Audit Logs */}
      <div className="surface p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight">Recent Audit Events</h2>
          <Link href="/admin/audit-logs" className="text-sm text-primary hover:underline flex items-center gap-1">
            View all <ArrowUpRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="space-y-3">
          {auditLogs.map((log) => (
            <div key={log.id} className="flex items-center justify-between p-4 rounded-xl bg-muted/20 border border-border/50">
              <div className="flex items-center gap-4">
                <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${
                  log.status === 'success' ? 'bg-emerald-500/10 text-emerald-500' :
                  log.status === 'failure' ? 'bg-red-500/10 text-red-500' :
                  'bg-amber-500/10 text-amber-500'
                }`}>
                  <Settings className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-bold">{log.event_type}</p>
                  <p className="text-xs text-muted-foreground">{log.description}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs font-bold">{log.actor_email || "System"}</p>
                <p className="text-[10px] text-muted-foreground">
                  {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function LiveMetric({ label, value, icon, color }: MetricProps) {
  return (
    <div className="flex items-center gap-2">
      <div className={`p-1.5 rounded-lg bg-muted/50 ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">{label}</p>
        <p className="text-xs font-bold">{value}</p>
      </div>
    </div>
  )
}

function StatCardLarge({ label, value, trend, description, chartData, dataKey, color }: StatCardLargeProps) {
  return (
    <div className="surface p-6 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-black uppercase tracking-[0.22em] text-muted-foreground">{label}</p>
        {trend && (
          <span className={`flex items-center gap-1 text-[10px] font-black uppercase tracking-widest ${trend.up ? 'text-emerald-500' : 'text-red-500'}`}>
            {trend.up ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {Math.abs(trend.value)}%
          </span>
        )}
      </div>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground font-medium">{description}</p>
      {chartData.length > 0 && (
        <div className="h-[60px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: color }} />
      <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{label}</span>
    </div>
  )
}
