"use client"

import { useEffect, useState, useMemo } from "react"
import { 
  Download, Filter, RefreshCw, Search, 
  ExternalLink, FileText, CheckCircle2, 
  AlertCircle, Clock, ChevronRight, BarChart2,
  X, FilterX
} from "lucide-react"
import { AppShell } from "@/components/AppShell"
import { useAuth } from "@/contexts/auth-context"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { fetchAnalysisHistory } from "@/lib/api-client"
import type { AnalysisHistoryItem } from "@/types/api"
import { motion, AnimatePresence } from "framer-motion"
import { formatDistanceToNow } from "date-fns"

const PLATFORMS = [
  { id: "youtube", label: "YouTube" },
  { id: "telegram", label: "Telegram" },
  { id: "instagram", label: "Instagram" },
  { id: "tiktok", label: "TikTok" },
  { id: "vk", label: "VK" },
  { id: "file", label: "File Upload" },
]

const STATUSES = [
  { id: "completed", label: "Completed" },
  { id: "failed", label: "Failed" },
  { id: "processing", label: "Processing" },
]

function getSourceTypeName(sourceType: string): string {
  const typeMap: Record<string, string> = {
    file: "Local Upload",
    url: "Direct Link",
    youtube: "YouTube",
    telegram: "Telegram",
    instagram: "Instagram",
    tiktok: "TikTok",
    vk: "VK",
  }
  return typeMap[sourceType.toLowerCase()] || sourceType
}

