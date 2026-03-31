"use client"

import { useEffect, useState } from "react"
import { Activity, AlertTriangle, CheckCircle2, Loader2, Server, Shield } from "lucide-react"
import { API_BASE_URL, fetchApiHealth, FRONTEND_AUTH_DISABLED, type ApiHealthResponse } from "@/lib/api-config"
import { cn } from "@/lib/utils"

type ApiConnectionStatusProps = {
  compact?: boolean
  className?: string
}

export function ApiConnectionStatus({ compact = false, className }: ApiConnectionStatusProps) {
  const [health, setHealth] = useState<ApiHealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    fetchApiHealth(controller.signal)
      .then((data) => {
        setHealth(data)
        setError(null)
      })
      .catch((requestError: unknown) => {
        if (requestError instanceof Error && requestError.name === "AbortError") {
          return
        }
        setError(requestError instanceof Error ? requestError.message : "Unable to reach the backend")
      })
      .finally(() => setLoading(false))

    return () => controller.abort()
  }, [])

  if (compact) {
    return (
      <div className={cn("rounded-full border border-border/60 bg-background/72 px-4 py-2 backdrop-blur-xl", className)}>
        <div className="flex items-center gap-2 text-xs font-medium">
          {loading ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
              Checking API
            </>
          ) : error ? (
            <>
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
              API unavailable
            </>
          ) : (
            <>
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
              API online
            </>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className={cn("surface relative overflow-hidden p-5", className)}>
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-cyan-400/10 opacity-80" />
      <div className="relative space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
              Self-hosted MVP
            </p>
            <h3 className="mt-2 text-xl font-semibold tracking-tight">Backend connection status</h3>
          </div>
          <div className="rounded-full border border-border/60 bg-background/80 p-2">
            <Server className="h-4 w-4 text-primary" />
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-3">
          <StatusPill
            icon={Activity}
            label="API endpoint"
            value={API_BASE_URL}
            tone="neutral"
          />
          <StatusPill
            icon={FRONTEND_AUTH_DISABLED ? Shield : CheckCircle2}
            label="Auth mode"
            value={FRONTEND_AUTH_DISABLED ? "Mock / disabled" : "Supabase"}
            tone={FRONTEND_AUTH_DISABLED ? "warning" : "success"}
          />
          <StatusPill
            icon={loading ? Loader2 : error ? AlertTriangle : CheckCircle2}
            label="Health check"
            value={loading ? "Checking..." : error ? "Unavailable" : String(health?.status || "Online")}
            tone={loading ? "neutral" : error ? "warning" : "success"}
            spin={loading}
          />
        </div>

        <div className="rounded-[1.25rem] border border-border/60 bg-background/70 p-4 text-sm leading-6 text-muted-foreground">
          {error ? (
            <>
              Frontend is pointed at <span className="font-medium text-foreground">{API_BASE_URL}</span>, but the
              health check failed. Verify `NEXT_PUBLIC_API_URL`, backend startup, and backend `CORS_ORIGINS`.
            </>
          ) : (
            <>
              Frontend is successfully reaching <span className="font-medium text-foreground">{API_BASE_URL}</span>.
              {health?.version ? ` Backend version: ${health.version}.` : ""}
              {FRONTEND_AUTH_DISABLED
                ? " MVP mode is ready for self-hosted demos without Supabase."
                : " Auth is enabled and ready for a full account flow."}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function StatusPill({
  icon: Icon,
  label,
  value,
  tone,
  spin = false,
}: {
  icon: typeof Activity
  label: string
  value: string
  tone: "neutral" | "success" | "warning"
  spin?: boolean
}) {
  const toneClassName =
    tone === "success"
      ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-500"
      : tone === "warning"
        ? "border-amber-500/20 bg-amber-500/10 text-amber-500"
        : "border-border/60 bg-background/80 text-foreground"

  return (
    <div className="rounded-[1.1rem] border border-border/60 bg-background/80 p-3">
      <div className="flex items-center gap-2">
        <div className={cn("rounded-full border px-2 py-1", toneClassName)}>
          <Icon className={cn("h-3.5 w-3.5", spin && "animate-spin")} />
        </div>
        <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground/70">{label}</div>
      </div>
      <div className="mt-3 break-all text-sm font-medium text-foreground">{value}</div>
    </div>
  )
}
