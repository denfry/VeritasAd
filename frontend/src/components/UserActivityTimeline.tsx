/**
 * User Activity Timeline - BigTech Standard
 * Аналог Activity Feed в GitHub, Linear, Notion
 * 
 * Shows all user actions in chronological order.
 */
"use client"

import { useEffect, useState } from "react"
import { formatDistanceToNow } from "date-fns"
import { ru } from "date-fns/locale"
import type { AuditLogListItem } from "@/types/api"
import { listAuditLogs } from "@/lib/api-client"
import {
  User,
  Shield,
  LogOut,
  Settings,
  FileText,
  AlertCircle,
  CheckCircle,
  XCircle,
  Ban,
  UserCheck,
  Key,
  Eye,
  Download,
  Upload,
  Trash2,
  Edit,
  Plus,
  RefreshCw,
} from "lucide-react"

type ActivityTimelineProps = {
  userId?: number
  userEmail?: string
  limit?: number
  showFilters?: boolean
}

// Icon mapping for event types
const EVENT_ICONS: Record<string, React.ReactNode> = {
  // Auth
  login: <User className="h-4 w-4" />,
  logout: <LogOut className="h-4 w-4" />,
  login_failed: <AlertCircle className="h-4 w-4" />,
  
  // User management
  "user.created": <Plus className="h-4 w-4" />,
  "user.updated": <Edit className="h-4 w-4" />,
  "user.deleted": <Trash2 className="h-4 w-4" />,
  "user.banned": <Ban className="h-4 w-4" />,
  "user.unbanned": <UserCheck className="h-4 w-4" />,
  "role.changed": <RefreshCw className="h-4 w-4" />,
  "plan.changed": <Shield className="h-4 w-4" />,
  
  // Admin
  "admin.login": <Shield className="h-4 w-4" />,
  "admin.user.view": <Eye className="h-4 w-4" />,
  "admin.user.list": <FileText className="h-4 w-4" />,
  "admin.user.update": <Edit className="h-4 w-4" />,
  "admin.analytics.view": <FileText className="h-4 w-4" />,
  "admin.export": <Download className="h-4 w-4" />,
  
  // Security
  "session.revoked": <Key className="h-4 w-4" />,
  "api_key.created": <Key className="h-4 w-4" />,
  "api_key.revoked": <Key className="h-4 w-4" />,
  
  // Data
  "data.export": <Download className="h-4 w-4" />,
  "data.import": <Upload className="h-4 w-4" />,
  "data.delete": <Trash2 className="h-4 w-4" />,
}

const STATUS_COLORS: Record<string, string> = {
  success: "text-green-600 bg-green-50 border-green-200",
  failure: "text-red-600 bg-red-50 border-red-200",
  denied: "text-amber-600 bg-amber-50 border-amber-200",
}

export function UserActivityTimeline({
  userId,
  userEmail,
  limit = 50,
  showFilters = true,
}: ActivityTimelineProps) {
  const [logs, setLogs] = useState<AuditLogListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>("all")
  const [cursor, setCursor] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(false)

  useEffect(() => {
    loadLogs()
  }, [filter])

  const loadLogs = async () => {
    try {
      const params: Record<string, string | number | boolean> = { limit }
      
      if (userId) params.actor_user_id = userId
      if (userEmail) params.actor_email = userEmail
      if (filter !== "all") params.event_category = filter
      
      const response = await listAuditLogs(params as any)
      setLogs(response.data)
      setCursor(response.next_cursor)
      setHasMore(response.has_more)
    } catch (error) {
      console.error("Failed to load activity logs:", error)
    } finally {
      setLoading(false)
    }
  }

  const loadMore = async () => {
    if (!cursor) return
    
    try {
      const params: Record<string, string | number> = { limit, cursor }
      if (userId) params.actor_user_id = userId
      if (userEmail) params.actor_email = userEmail
      if (filter !== "all") params.event_category = filter
      
      const response = await listAuditLogs(params as any)
      setLogs(prev => [...prev, ...response.data])
      setCursor(response.next_cursor)
      setHasMore(response.has_more)
    } catch (error) {
      console.error("Failed to load more logs:", error)
    }
  }

  const groupedLogs = logs.reduce((acc, log) => {
    const date = new Date(log.created_at).toLocaleDateString()
    if (!acc[date]) {
      acc[date] = []
    }
    acc[date].push(log)
    return acc
  }, {} as Record<string, AuditLogListItem[]>)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      {showFilters && (
        <div className="flex items-center gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input-field text-sm"
          >
            <option value="all">All Activities</option>
            <option value="auth">Authentication</option>
            <option value="user">User Management</option>
            <option value="admin">Admin Actions</option>
            <option value="security">Security</option>
            <option value="data">Data Operations</option>
          </select>
        </div>
      )}

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />

        <div className="space-y-8">
          {Object.entries(groupedLogs).map(([date, dayLogs]) => (
            <div key={date} className="relative">
              {/* Date label */}
              <div className="sticky top-0 z-10 flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-full bg-background border-2 border-primary flex items-center justify-center text-xs font-semibold">
                  {new Date(date).getDate()}
                </div>
                <div className="text-sm font-medium bg-background px-2">
                  {new Date(date).toLocaleDateString("ru-RU", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </div>
              </div>

              {/* Events for this day */}
              <div className="space-y-3 ml-2">
                {dayLogs.map((log, index) => {
                  const icon = EVENT_ICONS[log.event_type] || <FileText className="h-4 w-4" />
                  const statusClass = STATUS_COLORS[log.status] || STATUS_COLORS.success

                  return (
                    <div key={`${log.id}-${index}`} className="relative flex gap-3 group">
                      {/* Dot on timeline */}
                      <div className="absolute left-0 w-8 h-8 flex items-center justify-center">
                        <div
                          className={`w-2.5 h-2.5 rounded-full border-2 ${statusClass} bg-background`}
                        />
                      </div>

                      {/* Content */}
                      <div className="ml-8 flex-1">
                        <div className="card p-3 hover:shadow-md transition-shadow">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex items-start gap-3 flex-1">
                              {/* Icon */}
                              <div className={`p-2 rounded-lg ${statusClass}`}>
                                {icon}
                              </div>

                              {/* Details */}
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium">
                                  {log.description}
                                </p>
                                <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                  <span className="capitalize">
                                    {log.event_category}
                                  </span>
                                  <span>•</span>
                                  <span className="font-mono">
                                    {log.event_type}
                                  </span>
                                  {log.actor_ip && (
                                    <>
                                      <span>•</span>
                                      <span className="font-mono">
                                        {log.actor_ip}
                                      </span>
                                    </>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Status & Time */}
                            <div className="flex flex-col items-end gap-1">
                              <span className={`badge text-xs ${statusClass}`}>
                                {log.status}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {formatDistanceToNow(new Date(log.created_at), {
                                  addSuffix: true,
                                  locale: ru,
                                })}
                              </span>
                            </div>
                          </div>

                          {/* Additional info */}
                          {log.target_email && (
                            <div className="mt-3 pt-3 border-t text-xs space-y-1">
                              <p className="text-muted-foreground">
                                Target: <span className="font-medium">{log.target_email}</span>
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Load More */}
        {hasMore && (
          <div className="flex justify-center mt-8">
            <button onClick={loadMore} className="btn btn-outline btn-sm">
              Load More
            </button>
          </div>
        )}

        {logs.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No activity found</p>
          </div>
        )}
      </div>
    </div>
  )
}
