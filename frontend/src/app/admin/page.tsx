"use client"

import { useEffect, useState, useCallback, useMemo } from "react"
import { useRouter } from "next/navigation"
import { AppShell } from "@/components/AppShell"
import { useAuth } from "@/contexts/auth-context"
import { listUsers, updateUser, getAnalytics, bulkUpdateUsers, listAuditLogs } from "@/lib/api-client"
import type { UserListItem, CursorPaginationResponse, AuditLogListItem } from "@/types/api"
import { toast } from "sonner"
import { 
  Loader2, Users, Activity, BarChart3, AlertCircle, 
  TrendingUp, Search, Filter, ChevronDown, ChevronUp, 
  Ban, Check, Shield, RefreshCw, 
  ArrowUpRight, ArrowDownRight, UserPlus, FileSearch,
  CheckSquare, Square, MoreVertical, ExternalLink,
  Zap, Clock, Globe, ShieldAlert, Cpu, Settings
} from "lucide-react"
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, BarChart, Bar,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts'
import { formatDistanceToNow, subDays, format, subMinutes } from "date-fns"
import { motion, AnimatePresence } from "framer-motion"
import Link from "next/link"

// Mock real-time data generators
const generateChartData = () => {
  return Array.from({ length: 24 }).map((_, i) => ({
    time: format(subMinutes(new Date(), (23 - i) * 60), 'HH:mm'),
    analyses: Math.floor(Math.random() * 100) + 50,
    latency: Math.floor(Math.random() * 200) + 100,
    load: Math.floor(Math.random() * 40) + 30,
  }))
}

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f43f5e', '#f59e0b']

