import { supabase } from "@/lib/supabase"
import type {
  AnalysisCheckResponse,
  AnalysisResult,
  AnalyticsResponse,
  PaymentCreateResponse,
  ProgressPayload,
  UserListItem,
  UserProfile,
  AnalysisHistoryItem,
  CursorPaginationResponse,
} from "@/types/api"

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "")

type ApiErrorResponse = {
  detail?: unknown
  message?: string
  [key: string]: unknown
}

export class ApiError extends Error {
  response: { status: number; data: ApiErrorResponse | null }

  constructor(status: number, data: ApiErrorResponse | null, message?: string) {
    super(message || `Request failed with status ${status}`)
    this.name = "ApiError"
    this.response = { status, data }
  }
}

type RequestOptions = Omit<RequestInit, "headers"> & {
  headers?: Record<string, string>
}

async function getAccessToken(): Promise<string | null> {
  if (!supabase) {
    return null
  }
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

async function parseResponseBody(response: Response): Promise<ApiErrorResponse | null> {
  const contentType = response.headers.get("content-type") || ""
  if (!contentType.includes("application/json")) {
    return null
  }
  try {
    return (await response.json()) as ApiErrorResponse
  } catch {
    return null
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = await getAccessToken()
  const headers: Record<string, string> = {
    ...(options.headers || {}),
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  const data = await parseResponseBody(response)
  if (!response.ok) {
    throw new ApiError(response.status, data, data?.message as string | undefined)
  }

  return (data as T) ?? ({} as T)
}

export async function analyzeVideo(params: { url?: string; file?: File }): Promise<AnalysisCheckResponse> {
  const form = new FormData()
  if (params.url) {
    form.append("url", params.url)
  }
  if (params.file) {
    form.append("file", params.file)
  }
  return request<AnalysisCheckResponse>("/api/v1/analyze/check", {
    method: "POST",
    body: form,
  })
}

export async function fetchAnalysisResult(params: { taskId: string }): Promise<AnalysisResult> {
  return request<AnalysisResult>(`/api/v1/analysis/${encodeURIComponent(params.taskId)}/result`, {
    method: "GET",
  })
}

export async function fetchAnalysisHistory(params: { limit?: number; offset?: number }): Promise<AnalysisHistoryItem[]> {
  const search = new URLSearchParams()
  if (typeof params.limit === "number") {
    search.set("limit", String(params.limit))
  }
  if (typeof params.offset === "number") {
    search.set("offset", String(params.offset))
  }
  const query = search.toString()
  return request<AnalysisHistoryItem[]>(`/api/v1/analyze/history${query ? `?${query}` : ""}`, {
    method: "GET",
  })
}

export type { ProgressPayload }

export async function streamAnalysisProgress(params: {
  taskId: string
  onMessage: (payload: ProgressPayload) => void
  onError?: (error: Error) => void
  signal?: AbortSignal
}): Promise<void> {
  const wsBase = API_BASE_URL.replace(/^http/i, "ws")
  const wsUrl = `${wsBase}/api/v1/analysis/${encodeURIComponent(params.taskId)}/ws`

  // WebSocket first, SSE fallback.
  return new Promise((resolve, reject) => {
    let connectionTimeout: NodeJS.Timeout | null = null
    let heartbeatTimeout: NodeJS.Timeout | null = null
    let settled = false
    const websocket = new WebSocket(wsUrl)
    let eventSource: EventSource | null = null
    const abortError = Object.assign(new Error("Analysis was cancelled"), { name: "AbortError" })

    // Connection timeout - if no message within 30 seconds, something is wrong
    connectionTimeout = setTimeout(() => {
      const error = new Error("Connection timeout - no response from server")
      params.onError?.(error)
      if (!settled) {
        settled = true
        websocket.close()
        eventSource?.close()
        reject(error)
      }
    }, 30000)

    const resetHeartbeat = () => {
      if (heartbeatTimeout) {
        clearTimeout(heartbeatTimeout)
      }
      heartbeatTimeout = setTimeout(() => {
        const error = new Error("Connection lost - no heartbeat for 60 seconds")
        params.onError?.(error)
        if (!settled) {
          settled = true
          websocket.close()
          eventSource?.close()
          reject(error)
        }
      }, 60000)
    }

    const completeSuccess = () => {
      if (settled) return
      settled = true
      if (connectionTimeout) clearTimeout(connectionTimeout)
      if (heartbeatTimeout) clearTimeout(heartbeatTimeout)
      websocket.close()
      eventSource?.close()
      params.signal?.removeEventListener("abort", onAbort)
      resolve()
    }

    const failWith = (error: Error) => {
      if (settled) return
      settled = true
      if (connectionTimeout) clearTimeout(connectionTimeout)
      if (heartbeatTimeout) clearTimeout(heartbeatTimeout)
      websocket.close()
      eventSource?.close()
      params.signal?.removeEventListener("abort", onAbort)
      params.onError?.(error)
      reject(error)
    }

    const onAbort = () => {
      failWith(abortError)
    }

    if (params.signal?.aborted) {
      failWith(abortError)
      return
    }
    params.signal?.addEventListener("abort", onAbort)

    const handlePayload = (payload: ProgressPayload) => {
      params.onMessage(payload)
      if (payload.status === "completed" || payload.status === "failed") {
        completeSuccess()
      }
    }

    websocket.onopen = () => {
      resetHeartbeat()
    }

    websocket.onmessage = (event) => {
      if (connectionTimeout) {
        clearTimeout(connectionTimeout)
        connectionTimeout = null
      }
      resetHeartbeat()

      try {
        const payload = JSON.parse(event.data) as ProgressPayload
        handlePayload(payload)
      } catch (error) {
        const parseError = error instanceof Error ? error : new Error("Invalid SSE payload")
        params.onError?.(parseError)
      }
    }

    websocket.onerror = () => {
      // Fallback to SSE only if WS failed before completion.
      if (settled) return
      websocket.close()
      const tokenPromise = getAccessToken()
      tokenPromise
        .then((token) => {
          const tokenQuery = token ? `?token=${encodeURIComponent(token)}` : ""
          eventSource = new EventSource(
            `${API_BASE_URL}/api/v1/analysis/${encodeURIComponent(params.taskId)}/stream${tokenQuery}`
          )

          eventSource.onopen = () => resetHeartbeat()
          eventSource.onmessage = (evt) => {
            if (connectionTimeout) {
              clearTimeout(connectionTimeout)
              connectionTimeout = null
            }
            resetHeartbeat()
            try {
              const payload = JSON.parse(evt.data) as ProgressPayload
              handlePayload(payload)
            } catch (error) {
              const parseError = error instanceof Error ? error : new Error("Invalid SSE payload")
              params.onError?.(parseError)
            }
          }
          eventSource.addEventListener("error", (evt) => {
            const message =
              evt instanceof MessageEvent && typeof evt.data === "string" && evt.data
                ? evt.data
                : "Real-time connection failed"
            failWith(new Error(message))
          })
          eventSource.addEventListener("timeout", () => {
            failWith(new Error("Analysis progress stream timed out"))
          })
        })
        .catch((error) => failWith(error instanceof Error ? error : new Error("Failed to open fallback stream")))
    }
  })
}

export async function getCurrentUserProfile(): Promise<UserProfile> {
  return request<UserProfile>("/api/v1/users/me", {
    method: "GET",
  })
}

export type UserListParams = {
  limit?: number
  cursor?: string
  sort_by?: string
  sort_order?: "asc" | "desc"
  search?: string
  plan?: string
  role?: string
  is_active?: boolean
  is_banned?: boolean
}

export async function listUsers(params: UserListParams = {}): Promise<CursorPaginationResponse<UserListItem>> {
  const search = new URLSearchParams()

  if (typeof params.limit === "number") {
    search.set("limit", String(params.limit))
  }
  if (params.cursor) {
    search.set("cursor", params.cursor)
  }
  if (params.sort_by) {
    search.set("sort_by", params.sort_by)
  }
  if (params.sort_order) {
    search.set("sort_order", params.sort_order)
  }
  if (params.search) {
    search.set("search", params.search)
  }
  if (params.plan) {
    search.set("plan", params.plan)
  }
  if (params.role) {
    search.set("role", params.role)
  }
  if (params.is_active !== undefined) {
    search.set("is_active", String(params.is_active))
  }
  if (params.is_banned !== undefined) {
    search.set("is_banned", String(params.is_banned))
  }

  const query = search.toString()
  return request<CursorPaginationResponse<UserListItem>>(`/api/v1/admin/users${query ? `?${query}` : ""}`, {
    method: "GET",
  })
}

export async function updateUser(params: {
  userId: number
  data: Record<string, unknown>
}): Promise<UserListItem> {
  return request<UserListItem>(`/api/v1/admin/users/${params.userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params.data),
  })
}

export async function getAnalytics(): Promise<AnalyticsResponse> {
  return request<AnalyticsResponse>("/api/v1/admin/analytics", {
    method: "GET",
  })
}

// ==================== PAYMENTS & SUBSCRIPTIONS ====================

// Legacy function - use createSubscription instead
export async function createPayment(params: {
  plan: "pro" | "enterprise"
  returnUrl?: string
}): Promise<PaymentCreateResponse> {
  return request<PaymentCreateResponse>("/api/v1/payment/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      plan: params.plan,
      return_url: params.returnUrl,
    }),
  })
}

export async function createSubscription(params: {
  plan: "starter" | "pro" | "business" | "enterprise"
  returnUrl?: string
}): Promise<PaymentCreateResponse & { plan: string; daily_limit: number }> {
  return request<PaymentCreateResponse & { plan: string; daily_limit: number }>("/api/v1/payment/subscription/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      plan: params.plan,
      return_url: params.returnUrl,
    }),
  })
}

export async function purchaseCreditPackage(params: {
  package: "micro" | "standard" | "pro" | "business"
  returnUrl?: string
}): Promise<PaymentCreateResponse & {
  package_type: string
  credits: number
  validity_days: number
  price_per_analysis: number
}> {
  return request<PaymentCreateResponse & {
    package_type: string
    credits: number
    validity_days: number
    price_per_analysis: number
  }>("/api/v1/payment/credits/package", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      package: params.package,
      return_url: params.returnUrl,
    }),
  })
}

export type UserCreditsResponse = {
  credits: number
  expires_at: string | null
  total_used: number
  total_purchased: number
}

export async function getUserCredits(): Promise<UserCreditsResponse> {
  return request<UserCreditsResponse>("/api/v1/payment/credits", {
    method: "GET",
  })
}

export type CreditTransactionItem = {
  id: number
  transaction_type: string
  credits: number
  balance_after: number
  package_type: string | null
  description: string | null
  created_at: string
}

export type CreditHistoryResponse = {
  transactions: CreditTransactionItem[]
  total: number
}

export async function getCreditHistory(params?: {
  limit?: number
  offset?: number
}): Promise<CreditHistoryResponse> {
  const search = new URLSearchParams()
  if (params?.limit) {
    search.set("limit", String(params.limit))
  }
  if (params?.offset) {
    search.set("offset", String(params.offset))
  }
  const query = search.toString()
  return request<CreditHistoryResponse>(`/api/v1/payment/credits/history${query ? `?${query}` : ""}`, {
    method: "GET",
  })
}

// ==================== AUDIT LOGS ====================

export type AuditLogListItem = {
  id: number
  event_type: string
  event_category: string
  description: string
  actor_user_id: number | null
  actor_email: string | null
  actor_ip: string | null
  target_type: string | null
  target_id: number | null
  target_email: string | null
  status: string
  created_at: string
}

export type AuditLogListParams = {
  limit?: number
  cursor?: string
  event_type?: string
  event_category?: string
  actor_email?: string
  target_email?: string
  status?: string
  start_date?: string
  end_date?: string
}

export async function listAuditLogs(params: AuditLogListParams = {}): Promise<CursorPaginationResponse<AuditLogListItem>> {
  const search = new URLSearchParams()
  
  if (typeof params.limit === "number") {
    search.set("limit", String(params.limit))
  }
  if (params.cursor) {
    search.set("cursor", params.cursor)
  }
  if (params.event_type) {
    search.set("event_type", params.event_type)
  }
  if (params.event_category) {
    search.set("event_category", params.event_category)
  }
  if (params.actor_email) {
    search.set("actor_email", params.actor_email)
  }
  if (params.target_email) {
    search.set("target_email", params.target_email)
  }
  if (params.status) {
    search.set("status", params.status)
  }
  if (params.start_date) {
    search.set("start_date", params.start_date)
  }
  if (params.end_date) {
    search.set("end_date", params.end_date)
  }
  
  const query = search.toString()
  return request<CursorPaginationResponse<AuditLogListItem>>(`/api/v1/admin/audit-logs${query ? `?${query}` : ""}`, {
    method: "GET",
  })
}

export async function getAuditStats(params: { days?: number } = {}): Promise<{
  total_events: number
  period_days: number
  events_by_category: Array<{ category: string; count: number }>
  events_by_status: Array<{ status: string; count: number }>
  top_actors: Array<{ email: string; count: number }>
  top_event_types: Array<{ event_type: string; count: number }>
}> {
  const search = new URLSearchParams()
  if (params.days) {
    search.set("days", String(params.days))
  }
  return request(`/api/v1/admin/audit-logs/stats${search.toString() ? `?${search.toString()}` : ""}`, {
    method: "GET",
  })
}

// ==================== BULK OPERATIONS ====================

export async function bulkUpdateUsers(params: {
  user_ids: number[]
  updates: Record<string, unknown>
}): Promise<UserListItem[]> {
  return request<UserListItem[]>("/api/v1/admin/users/bulk-update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  })
}

export async function bulkDeleteUsers(params: { user_ids: number[] }): Promise<void> {
  return request("/api/v1/admin/users/bulk-delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  })
}

// ==================== TELEGRAM ====================

export type TelegramLinkStatus = {
  is_linked: boolean
  telegram_id?: number | null
  telegram_username?: string | null
  linked_at?: string | null
}

export type TelegramLinkToken = {
  token: string
  expires_in: number
}

export async function getTelegramLinkStatus(): Promise<TelegramLinkStatus> {
  return request<TelegramLinkStatus>("/api/v1/telegram/status", {
    method: "GET",
  })
}

export async function generateTelegramLinkToken(): Promise<TelegramLinkToken> {
  return request<TelegramLinkToken>("/api/v1/telegram/link-token", {
    method: "POST",
  })
}

export async function linkTelegramAccount(params: {
  telegram_id: number
  link_token: string
  username?: string
}): Promise<{ success: boolean; message: string }> {
  return request("/api/v1/telegram/link", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  })
}

export async function unlinkTelegramAccount(): Promise<{ success: boolean; message: string }> {
  return request("/api/v1/telegram/unlink", {
    method: "POST",
  })
}