export default function HistoryPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  
  // Filter state
  const [searchQuery, setSearchQuery] = useState("")
  const [platformFilter, setPlatformFilter] = useState<string>("")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [showFilters, setShowFilters] = useState(false)

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
      const data = await fetchAnalysisHistory({ limit: 100 })
      setHistory(data)
    } catch (error: any) {
      console.error("Failed to load history:", error)
      if (error.response?.status === 401) {
        toast.error("Session expired")
        router.push("/auth/login")
      } else {
        toast.error("Failed to load history")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const filteredHistory = useMemo(() => {
    return history.filter(item => {
      const matchesSearch = item.task_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.source_type.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesPlatform = !platformFilter || item.source_type.toLowerCase() === platformFilter.toLowerCase()
      const matchesStatus = !statusFilter || item.status.toLowerCase() === statusFilter.toLowerCase()
      
      return matchesSearch && matchesPlatform && matchesStatus
    })
  }, [history, searchQuery, platformFilter, statusFilter])

  const clearFilters = () => {
    setSearchQuery("")
    setPlatformFilter("")
    setStatusFilter("")
  }

  return (
    <AppShell>
      <section className="container mx-auto max-w-6xl px-4 py-12 space-y-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1">
            <h1 className="text-4xl font-extrabold tracking-tight">Analysis Archive</h1>
            <p className="text-muted-foreground font-medium">Detailed history of all your compliance checks and generated reports.</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={loadHistory}
              disabled={isLoading}
              className="btn btn-outline h-11 px-4 rounded-xl gap-2 font-bold transition-all hover:bg-muted"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <button className="btn btn-primary h-11 px-6 rounded-xl gap-2 font-bold shadow-lg shadow-primary/20" disabled={history.length === 0}>
              <Download className="h-4 w-4" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Search by Task ID..."
                className="input-field pl-12 h-12 bg-card border-border shadow-sm focus:border-primary/50 transition-all font-medium"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className={`btn h-12 px-6 rounded-xl gap-2 font-bold border shadow-sm transition-all ${showFilters ? 'bg-primary text-white border-primary shadow-primary/20' : 'bg-card border-border hover:bg-muted'}`}
            >
              <Filter className="h-4 w-4" />
              {showFilters ? 'Hide Filters' : 'Filters'}
              {(platformFilter || statusFilter) && (
                <span className="ml-1 px-1.5 py-0.5 bg-white/20 rounded-full text-[10px]">!</span>
              )}
            </button>
          </div>

          <AnimatePresence>
            {showFilters && (
              <motion.div 
                initial={{ opacity: 0, height: 0, y: -10 }}
                animate={{ opacity: 1, height: 'auto', y: 0 }}
                exit={{ opacity: 0, height: 0, y: -10 }}
                className="overflow-hidden"
              >
                <div className="p-6 bg-muted/30 rounded-2xl border border-dashed border-border/50 grid grid-cols-1 md:grid-cols-3 gap-6">
                   <div className="space-y-2">
                      <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">Platform Origin</label>
                      <select 
                        value={platformFilter} 
                        onChange={(e) => setPlatformFilter(e.target.value)}
                        className="input-field h-11 bg-background text-sm font-bold"
                      >
                        <option value="">All Platforms</option>
                        {PLATFORMS.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
                      </select>
                   </div>
                   <div className="space-y-2">
                      <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">Processing Status</label>
                      <select 
                        value={statusFilter} 
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="input-field h-11 bg-background text-sm font-bold"
                      >
                        <option value="">All Statuses</option>
                        {STATUSES.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                      </select>
                   </div>
                   <div className="flex items-end">
                      <button 
                        onClick={clearFilters}
                        disabled={!platformFilter && !statusFilter && !searchQuery}
                        className="btn btn-ghost h-11 w-full gap-2 text-xs font-black uppercase tracking-widest disabled:opacity-30"
                      >
                        <FilterX className="h-4 w-4" />
                        Reset All Filters
                      </button>
                   </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Table/List */}
        <div className="card overflow-hidden border-border/50 shadow-2xl shadow-black/5">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-muted/30 text-muted-foreground font-black uppercase tracking-widest text-[10px] border-b border-border/50">
                <tr>
                  <th className="px-6 py-4">Status & ID</th>
                  <th className="px-6 py-4">Source Platform</th>
                  <th className="px-6 py-4 text-center">Confidence</th>
                  <th className="px-6 py-4">Compliance Verdict</th>
                  <th className="px-6 py-4">Sync Date</th>
                  <th className="px-6 py-4"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50 bg-card">
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={6} className="px-6 py-8">
                        <div className="flex items-center gap-4">
                          <div className="h-10 w-10 bg-muted rounded-xl" />
                          <div className="space-y-2">
                            <div className="h-4 w-40 bg-muted rounded" />
                            <div className="h-3 w-24 bg-muted rounded" />
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : filteredHistory.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-24 text-center">
                      <div className="max-w-xs mx-auto space-y-4">
                        <div className="bg-muted h-20 w-20 rounded-3xl flex items-center justify-center mx-auto border-2 border-dashed border-border/50">
                           <FileText className="h-10 w-10 text-muted-foreground/50" />
                        </div>
                        <div className="space-y-1">
                          <h3 className="text-xl font-black tracking-tight">No Records Located</h3>
                          <p className="text-sm text-muted-foreground font-medium">
                            {searchQuery || platformFilter || statusFilter 
                              ? "Zero matches found for active filter parameters." 
                              : "The neural archive is currently empty. Start a new analysis to populate history."}
                          </p>
                        </div>
                        <button 
                          onClick={() => { clearFilters(); router.push("/analyze") }} 
                          className="btn btn-primary h-11 px-8 rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg shadow-primary/20"
                        >
                          {searchQuery || platformFilter || statusFilter ? "Clear Filters" : "New Analysis"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredHistory.map((item, index) => (
                    <motion.tr 
                      key={item.task_id}
                      className="hover:bg-muted/30 transition-colors group cursor-pointer active:bg-muted/50"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.01 }}
                      onClick={() => router.push(`/analyze?taskId=${item.task_id}`)}
                    >
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-4">
                           <div className={`h-10 w-10 rounded-xl flex items-center justify-center border border-border/50 bg-background shadow-sm ${
                             item.status === 'completed' ? 'text-emerald-500' :
                             item.status === 'failed' ? 'text-red-500' :
                             'text-blue-500'
                           }`}>
                             {item.status === 'completed' ? <CheckCircle2 className="h-5 w-5" /> :
                              item.status === 'failed' ? <AlertCircle className="h-5 w-5" /> :
                              <RefreshCw className="h-5 w-5 animate-spin" />}
                           </div>
                           <div>
                             <p className="font-bold text-foreground">Task {item.task_id.slice(0, 8)}</p>
                             <div className="flex items-center gap-2">
                                <span className={`text-[10px] font-black uppercase tracking-tighter ${
                                  item.status === 'completed' ? 'text-emerald-600' :
                                  item.status === 'failed' ? 'text-red-500' :
                                  'text-blue-500'
                                }`}>
                                  {item.status}
                                </span>
                             </div>
                           </div>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <span className="inline-flex items-center px-3 py-1 rounded-lg bg-muted text-foreground text-[10px] font-black uppercase tracking-widest border border-border/50">
                          {getSourceTypeName(item.source_type)}
                        </span>
                      </td>
                      <td className="px-6 py-5 text-center">
                        {item.status === "completed" && item.confidence_score !== null ? (
                          <div className="space-y-1 w-20 mx-auto">
                            <span className="text-xs font-black text-primary">
                              {Math.round(item.confidence_score * 100)}%
                            </span>
                            <div className="w-full h-1 bg-muted rounded-full overflow-hidden">
                              <div className="h-full bg-primary" style={{ width: `${item.confidence_score * 100}%` }} />
                            </div>
                          </div>
                        ) : (
                          <span className="text-muted-foreground font-black text-[10px]">--</span>
                        )}
                      </td>
                      <td className="px-6 py-5">
                        {item.status === "completed" ? (
                          item.has_advertising ? (
                            <span className="inline-flex items-center gap-1.5 text-red-500 font-black text-[10px] uppercase tracking-widest">
                              <AlertCircle className="h-3 w-3" /> ADVERTISING
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-emerald-500 font-black text-[10px] uppercase tracking-widest">
                              <CheckCircle2 className="h-3 w-3" /> CLEAN NODE
                            </span>
                          )
                        ) : (
                          <span className="text-muted-foreground italic text-[10px] font-bold uppercase tracking-widest animate-pulse">PENDING...</span>
                        )}
                      </td>
                      <td className="px-6 py-5">
                        <div className="space-y-0.5">
                          <p className="text-xs font-bold text-foreground">
                            {new Date(item.created_at).toLocaleDateString()}
                          </p>
                          <p className="text-[9px] font-black text-muted-foreground flex items-center gap-1 uppercase tracking-tighter">
                            <Clock className="h-2.5 w-2.5" />
                            {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <button 
                          className="p-2.5 rounded-xl hover:bg-primary/10 text-muted-foreground hover:text-primary transition-all group-hover:scale-110 shadow-sm border border-transparent hover:border-border/50 bg-muted/20"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/analyze?taskId=${item.task_id}`);
                          }}
                        >
                           <ChevronRight className="h-4 w-4" />
                        </button>
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          <div className="px-6 py-4 bg-muted/10 border-t border-border/50 flex items-center justify-between">
             <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
               Visible: {filteredHistory.length} / Total: {history.length}
             </span>
             <div className="flex gap-2">
                <button disabled className="btn btn-outline btn-sm h-9 px-4 rounded-lg font-bold disabled:opacity-30">Prev</button>
                <button disabled className="btn btn-outline btn-sm h-9 px-4 rounded-lg font-bold disabled:opacity-30">Next</button>
             </div>
          </div>
        </div>
      </section>
    </AppShell>
  )
}
