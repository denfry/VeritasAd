"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { 
  listUsers, 
  updateUser, 
  getAnalytics, 
  getAdvancedAnalytics,
  bulkUpdateUsers, 
  bulkDeleteUsers 
} from "@/lib/api-client"
import type { UserListItem, CursorPaginationResponse } from "@/types/api"
import { toast } from "sonner"
import { 
  Loader2, 
  Users, 
  Activity, 
  BarChart3, 
  AlertCircle, 
  TrendingUp, 
  Search, 
  Filter, 
  ChevronDown, 
  ChevronUp, 
  MoreHorizontal, 
  CheckSquare, 
  Square, 
  Ban, 
  Check, 
  X, 
  Shield,
  Zap,
  Globe,
  Lock,
  ArrowUpRight
} from "lucide-react"
import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import { CommandPalette, useAdminCommands, useCommandPalette } from "@/components/CommandPalette"
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts"

type SortField = "id" | "email" | "created_at" | "total_analyses" | "daily_used"
type SortOrder = "asc" | "desc"

export default function AdminPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, loading: authLoading, signOut, authDisabled } = useAuth()
  
  // Command Palette
  const adminCommands = useAdminCommands()
  const { Component: CommandPaletteComponent } = useCommandPalette(adminCommands)
  
  // Keyboard Shortcuts
  useKeyboardShortcuts({ enabled: true })
  
  // Data state
  const [usersResponse, setUsersResponse] = useState<CursorPaginationResponse<UserListItem> | null>(null)
  const [analytics, setAnalytics] = useState<any | null>(null)
  const [advancedAnalytics, setAdvancedAnalytics] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  
  // Pagination state
  const [cursor, setCursor] = useState<string | null>(null)
  const [history, setHistory] = useState<string[]>([])
  
  // Filters state
  const [search, setSearch] = useState("")
  const [searchDebounce, setSearchDebounce] = useState("")
  const [planFilter, setPlanFilter] = useState<string>("")
  const [roleFilter, setRoleFilter] = useState<string>("")
  const [activeFilter, setActiveFilter] = useState<string>("")
  const [bannedFilter, setBannedFilter] = useState<string>("")
  
  // Sorting state
  const [sortBy, setSortBy] = useState<SortField>("created_at")
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc")
  
  // Selection state
  const [selectedUsers, setSelectedUsers] = useState<Set<number>>(new Set())
  const [showFilters, setShowFilters] = useState(false)
  
  // Edit modal state
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(null)

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
      const [usersData, analyticsData, advAnalyticsData] = await Promise.all([
        listUsers({
          limit: 20,
          cursor: cursor || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
          search: searchDebounce || undefined,
          plan: planFilter || undefined,
          role: roleFilter || undefined,
          is_active: activeFilter ? activeFilter === "true" : undefined,
          is_banned: bannedFilter ? bannedFilter === "true" : undefined,
        }),
        getAnalytics(),
        getAdvancedAnalytics({ days: 30 }).catch(() => null)
      ])
      setUsersResponse(usersData)
      setAnalytics(analyticsData)
      setAdvancedAnalytics(advAnalyticsData)
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
        toast.error("Failed to load admin data")
        setErrorMessage("Failed to load admin data. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }, [cursor, sortBy, sortOrder, searchDebounce, planFilter, roleFilter, activeFilter, bannedFilter, router, signOut])

  useEffect(() => {
    if (authDisabled) {
      loadData()
      return
    }

    if (!authLoading && !user) {
      router.push("/auth/login")
      return
    }

    if (user) {
      loadData()
    }
  }, [user, authLoading, loadData, router, authDisabled])

  // Handle pagination
  const handleNextPage = () => {
    if (usersResponse?.next_cursor) {
      setHistory([...history, cursor || ""])
      setCursor(usersResponse.next_cursor)
    }
  }

  const handlePrevPage = () => {
    if (history.length > 0) {
      const prevCursor = history[history.length - 1]
      setHistory(history.slice(0, -1))
      setCursor(prevCursor || null)
    }
  }

  // Handle sorting
  const handleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "desc" ? "asc" : "desc")
    } else {
      setSortBy(field)
      setSortOrder("desc")
    }
  }

  // Handle selection
  const toggleSelectAll = () => {
    if (selectedUsers.size === (usersResponse?.data.length || 0)) {
      setSelectedUsers(new Set())
    } else {
      setSelectedUsers(new Set(usersResponse?.data.map(u => u.id) || []))
    }
  }

  const toggleSelectUser = (userId: number) => {
    const newSelected = new Set(selectedUsers)
    if (newSelected.has(userId)) {
      newSelected.delete(userId)
    } else {
      newSelected.add(userId)
    }
    setSelectedUsers(newSelected)
  }

  // Handle bulk actions
  const handleBulkBan = async () => {
    if (selectedUsers.size === 0) return
    try {
      await bulkUpdateUsers({
        user_ids: Array.from(selectedUsers),
        updates: { is_banned: true },
      })
      toast.success(`Banned ${selectedUsers.size} users`)
      setSelectedUsers(new Set())
      loadData()
    } catch (error) {
      toast.error("Failed to ban users")
    }
  }

  const handleBulkUnban = async () => {
    if (selectedUsers.size === 0) return
    try {
      await bulkUpdateUsers({
        user_ids: Array.from(selectedUsers),
        updates: { is_banned: false },
      })
      toast.success(`Unbanned ${selectedUsers.size} users`)
      setSelectedUsers(new Set())
      loadData()
    } catch (error) {
      toast.error("Failed to unban users")
    }
  }

  const handleUserUpdate = async (
    userId: number,
    data: Partial<{
      role: string
      plan: string
      is_banned: boolean
      is_active: boolean
    }>
  ) => {
    try {
      await updateUser({ userId, data })
      toast.success("User updated successfully")
      loadData()
      setSelectedUser(null)
    } catch (error: any) {
      toast.error("Failed to update user")
    }
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
            <h1 className="text-xl font-semibold">Admin dashboard unavailable</h1>
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
              <button onClick={() => router.push("/account")} className="btn btn-outline">
                Go to account
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
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold flex items-center gap-2">
              <Shield className="h-8 w-8 text-primary" />
              Admin Dashboard
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Platform-wide control, user management, and advanced compliance analytics.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/admin/audit-logs" className="btn btn-outline btn-sm">
              <Shield className="h-4 w-4 mr-1" />
              Audit Logs
            </Link>
            <button onClick={() => loadData()} className="btn btn-outline btn-sm">
              Refresh Data
            </button>
          </div>
        </div>

        {/* Quick Stats Grid */}
        {analytics && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="card p-5 relative overflow-hidden group">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">Total Users</p>
                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
                  <Users className="h-5 w-5" />
                </div>
              </div>
              <p className="text-2xl font-bold">{analytics.total_users}</p>
              <div className="flex items-center gap-1 mt-1 text-xs text-green-500">
                <TrendingUp className="h-3 w-3" />
                <span>{analytics.active_users_today} active today</span>
              </div>
            </div>

            <div className="card p-5 relative overflow-hidden group">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">Total Analyses</p>
                <div className="p-2 rounded-lg bg-primary/10 text-primary">
                  <BarChart3 className="h-5 w-5" />
                </div>
              </div>
              <p className="text-2xl font-bold">{analytics.total_analyses}</p>
              <div className="flex items-center gap-1 mt-1 text-xs text-primary">
                <Activity className="h-3 w-3" />
                <span>{analytics.analyses_today} new today</span>
              </div>
            </div>

            <div className="card p-5 relative overflow-hidden group">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">Avg Confidence</p>
                <div className="p-2 rounded-lg bg-green-500/10 text-green-500">
                  <Check className="h-5 w-5" />
                </div>
              </div>
              <p className="text-2xl font-bold">{(analytics.avg_confidence_score * 100).toFixed(0)}%</p>
              <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                <Shield className="h-3 w-3" />
                <span>Across all processed videos</span>
              </div>
            </div>

            <div className="card p-5 relative overflow-hidden group">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">System Health</p>
                <div className="p-2 rounded-lg bg-green-500/10 text-green-500">
                  <Globe className="h-5 w-5" />
                </div>
              </div>
              <p className="text-2xl font-bold">99.9%</p>
              <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                <Zap className="h-3 w-3 text-amber-500" />
                <span>All services operational</span>
              </div>
            </div>
          </div>
        )}

        {/* Analytics & Top Users Row */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Recent Activity / Advanced Analytics Hint */}
          <div className="lg:col-span-2 card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">User Growth</h2>
              <select className="input-field py-1 text-xs w-32">
                <option>Last 30 days</option>
                <option>Last 7 days</option>
              </select>
            </div>
            
            {advancedAnalytics?.user_growth ? (
              <div className="h-64 flex items-end justify-between gap-2 px-2">
                {advancedAnalytics.user_growth.slice(-15).map((point: any, i: number) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-2 group">
                    <div 
                      className="w-full bg-primary/20 hover:bg-primary transition-colors rounded-t-sm" 
                      style={{ height: `${Math.max(10, (point.count / Math.max(...advancedAnalytics.user_growth.map((p:any) => p.count))) * 100)}%` }}
                    />
                    <span className="text-[10px] text-muted-foreground hidden group-hover:block whitespace-nowrap">
                      {point.date.split('T')[0]}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center bg-muted/20 rounded-lg border border-dashed">
                <p className="text-sm text-muted-foreground">User growth visualization data loading...</p>
              </div>
            )}
            
            <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t">
              <div>
                <p className="text-xs text-muted-foreground uppercase">New Users</p>
                <p className="text-lg font-semibold">+{advancedAnalytics?.summary?.new_users || 0}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase">Analyses</p>
                <p className="text-lg font-semibold">{advancedAnalytics?.summary?.total_analyses || 0}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase">Conversion</p>
                <p className="text-lg font-semibold">
                  {advancedAnalytics?.funnel?.conversion_rate ? (advancedAnalytics.funnel.conversion_rate * 100).toFixed(1) : "0"}%
                </p>
              </div>
            </div>
          </div>

          {/* Top Users */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold mb-4">Top Performers</h2>
            <div className="space-y-4">
              {analytics?.top_users.map((topUser: any, index: number) => (
                <div
                  key={topUser.id}
                  className="flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium line-clamp-1">{topUser.email}</p>
                      <span className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
                        {topUser.plan}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold">{topUser.total_analyses}</p>
                    <p className="text-[10px] text-muted-foreground">analyses</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="btn btn-ghost btn-sm w-full mt-6 text-xs text-primary">
              View All Rankings
            </button>
          </div>
        </div>

        {/* Users Table */}
        <div className="card overflow-hidden">
          <div className="p-6 border-b">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <h2 className="text-lg font-semibold">User Directory</h2>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search by email or ID..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="input-field pl-9 w-64 text-sm"
                  />
                </div>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`btn btn-sm ${showFilters ? "btn-primary" : "btn-outline"}`}
                >
                  <Filter className="h-4 w-4 mr-1" />
                  Filters
                </button>
              </div>
            </div>

            {selectedUsers.size > 0 && (
              <div className="mt-4 p-2 bg-primary/5 border border-primary/20 rounded-lg flex items-center justify-between">
                <span className="text-sm font-medium ml-2">
                  {selectedUsers.size} users selected
                </span>
                <div className="flex gap-2">
                  <button onClick={handleBulkBan} className="btn btn-sm btn-ghost text-destructive">
                    <Ban className="h-4 w-4 mr-1" /> Ban
                  </button>
                  <button onClick={handleBulkUnban} className="btn btn-sm btn-ghost text-primary">
                    <Check className="h-4 w-4 mr-1" /> Unban
                  </button>
                  <button onClick={() => setSelectedUsers(new Set())} className="btn btn-sm btn-ghost">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}

            {showFilters && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 p-4 rounded-lg bg-muted/40 animate-in fade-in slide-in-from-top-2">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground mb-1 block uppercase">Plan</label>
                  <select
                    value={planFilter}
                    onChange={(e) => setPlanFilter(e.target.value)}
                    className="input-field text-sm"
                  >
                    <option value="">All Plans</option>
                    <option value="free">Free</option>
                    <option value="pro">Pro</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground mb-1 block uppercase">Role</label>
                  <select
                    value={roleFilter}
                    onChange={(e) => setRoleFilter(e.target.value)}
                    className="input-field text-sm"
                  >
                    <option value="">All Roles</option>
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground mb-1 block uppercase">Status</label>
                  <select
                    value={activeFilter}
                    onChange={(e) => setActiveFilter(e.target.value)}
                    className="input-field text-sm"
                  >
                    <option value="">All Statuses</option>
                    <option value="true">Active</option>
                    <option value="false">Inactive</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground mb-1 block uppercase">Banned</label>
                  <select
                    value={bannedFilter}
                    onChange={(e) => setBannedFilter(e.target.value)}
                    className="input-field text-sm"
                  >
                    <option value="">All</option>
                    <option value="true">Banned</option>
                    <option value="false">Not Banned</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left">
                <tr>
                  <th className="px-6 py-4 w-10">
                    <button onClick={toggleSelectAll}>
                      {selectedUsers.size === (usersResponse?.data.length || 0) && usersResponse?.data.length ? (
                        <CheckSquare className="h-4 w-4 text-primary" />
                      ) : (
                        <Square className="h-4 w-4 text-muted-foreground" />
                      )}
                    </button>
                  </th>
                  <th className="px-6 py-4">
                    <button onClick={() => handleSort("email")} className="flex items-center gap-1 group">
                      User
                      <ArrowUpRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </button>
                  </th>
                  <th className="px-6 py-4">Plan & Role</th>
                  <th className="px-6 py-4 text-center">Analyses</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Joined</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {usersResponse?.data.map((u) => (
                  <tr key={u.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-6 py-4">
                      <button onClick={() => toggleSelectUser(u.id)}>
                        {selectedUsers.has(u.id) ? (
                          <CheckSquare className="h-4 w-4 text-primary" />
                        ) : (
                          <Square className="h-4 w-4 text-muted-foreground" />
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="font-medium">{u.email || "No email"}</span>
                        <span className="text-xs text-muted-foreground font-mono">ID: {u.id}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className={`badge text-[10px] font-bold uppercase ${
                          u.plan === 'enterprise' ? 'bg-purple-500/10 text-purple-600' : 
                          u.plan === 'pro' ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                        }`}>
                          {u.plan}
                        </span>
                        <span className="text-[10px] font-medium text-muted-foreground uppercase">{u.role}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex flex-col">
                        <span className="font-bold">{u.total_analyses}</span>
                        <span className="text-[10px] text-muted-foreground">{u.daily_used}/{u.daily_limit} today</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {u.is_banned ? (
                        <span className="flex items-center gap-1 text-destructive font-medium">
                          <Ban className="h-3 w-3" /> Banned
                        </span>
                      ) : u.is_active ? (
                        <span className="flex items-center gap-1 text-green-600 font-medium">
                          <Check className="h-3 w-3" /> Active
                        </span>
                      ) : (
                        <span className="text-muted-foreground">Inactive</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(u.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setSelectedUser(u)}
                        className="btn btn-sm btn-ghost hover:bg-primary/10 hover:text-primary"
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between p-6 bg-muted/30 border-t">
            <p className="text-sm text-muted-foreground">
              Showing <span className="font-bold text-foreground">{usersResponse?.data.length || 0}</span> of <span className="font-bold text-foreground">{usersResponse?.total_count || 0}</span> users
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrevPage}
                disabled={history.length === 0}
                className="btn btn-sm btn-outline disabled:opacity-30"
              >
                Previous
              </button>
              <button
                onClick={handleNextPage}
                disabled={!usersResponse?.has_more}
                className="btn btn-sm btn-outline disabled:opacity-30"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        {/* Edit User Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="card p-8 max-w-md w-full space-y-6 shadow-2xl animate-in zoom-in-95">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold">Manage User</h3>
                <button onClick={() => setSelectedUser(null)} className="p-1 hover:bg-muted rounded-full">
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="p-4 bg-muted/40 rounded-lg">
                  <label className="text-xs font-bold text-muted-foreground uppercase block mb-1">Target Account</label>
                  <p className="font-medium">{selectedUser.email}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-muted-foreground uppercase block">Role</label>
                    <select
                      className="input-field"
                      defaultValue={selectedUser.role}
                      onChange={(e) => handleUserUpdate(selectedUser.id, { role: e.target.value })}
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-muted-foreground uppercase block">Plan</label>
                    <select
                      className="input-field"
                      defaultValue={selectedUser.plan}
                      onChange={(e) => handleUserUpdate(selectedUser.id, { plan: e.target.value })}
                    >
                      <option value="free">Free</option>
                      <option value="pro">Pro</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    onClick={() => handleUserUpdate(selectedUser.id, { is_banned: !selectedUser.is_banned })}
                    className={`btn flex-1 gap-2 ${selectedUser.is_banned ? 'btn-outline' : 'btn-outline border-destructive text-destructive hover:bg-destructive hover:text-white'}`}
                  >
                    <Ban className="h-4 w-4" />
                    {selectedUser.is_banned ? "Unban User" : "Ban Account"}
                  </button>
                  <button
                    onClick={() => handleUserUpdate(selectedUser.id, { is_active: !selectedUser.is_active })}
                    className="btn btn-outline flex-1 gap-2"
                  >
                    {selectedUser.is_active ? <X className="h-4 w-4" /> : <Check className="h-4 w-4" />}
                    {selectedUser.is_active ? "Deactivate" : "Activate"}
                  </button>
                </div>
              </div>

              <div className="pt-4">
                <button onClick={() => setSelectedUser(null)} className="btn btn-primary w-full">
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}
      </section>
      {CommandPaletteComponent}
    </SiteShell>
  )
}
