"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ApiConnectionStatus } from "@/components/ApiConnectionStatus"
import { SiteShell } from "@/components/SiteShell"
import { BookOpen, CheckCircle2, Cloud, Code2, LockOpen, Rocket, Server, TerminalSquare } from "lucide-react"

const quickStartSteps = [
  {
    title: "Run the backend",
    body: "Start FastAPI locally or on your server, then make sure `/health` responds successfully.",
    command: "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
    icon: Server,
  },
  {
    title: "Point the frontend to your API",
    body: "Use `NEXT_PUBLIC_API_URL` so the browser knows where to send uploads, progress streams, and report requests.",
    command: "NEXT_PUBLIC_API_URL=http://localhost:8000",
    icon: Cloud,
  },
  {
    title: "Enable MVP auth bypass if needed",
    body: "For self-hosted demos without Supabase, explicitly disable auth on both sides.",
    command: "NEXT_PUBLIC_DISABLE_AUTH=true\nDISABLE_AUTH=true",
    icon: LockOpen,
  },
]

const checklist = [
  "Backend `/health` returns 200 OK",
  "Backend `CORS_ORIGINS` includes your frontend origin",
  "Frontend `NEXT_PUBLIC_API_URL` points at the correct domain",
  "Realtime progress works over WebSocket or SSE",
  "Analyze page opens without Supabase when mock auth is enabled",
]

export default function DocsPage() {
  return (
    <SiteShell>
      <section className="container mx-auto max-w-7xl px-4 py-16">
        <motion.div
          className="mx-auto max-w-3xl text-center"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-background/72 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-muted-foreground backdrop-blur-xl">
            <BookOpen className="h-3.5 w-3.5 text-primary" />
            Self-hosted setup
          </div>
          <h1 className="mt-6 text-5xl font-semibold tracking-tight text-balance lg:text-6xl">
            Connect VeritasAd to your own server without guesswork.
          </h1>
          <p className="mt-5 text-lg leading-8 text-muted-foreground text-balance">
            This page focuses on the MVP path: point the frontend at your backend, disable auth if you need a
            quick demo, and verify the connection immediately from the UI.
          </p>
        </motion.div>

        <div className="mt-10 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <div className="section-shell p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Quick start</p>
              <div className="mt-6 space-y-4">
                {quickStartSteps.map((step, index) => {
                  const Icon = step.icon
                  return (
                    <div key={step.title} className="rounded-[1.35rem] border border-border/60 bg-background/78 p-5">
                      <div className="flex gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-border/60 bg-background/84 text-primary">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                            Step {index + 1}
                          </div>
                          <h2 className="mt-2 text-2xl font-semibold tracking-tight">{step.title}</h2>
                          <p className="mt-3 text-sm leading-7 text-muted-foreground">{step.body}</p>
                          <div className="mt-4 overflow-x-auto rounded-2xl border border-border/60 bg-foreground/[0.04] px-4 py-3 font-mono text-xs text-foreground">
                            <pre>{step.command}</pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="section-shell p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Checklist</p>
              <div className="mt-5 grid gap-3">
                {checklist.map((item) => (
                  <div key={item} className="flex items-start gap-3 rounded-2xl border border-border/60 bg-background/78 px-4 py-3">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-500" />
                    <span className="text-sm leading-6 text-foreground">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <ApiConnectionStatus />

            <div className="section-shell p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Frontend env</p>
              <div className="mt-4 space-y-2">
                {[
                  "NEXT_PUBLIC_API_URL=https://api.your-domain.com",
                  "NEXT_PUBLIC_DISABLE_AUTH=true",
                ].map((row) => (
                  <div key={row} className="rounded-xl border border-border/60 bg-background/78 px-3 py-2 font-mono text-xs text-foreground">
                    {row}
                  </div>
                ))}
              </div>
            </div>

            <div className="section-shell p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Backend env</p>
              <div className="mt-4 space-y-2">
                {[
                  "DISABLE_AUTH=true",
                  'CORS_ORIGINS=["https://app.your-domain.com","http://localhost:3000"]',
                  "DATABASE_URL=sqlite+aiosqlite:///./veritasad_dev.db",
                ].map((row) => (
                  <div key={row} className="rounded-xl border border-border/60 bg-background/78 px-3 py-2 font-mono text-xs text-foreground">
                    {row}
                  </div>
                ))}
              </div>
            </div>

            <div className="section-shell p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Useful routes</p>
              <div className="mt-4 grid gap-3">
                <RouteCard method="GET" path="/health" description="Basic health probe for the backend." icon={Rocket} />
                <RouteCard method="POST" path="/api/v1/analyze/check" description="Submit file or URL analysis jobs." icon={Code2} />
                <RouteCard method="GET" path="/api/v1/analysis/{taskId}/stream" description="Progress updates over SSE." icon={TerminalSquare} />
              </div>
            </div>

            <div className="rounded-[1.6rem] border border-border/60 bg-foreground/[0.035] p-6">
              <h2 className="text-2xl font-semibold tracking-tight">Next recommended step</h2>
              <p className="mt-3 text-sm leading-7 text-muted-foreground">
                Open the analysis workspace and confirm that the connection badge shows your API as online before
                tuning models, payments, or auth providers.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <Link href="/analyze" className="btn btn-primary h-11 px-5">
                  Open analyze
                </Link>
                <Link href="/" className="btn btn-outline h-11 px-5 bg-background/76">
                  Back to landing
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </SiteShell>
  )
}

function RouteCard({
  method,
  path,
  description,
  icon: Icon,
}: {
  method: string
  path: string
  description: string
  icon: typeof Rocket
}) {
  return (
    <div className="rounded-[1.25rem] border border-border/60 bg-background/78 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-border/60 bg-background/84 text-primary">
            <Icon className="h-4 w-4" />
          </div>
          <div>
            <div className="inline-flex rounded-full border border-primary/20 bg-primary/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">
              {method}
            </div>
            <div className="mt-2 font-mono text-sm text-foreground">{path}</div>
          </div>
        </div>
      </div>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{description}</p>
    </div>
  )
}
