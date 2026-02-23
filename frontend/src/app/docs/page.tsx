"use client"

import Link from "next/link"
import { Code2, FileText, Terminal } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

const sections = [
  {
    title: "Quick start",
    description: "How to run the platform locally with Docker Compose.",
    icon: <Terminal className="h-5 w-5" />,
    href: "/docs#quick-start",
  },
  {
    title: "API reference",
    description: "Endpoints for analysis, uploads, reports, and SSE progress.",
    icon: <Code2 className="h-5 w-5" />,
    href: "/docs#api",
  },
  {
    title: "Reports",
    description: "Understand scores, brand detection, and disclosure markers.",
    icon: <FileText className="h-5 w-5" />,
    href: "/docs#reports",
  },
]

export default function DocsPage() {
  return (
    <SiteShell>
      <section className="container mx-auto max-w-6xl px-4 section space-y-10">
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">Documentation</p>
          <h1 className="text-4xl font-semibold">VeritasAd documentation</h1>
          <p className="text-muted-foreground max-w-2xl">
            Everything you need to integrate VeritasAd into your workflow and understand the
            results.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {sections.map((section) => (
            <Link
              key={section.title}
              href={section.href}
              className="card card-hover p-6 hover:border-primary transition-colors"
            >
              <div className="text-primary">{section.icon}</div>
              <h2 className="mt-4 text-lg font-semibold">{section.title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{section.description}</p>
            </Link>
          ))}
        </div>

        <div className="card p-8 prose prose-zinc dark:prose-invert max-w-none">
          <h2 id="quick-start">Quick start</h2>
          <p>Run the platform locally:</p>
          <pre>
            <code>{`cd infra\ndocker-compose up -d`}</code>
          </pre>

          <h2 id="api">API</h2>
          <p>Key endpoints:</p>
          <pre>
            <code>{`POST /api/v1/analyze/check\nGET  /api/v1/analysis/{task_id}/stream\nGET  /api/v1/report/{video_id}`}</code>
          </pre>

          <h2 id="reports">Reports</h2>
          <p>
            Reports include confidence scores, detected brands, timestamps, disclosure markers, and
            transcripts. Use them for audits or compliance reviews.
          </p>
        </div>
      </section>
    </SiteShell>
  )
}
