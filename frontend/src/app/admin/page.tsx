"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { listUsers, updateUser, getAnalytics, bulkUpdateUsers, bulkDeleteUsers } from "@/lib/api-client"
import type { UserListItem, CursorPaginationResponse } from "@/types/api"
import { toast } from "sonner"
import { Loader2, Users, Activity, BarChart3, AlertCircle, TrendingUp, Search, Filter, ChevronDown, ChevronUp, MoreHorizontal, CheckSquare, Square, Ban, Check, X, Shield } from "lucide-react"
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
      const [usersData, analyticsData] = await Promise.all([
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
      ])
      setUsersResponse(usersData)
      setAnalytics(analyticsData)
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
    // Если авторизация отключена, всё равно загружаем данные
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
        <section className="container mx-auto max-w-6xl px-4 section">
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold">Admin Dashboard</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Manage users and view platform analytics
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/admin/audit-logs" className="btn btn-outline btn-sm">
              <Shield className="h-4 w-4 mr-1" />
              Audit Logs
            </Link>
            <Link href="/account" className="btn btn-outline">
              My Account
            </Link>
          </div>
        </div>

        {/* Analytics Cards */}
        {analytics && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="card card-hover p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Total Users</p>
                <Users className="h-5 w-5 text-primary" />
              </div>
              <p className="mt-2 text-2xl font-semibold">{analytics.total_users}</p>
              <p className="text-xs text-muted-foreground">
                {analytics.active_users_today} active today
              </p>
            </div>

            <div className="card card-hover p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Total Analyses</p>
                <BarChart3 className="h-5 w-5 text-primary" />
              </div>
              <p className="mt-2 text-2xl font-semibold">{analytics.total_analyses}</p>
              <p className="text-xs text-muted-foreground">
                {analytics.analyses_today} today
              </p>
            </div>

            <div className="card card-hover p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Avg Confidence</p>
                <TrendingUp className="h-5 w-5 text-primary" />
              </div>
              <p className="mt-2 text-2xl font-semibold">{analytics.avg_confidence_score}</p>
              <p className="text-xs text-muted-foreground">Completed analyses</p>
            </div>

            <div className="card card-hover p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Failed</p>
                <AlertCircle className="h-5 w-5 text-destructive" />
              </div>
              <p className="mt-2 text-2xl font-semibold">{analytics.failed_analyses}</p>
              <p className="text-xs text-muted-foreground">Error rate</p>
            </div>
          </div>
        )}

        {/* Top Users */}
        {analytics && (
          <div className="card p-6">
            <h2 className="text-lg font-semibold mb-4">Top Users</h2>
            <div className="space-y-2">
              {analytics.top_users.map((topUser: any, index: number) => (
                <div
                  key={topUser.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/40"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground w-6">#{index + 1}</span>
                    <div>
                      <p className="font-medium">{topUser.email}</p>
                      <p className="text-xs text-muted-foreground capitalize">{topUser.plan}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{topUser.total_analyses}</p>
                    <p className="text-xs text-muted-foreground">analyses</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Users Table */}
        <div className="card p-6">
          {/* Toolbar */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search users..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="input-field pl-9 w-64"
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
            
            {selectedUsers.size > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  {selectedUsers.size} selected
                </span>
                <button onClick={handleBulkBan} className="btn btn-sm btn-ghost text-destructive">
                  <Ban className="h-4 w-4 mr-1" />
                  Ban
                </button>
                <button onClick={handleBulkUnban} className="btn btn-sm btn-ghost">
                  <Check className="h-4 w-4 mr-1" />
                  Unban
                </button>
              </div>
            )}
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 rounded-lg bg-muted/40">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Plan</label>
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
                <label className="text-xs text-muted-foreground mb-1 block">Role</label>
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
                <label className="text-xs text-muted-foreground mb-1 block">Status</label>
                <select
                  value={activeFilter}
                  onChange={(e) => setActiveFilter(e.target.value)}
                  className="input-field text-sm"
                >
                  <option value="">All</option>
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Banned</label>
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
              <div className="col-span-2 md:col-span-4 flex justify-end">
                <button
                  onClick={() => {
                    setPlanFilter("")
                    setRoleFilter("")
                    setActiveFilter("")
                    setBannedFilter("")
                    setSearch("")
                  }}
                  className="btn btn-sm btn-ghost"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left">
                <tr>
                  <th className="px-4 py-3 w-10">
                    <button onClick={toggleSelectAll}>
                      {selectedUsers.size === (usersResponse?.data.length || 0) && usersResponse?.data.length ? (
                        <CheckSquare className="h-4 w-4" />
                      ) : (
                        <Square className="h-4 w-4" />
                      )}
                    </button>
                  </th>
                  <th className="px-4 py-3">
                    <button
                      onClick={() => handleSort("id")}
                      className="flex items-center gap-1 hover:text-primary"
                    >
                      ID
                      {sortBy === "id" && (sortOrder === "desc" ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />)}
                    </button>
                  </th>
                  <th className="px-4 py-3">
                    <button
                      onClick={() => handleSort("email")}
                      className="flex items-center gap-1 hover:text-primary"
                    >
                      Email
                      {sortBy === "email" && (sortOrder === "desc" ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />)}
                    </button>
                  </th>
                  <th className="px-4 py-3">Plan</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">
                    <button
                      onClick={() => handleSort("daily_used")}
                      className="flex items-center gap-1 hover:text-primary"
                    >
                      Usage
                      {sortBy === "daily_used" && (sortOrder === "desc" ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />)}
                    </button>
                  </th>
                  <th className="px-4 py-3">
                    <button
                      onClick={() => handleSort("total_analyses")}
                      className="flex items-center gap-1 hover:text-primary"
                    >
                      Total
                      {sortBy === "total_analyses" && (sortOrder === "desc" ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />)}
                    </button>
                  </th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">
                    <button
                      onClick={() => handleSort("created_at")}
                      className="flex items-center gap-1 hover:text-primary"
                    >
                      Created
                      {sortBy === "created_at" && (sortOrder === "desc" ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />)}
                    </button>
                  </th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {usersResponse?.data.map((user) => (
                  <tr key={user.id} className="hover:bg-muted/20">
                    <td className="px-4 py-3">
                      <button onClick={() => toggleSelectUser(user.id)}>
                        {selectedUsers.has(user.id) ? (
                          <CheckSquare className="h-4 w-4" />
                        ) : (
                          <Square className="h-4 w-4" />
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-3 font-medium">#{user.id}</td>
                    <td className="px-4 py-3 font-medium">{user.email || "No email"}</td>
                    <td className="px-4 py-3">
                      <span className="badge capitalize">{user.plan}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="badge capitalize">{user.role}</span>
                    </td>
                    <td className="px-4 py-3">
                      {user.daily_used} / {user.daily_limit}
                    </td>
                    <td className="px-4 py-3">{user.total_analyses}</td>
                    <td className="px-4 py-3">
                      {user.is_banned ? (
                        <span className="badge border-destructive text-destructive">Banned</span>
                      ) : user.is_active ? (
                        <span className="badge border-green-500 text-green-600">Active</span>
                      ) : (
                        <span className="badge">Inactive</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(user.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setSelectedUser(user)}
                        className="text-xs text-primary hover:underline"
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              {usersResponse?.data.length || 0} of {usersResponse?.total_count || 0} users
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
                disabled={!usersResponse?.has_more}
                className="btn btn-sm btn-outline"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        {/* Edit User Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="card p-6 max-w-md w-full space-y-4">
              <h3 className="text-lg font-semibold">Edit User</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-muted-foreground">Email</label>
                  <p className="font-medium">{selectedUser.email || "No email"}</p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Role</label>
                  <select
                    className="input-field"
                    defaultValue={selectedUser.role}
                    onChange={(e) =>
                      handleUserUpdate(selectedUser.id, { role: e.target.value })
                    }
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Plan</label>
                  <select
                    className="input-field"
                    defaultValue={selectedUser.plan}
                    onChange={(e) =>
                      handleUserUpdate(selectedUser.id, { plan: e.target.value })
                    }
                  >
                    <option value="free">Free</option>
                    <option value="pro">Pro</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() =>
                      handleUserUpdate(selectedUser.id, {
                        is_banned: !selectedUser.is_banned,
                      })
                    }
                    className={
                      selectedUser.is_banned ? "btn btn-outline flex-1" : "btn btn-ghost flex-1 text-destructive"
                    }
                  >
                    {selectedUser.is_banned ? "Unban" : "Ban"}
                  </button>
                  <button
                    onClick={() =>
                      handleUserUpdate(selectedUser.id, {
                        is_active: !selectedUser.is_active,
                      })
                    }
                    className="btn btn-outline flex-1"
                  >
                    {selectedUser.is_active ? "Deactivate" : "Activate"}
                  </button>
                </div>
              </div>

              <button onClick={() => setSelectedUser(null)} className="btn btn-outline w-full">
                Close
              </button>
            </div>
          </div>
        )}
      </section>
      {CommandPaletteComponent}
    </SiteShell>
  )
}
