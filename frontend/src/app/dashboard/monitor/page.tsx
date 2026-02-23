"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Plus, Search, Activity, PauseCircle, PlayCircle, MoreHorizontal, Settings2, Trash2 } from "lucide-react"

// Mock data
const monitors = [
  { id: 1, name: "Competitor Watch: BetBoom", status: "active", sources: ["YouTube", "Telegram"], hits: 142, lastCheck: "2 min ago" },
  { id: 2, name: "Category: Crypto Scams", status: "active", sources: ["Telegram"], hits: 853, lastCheck: "1 min ago" },
  { id: 3, name: "Brand Safety: Nike (Official)", status: "paused", sources: ["Instagram", "TikTok"], hits: 45, lastCheck: "2 days ago" },
]

export default function MonitorPage() {
  const [activeTab, setActiveTab] = useState("all")

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Brand Intelligence</h1>
          <p className="text-muted-foreground mt-1">
            Proactively monitor keywords and brands across social platforms.
          </p>
        </div>
        <button className="btn btn-primary shadow-lg shadow-primary/20">
          <Plus className="mr-2 h-4 w-4" />
          New Monitor
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-6 space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">Active Monitors</h3>
          <div className="text-2xl font-bold">12</div>
          <div className="text-xs text-emerald-500 flex items-center gap-1">
            <Activity className="h-3 w-3" />
            Running smoothly
          </div>
        </div>
        <div className="card p-6 space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">Total Detections (24h)</h3>
          <div className="text-2xl font-bold">1,248</div>
          <div className="text-xs text-muted-foreground">+12% from yesterday</div>
        </div>
        <div className="card p-6 space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">API Usage</h3>
          <div className="text-2xl font-bold">85%</div>
          <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden mt-2">
            <div className="bg-primary h-full w-[85%] rounded-full" />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 bg-muted/50 p-1 rounded-lg">
            <button 
              onClick={() => setActiveTab("all")}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === "all" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            >
              All Monitors
            </button>
            <button 
              onClick={() => setActiveTab("active")}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === "active" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            >
              Active
            </button>
            <button 
              onClick={() => setActiveTab("paused")}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === "paused" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            >
              Paused
            </button>
          </div>
          
          <div className="relative w-full max-w-sm hidden sm:block">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Filter monitors..."
              className="input-field pl-9"
            />
          </div>
        </div>

        <div className="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden">
          <div className="relative w-full overflow-auto">
            <table className="w-full caption-bottom text-sm">
              <thead className="[&_tr]:border-b">
                <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[300px]">Name</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Sources</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Hits (24h)</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Last Check</th>
                  <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="[&_tr:last-child]:border-0">
                {monitors.map((monitor) => (
                  <tr key={monitor.id} className="border-b transition-colors hover:bg-muted/50">
                    <td className="p-4 align-middle font-medium">{monitor.name}</td>
                    <td className="p-4 align-middle">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${
                        monitor.status === 'active' 
                          ? 'border-transparent bg-emerald-500/10 text-emerald-500' 
                          : 'border-transparent bg-yellow-500/10 text-yellow-500'
                      }`}>
                        {monitor.status === 'active' && <span className="mr-1.5 flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />}
                        {monitor.status.charAt(0).toUpperCase() + monitor.status.slice(1)}
                      </span>
                    </td>
                    <td className="p-4 align-middle text-muted-foreground">
                      <div className="flex gap-1">
                        {monitor.sources.map(src => (
                          <span key={src} className="border px-1.5 py-0.5 rounded text-xs bg-muted/50">
                            {src}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="p-4 align-middle font-mono">{monitor.hits}</td>
                    <td className="p-4 align-middle text-muted-foreground">{monitor.lastCheck}</td>
                    <td className="p-4 align-middle text-right">
                      <div className="flex justify-end gap-2">
                        <button className="btn btn-ghost h-8 w-8 p-0">
                          {monitor.status === 'active' ? <PauseCircle className="h-4 w-4" /> : <PlayCircle className="h-4 w-4" />}
                        </button>
                        <button className="btn btn-ghost h-8 w-8 p-0 text-muted-foreground hover:text-foreground">
                          <Settings2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
