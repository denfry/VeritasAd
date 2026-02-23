/** API response types - aligned with backend schemas */

export type BrandDetection = {
  name: string
  confidence?: number
  timestamps?: number[]
  source?: string
  frame_count?: number
  detections?: number
  total_exposure_seconds?: number
  is_unknown?: boolean
  logo_url?: string
}

export type AnalysisCheckResponse = {
  analysis_type: "video" | "post"
  status: string
  task_id?: string
  video_id?: string
  error?: string
  url?: string
  source_type?: string
  title?: string
  uploader?: string
  view_count?: number
  has_advertising?: boolean
  confidence_score?: number
  visual_score?: number
  audio_score?: number
  disclosure_score?: number
  disclosure_markers?: string[]
  disclosure_text?: string[]
  ad_classification?: string
  ad_reason?: string
  detected_brands?: BrandDetection[]
  detected_keywords?: string[]
  transcript?: string
  duration?: number
}

export type AnalysisResult = AnalysisCheckResponse

export type AnalysisHistoryItem = {
  task_id: string
  video_id: string
  source_type: string
  source_url: string | null
  status: string
  has_advertising: boolean
  confidence_score: number
  visual_score: number
  audio_score: number
  text_score: number
  disclosure_score: number
  detected_brands: BrandDetection[]
  detected_keywords: string[]
  ad_classification: string | null
  ad_reason: string | null
  duration: number | null
  progress: number
  error_message: string | null
  created_at: string
  completed_at: string | null
}

export type ProgressPayload = {
  task_id?: string
  progress?: number
  status?: string
  message?: string
  stage?: string
}

export type UserProfile = {
  id: number
  email?: string | null
  supabase_user_id?: string | null
  telegram_id?: number | null
  telegram_username?: string | null
  plan: string
  role: string
  daily_limit: number
  daily_used: number
  total_analyses: number
  is_active: boolean
  api_key?: string | null
}

export type UserListItem = {
  id: number
  email?: string | null
  supabase_user_id?: string | null
  plan: string
  role: string
  daily_limit: number
  daily_used: number
  total_analyses: number
  is_active: boolean
  is_banned: boolean
  created_at: string
}

export type AnalyticsResponse = {
  total_users: number
  active_users_today: number
  total_analyses: number
  analyses_today: number
  avg_confidence_score: number
  failed_analyses: number
  top_users: Array<{
    id: number
    email: string
    plan: string
    total_analyses: number
  }>
}

export type PaymentCreateResponse = {
  payment_id: string
  status: string
  amount: number
  currency: string
  checkout_url: string
}

export type CursorPaginationResponse<T> = {
  data: T[]
  next_cursor: string | null
  has_more: boolean
  total_count: number | null
}

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