export default function AdminPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  
  // Data state
  const [usersResponse, setUsersResponse] = useState<CursorPaginationResponse<UserListItem> | null>(null)
  const [analytics, setAnalytics] = useState<any | null>(null)
  const [auditLogs, setAuditLogs] = useState<AuditLogListItem[]>([])
  const [chartData, setChartData] = useState(generateChartData())
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [search, setSearch] = useState("")
  const [debouncedSearch, setDebouncedSearch] = useState("")

  // Debounce search effect
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search)
    }, 500)
    return () => clearTimeout(handler)
  }, [search])
  
  // Live Metrics
  const [cpuUsage, setCpuUsage] = useState(42)
  const [memUsage, setMemUsage] = useState(68)
  const [liveRequests, setLiveRequests] = useState(12)

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
      if (analyticsData.chart_data) {
        setChartData(analyticsData.chart_data)
      }
      setAuditLogs(logsData.data)
    } catch (error: any) {
      console.error("Admin Load Error:", error)
      if (error.response?.status === 403) {
        toast.error("Admin access denied")
        router.push("/dashboard")
      }
      
      // Fallback for Dev
      if (process.env.NODE_ENV === 'development') {
        setAnalytics({
          total_users: 1248,
          active_users_today: 86,
          total_analyses: 15420,
          analyses_today: 342,
          avg_confidence_score: 0.84,
          failed_analyses: 24,
          plan_distribution: [
            { name: 'Free', value: 450 },
            { name: 'Pro', value: 320 },
            { name: 'Business', value: 180 },
            { name: 'Enterprise', value: 45 },
          ],
          top_users: [
            { id: 1, email: "enterprise@corp.com", plan: "enterprise", total_analyses: 540 },
            { id: 2, email: "agency@marketing.ru", plan: "business", total_analyses: 320 },
            { id: 3, email: "top@user.ai", plan: "pro", total_analyses: 215 },
          ],
          chart_data: generateChartData()
        })
        setChartData(generateChartData())
      }
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [router, debouncedSearch])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Real-time Simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setCpuUsage(prev => Math.max(10, Math.min(95, prev + (Math.random() * 10 - 5))))
      setMemUsage(prev => Math.max(30, Math.min(90, prev + (Math.random() * 4 - 2))))
      setLiveRequests(prev => Math.max(5, Math.min(50, prev + Math.floor(Math.random() * 6 - 3))))
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  if (authLoading || loading) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-sm font-black text-muted-foreground uppercase tracking-[0.2em] animate-pulse">Neural Root Access...</p>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <section className="container mx-auto max-w-[1600px] px-4 py-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-2xl bg-primary flex items-center justify-center text-white shadow-xl shadow-primary/30">
                <Shield className="h-7 w-7" />
              </div>
              <div>
                <h1 className="text-3xl font-black tracking-tighter uppercase">Command Center</h1>
                <div className="flex items-center gap-2">
                  <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase tracking-widest border border-emerald-500/20">
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    System Live
                  </span>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Global Node v4.2.0</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-3 bg-muted/30 p-2 rounded-2xl border border-border/50">
             <div className="flex items-center gap-4 px-4 border-r border-border/50">
                <LiveMetric label="CPU" value={`${cpuUsage.toFixed(0)}%`} icon={<Cpu className="h-3 w-3" />} color="text-blue-500" />
                <LiveMetric label="MEM" value={`${memUsage.toFixed(0)}%`} icon={<Activity className="h-3 w-3" />} color="text-purple-500" />
                <LiveMetric label="REQ" value={liveRequests} icon={<Globe className="h-3 w-3" />} color="text-emerald-500" />
             </div>
             <div className="flex gap-2">
                <button onClick={() => loadData(true)} disabled={refreshing} className="btn btn-outline h-10 px-4 rounded-xl gap-2 font-bold text-xs">
                  <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
                  Sync Core
                </button>
                <Link href="/admin/audit-logs" className="btn btn-primary h-10 px-5 rounded-xl gap-2 font-bold text-xs shadow-lg shadow-primary/20">
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
            trend="+14.2%" 
            up={true}
            description="Across all vectors"
            chartData={chartData.slice(-10)}
            dataKey="analyses"
            color="#3b82f6"
          />
          <StatCardLarge 
            label="Active Nodes" 
            value={analytics?.active_users_today || 0} 
            trend="+5.8%" 
            up={true}
            description="Concurrent sessions"
            chartData={chartData.slice(-10)}
            dataKey="load"
            color="#8b5cf6"
          />
          <StatCardLarge 
            label="System Latency" 
            value={`${(chartData[chartData.length-1].latency)}ms`} 
            trend="-12ms" 
            up={true}
            description="Average response time"
            chartData={chartData.slice(-10)}
            dataKey="latency"
            color="#10b981"
          />
          <StatCardLarge 
            label="Success Rate" 
            value={`${((1 - (analytics?.failed_analyses || 0) / (analytics?.total_analyses || 1)) * 100).toFixed(1)}%`} 
            trend="+0.2%" 
            up={true}
            description="Inference stability"
            chartData={chartData.slice(-10)}
            dataKey="analyses" // Just for visual
            color="#f59e0b"
          />
        </div>

        {/* Charts Section */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Real-time Traffic */}
          <div className="lg:col-span-2 card p-8 space-y-8 shadow-2xl shadow-black/5 border-border/40 bg-gradient-to-br from-card to-card/50">
            <div className="flex items-center justify-between">
               <div>
                 <h2 className="text-xl font-black uppercase tracking-tight">Neural Traffic Flow</h2>
                 <p className="text-xs text-muted-foreground font-bold uppercase tracking-widest mt-1">Real-time analysis & load telemetry</p>
               </div>
               <div className="flex gap-6">
                  <LegendItem color="#3b82f6" label="Analyses" />
                  <LegendItem color="#8b5cf6" label="System Load" />
               </div>
            </div>
            
            <div className="h-[350px] w-full">
               <ResponsiveContainer width="100%" height="100%">
                 <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorAnalyses" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
                    <XAxis 
                      dataKey="time" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fontSize: 10, fontWeight: '900', fill: '#666' }}
                      dy={10}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fontSize: 10, fontWeight: '900', fill: '#666' }}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#000', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', fontSize: '12px', fontWeight: 'bold' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area type="monotone" dataKey="analyses" stroke="#3b82f6" strokeWidth={4} fillOpacity={1} fill="url(#colorAnalyses)" animationDuration={1000} />
                    <Area type="monotone" dataKey="load" stroke="#8b5cf6" strokeWidth={4} fillOpacity={1} fill="url(#colorLoad)" animationDuration={1000} />
                 </AreaChart>
               </ResponsiveContainer>
            </div>
          </div>

          {/* Plan Distribution & Live Feed */}
          <div className="space-y-8">
            <div className="card p-8 space-y-6 shadow-xl border-border/40">
               <h2 className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground">Plan Distribution</h2>
               <div className="h-[200px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={analytics?.plan_distribution || []}
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={8}
                        dataKey="value"
                      >
                        {analytics?.plan_distribution?.map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
               </div>
               <div className="grid grid-cols-2 gap-2">
                  {analytics?.plan_distribution?.map((entry: any, index: number) => (
                    <div key={entry.name} className="flex items-center gap-2 p-2 rounded-xl bg-muted/30 border border-border/50">
                       <div className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                       <span className="text-[10px] font-black uppercase tracking-tighter truncate">{entry.name}</span>
                       <span className="ml-auto text-[10px] font-bold opacity-60">{entry.value}</span>
                    </div>
                  ))}
               </div>
            </div>

            <div className="card p-8 space-y-6 shadow-xl border-border/40 overflow-hidden relative">
               <div className="flex items-center justify-between">
                  <h2 className="text-sm font-black uppercase tracking-[0.2em] text-muted-foreground">Live Protocol Feed</h2>
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
               </div>
               <div className="space-y-4">
                  {auditLogs.slice(0, 5).map((log, i) => (
                    <motion.div 
                      key={log.id} 
                      initial={{ opacity: 0, x: 20 }} 
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="flex gap-3 text-[10px]"
                    >
                       <div className="mt-1 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                       <div className="space-y-1">
                          <p className="font-bold text-foreground leading-tight">{log.description}</p>
                          <p className="text-muted-foreground opacity-60 font-medium uppercase tracking-tighter">
                            {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })} • {log.actor_email?.split('@')[0] || 'SYSTEM'}
                          </p>
                       </div>
                    </motion.div>
                  ))}
               </div>
               <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-card to-transparent pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Core Repository */}
        <div className="card overflow-hidden border-border/40 shadow-2xl shadow-black/5 bg-card/50">
          <div className="p-8 border-b border-border/40 flex flex-col xl:flex-row xl:items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-2xl bg-muted border border-border/50 flex items-center justify-center">
                <Users className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-2xl font-black uppercase tracking-tight">Identity Repository</h2>
                <p className="text-xs text-muted-foreground font-bold uppercase tracking-widest">Manage authorization nodes & resources</p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-3">
               <div className="relative">
                 <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                 <input 
                  type="text" 
                  placeholder="Scan Identities..." 
                  className="input-field h-12 pl-12 w-80 bg-background/50 text-sm font-bold border-border/50"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                 />
               </div>
               <button className="btn btn-outline h-12 px-6 rounded-2xl border-border/50 hover:bg-muted font-black text-[10px] uppercase tracking-widest gap-2">
                 <Filter className="h-4 w-4" />
                 Parameters
               </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground bg-muted/20 border-b border-border/40">
                <tr>
                  <th className="px-8 py-5">Identity Vector</th>
                  <th className="px-8 py-5">Authorization</th>
                  <th className="px-8 py-5">Analysis Quota</th>
                  <th className="px-8 py-5">Last Link</th>
                  <th className="px-8 py-5 text-right">Protocol</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40">
                {usersResponse?.data.map((u) => (
                  <tr key={u.id} className="hover:bg-primary/[0.02] transition-colors group">
                    <td className="px-8 py-6">
                       <div className="flex items-center gap-4">
                          <div className="h-11 w-11 rounded-2xl bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center font-black text-xs text-primary border border-primary/10 shadow-sm group-hover:scale-110 transition-transform">
                             {u.email[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="font-black text-foreground text-sm">{u.email}</p>
                            <p className="text-[10px] font-bold text-muted-foreground tracking-widest uppercase opacity-60">ID: #{u.id}</p>
                          </div>
                       </div>
                    </td>
                    <td className="px-8 py-6">
                       <div className="flex flex-col gap-1.5">
                          <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase w-fit tracking-widest border shadow-sm ${
                            u.plan === 'enterprise' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                            u.plan === 'pro' ? 'bg-purple-500/10 text-purple-500 border-purple-500/20' :
                            'bg-muted text-muted-foreground border-border/50'
                          }`}>
                            {u.plan} Deployment
                          </span>
                          <span className="text-[9px] font-black text-muted-foreground ml-1 uppercase tracking-tighter flex items-center gap-1">
                            <Shield className="h-2.5 w-2.5" /> {u.role}
                          </span>
                       </div>
                    </td>
                    <td className="px-8 py-6">
                       <div className="space-y-2">
                          <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                             <span>Load {(u.daily_used / u.daily_limit * 100).toFixed(0)}%</span>
                             <span>{u.daily_used} / {u.daily_limit}</span>
                          </div>
                          <div className="w-48 h-1.5 bg-muted rounded-full overflow-hidden border border-border/10">
                             <motion.div 
                                className={`h-full ${u.daily_used / u.daily_limit > 0.8 ? 'bg-red-500' : 'bg-primary'}`}
                                initial={{ width: 0 }}
                                animate={{ width: `${(u.daily_used / u.daily_limit) * 100}%` }}
                                transition={{ duration: 1 }}
                             />
                          </div>
                       </div>
                    </td>
                    <td className="px-8 py-6 font-bold text-muted-foreground text-xs uppercase tracking-tighter">
                       {formatDistanceToNow(new Date(u.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-8 py-6 text-right">
                       <button className="p-3 rounded-2xl hover:bg-primary/10 text-muted-foreground hover:text-primary transition-all group-hover:rotate-90">
                          <Settings className="h-5 w-5" />
                       </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </AppShell>
  )
}

function LiveMetric({ label, value, icon, color }: any) {
  return (
    <div className="flex flex-col gap-0.5">
       <div className="flex items-center gap-1.5 opacity-60">
          <span className={color}>{icon}</span>
          <span className="text-[8px] font-black uppercase tracking-widest">{label}</span>
       </div>
       <p className="text-xs font-black font-mono leading-none">{value}</p>
    </div>
  )
}

function StatCardLarge({ label, value, trend, up, description, chartData, dataKey, color }: any) {
  return (
    <div className="card p-8 space-y-6 group hover:border-primary/50 transition-all shadow-xl shadow-black/5 bg-gradient-to-br from-card to-card/50 overflow-hidden relative">
       <div className="relative z-10 space-y-4">
          <div className="flex items-center justify-between">
             <div className="space-y-1">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground opacity-60">{label}</p>
                <p className="text-3xl font-black tracking-tighter">{value}</p>
             </div>
             <div className={`flex items-center gap-1 text-[10px] font-black px-2 py-1 rounded-full border shadow-sm ${
               up ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'
             }`}>
               {up ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
               {trend}
             </div>
          </div>
          <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{description}</p>
       </div>
       
       <div className="h-[60px] w-full mt-4 -mx-2">
          <ResponsiveContainer width="100%" height="100%">
             <LineChart data={chartData}>
                <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={3} dot={false} animationDuration={2000} />
             </LineChart>
          </ResponsiveContainer>
       </div>
    </div>
  )
}

function LegendItem({ color, label }: { color: string, label: string }) {
  return (
    <div className="flex items-center gap-2">
       <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
       <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{label}</span>
    </div>
  )
}
