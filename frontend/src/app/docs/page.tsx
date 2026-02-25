"use client"

import Link from "next/link"
import { Code2, FileText, Terminal, BookOpen, Layers, ShieldCheck, Cpu } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"
import { motion } from "framer-motion"

const sections = [
  {
    title: "Quick start",
    description: "Launch the platform locally with Docker or UV in minutes.",
    icon: <Terminal className="h-6 w-6" />,
    href: "#quick-start",
    color: "text-blue-500",
    bgColor: "bg-blue-500/10"
  },
  {
    title: "API reference",
    description: "Full endpoint documentation for analysis, reports, and streaming.",
    icon: <Code2 className="h-6 w-6" />,
    href: "#api",
    color: "text-purple-500",
    bgColor: "bg-purple-500/10"
  },
  {
    title: "Reports",
    description: "How to interpret scores, brand detection, and compliance markers.",
    icon: <FileText className="h-6 w-6" />,
    href: "#reports",
    color: "text-emerald-500",
    bgColor: "bg-emerald-500/10"
  },
]

export default function DocsPage() {
  return (
    <SiteShell>
      <section className="container mx-auto max-w-6xl px-4 py-16 space-y-12">
        {/* Header */}
        <motion.div 
          className="text-center space-y-4 max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-widest border border-primary/20">
            <BookOpen className="h-3 w-3" /> Documentation
          </div>
          <h1 className="text-5xl font-extrabold tracking-tight">VeritasAd Knowledge Base</h1>
          <p className="text-xl text-muted-foreground">
            Everything you need to integrate VeritasAd into your workflow and understand the
            automated compliance results.
          </p>
        </motion.div>

        {/* Quick Links */}
        <div className="grid gap-6 md:grid-cols-3">
          {sections.map((section, idx) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * idx }}
            >
              <Link
                href={section.href}
                className="card card-hover p-8 flex flex-col h-full hover:border-primary/50 transition-all group"
              >
                <div className={`h-12 w-12 rounded-xl ${section.bgColor} ${section.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                  {section.icon}
                </div>
                <h2 className="mt-6 text-xl font-bold">{section.title}</h2>
                <p className="mt-3 text-muted-foreground leading-relaxed">{section.description}</p>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Main Content */}
        <div className="grid gap-12 lg:grid-cols-4 pt-12">
          {/* Table of Contents - Sidebar */}
          <aside className="lg:col-span-1 hidden lg:block sticky top-24 h-fit">
             <nav className="space-y-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 px-2">On this page</p>
                <div className="flex flex-col gap-1">
                   <TocLink href="#architecture" label="Architecture" />
                   <TocLink href="#quick-start" label="Quick Start" />
                   <TocLink href="#api" label="API Endpoints" />
                   <TocLink href="#reports" label="Reading Reports" />
                </div>
             </nav>
          </aside>

          {/* Documentation Body */}
          <div className="lg:col-span-3 space-y-16">
            <DocSection id="architecture" title="Architecture" icon={<Layers className="h-5 w-5" />}>
              <p>
                VeritasAd is built on a distributed pipeline architecture designed for high-throughput video processing.
                The system consists of three main layers:
              </p>
              <div className="grid gap-4 md:grid-cols-2 mt-6">
                 <FeatureCard 
                  icon={<Cpu className="h-4 w-4" />}
                  title="Analysis Pipeline" 
                  description="Leverages Vision-LLMs and dedicated logo detection models for multi-modal analysis."
                 />
                 <FeatureCard 
                  icon={<ShieldCheck className="h-4 w-4" />}
                  title="Compliance Engine" 
                  description="Cross-references detected signals with regional advertising laws (e.g., FAS, FTC)."
                 />
              </div>
            </DocSection>

            <DocSection id="quick-start" title="Quick start" icon={<Terminal className="h-5 w-5" />}>
              <p>Run the entire platform locally using Docker Compose. This starts the API, Frontend, Workers, and Databases.</p>
              <div className="bg-muted rounded-2xl p-6 font-mono text-sm border relative group overflow-hidden">
                <div className="absolute top-0 right-0 p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                   <button className="text-[10px] font-bold bg-foreground text-background px-2 py-1 rounded">COPY</button>
                </div>
                <code className="block whitespace-pre text-primary">
                  {`# Clone the repository\ngit clone https://github.com/veritasad/core.git\n\n# Navigate to infra\ncd infra\n\n# Start development environment\ndocker-compose up -d`}
                </code>
              </div>
            </DocSection>

            <DocSection id="api" title="API Reference" icon={<Code2 className="h-5 w-5" />}>
              <p>The VeritasAd API follows REST principles and uses JWT for authentication. All requests should be made to the base URL: <code>https://api.veritasad.ai/v1/</code>.</p>
              
              <div className="space-y-4 mt-6">
                <EndpointRow method="POST" path="/analyze/check" description="Submit a video URL or file for analysis" />
                <EndpointRow method="GET" path="/analysis/{id}/result" description="Fetch finalized analysis data" />
                <EndpointRow method="GET" path="/analysis/{id}/stream" description="Real-time progress via SSE" />
              </div>
            </DocSection>

            <DocSection id="reports" title="Interpreting Reports" icon={<FileText className="h-5 w-5" />}>
              <p>
                Every analysis generates a structured JSON report and a human-readable summary. Key metrics include:
              </p>
              <ul className="list-disc pl-6 space-y-2 mt-4 text-muted-foreground">
                <li><strong>Confidence Score:</strong> 0.0 to 1.0 indicating the likelihood of advertising.</li>
                <li><strong>Brand Exposure:</strong> Total seconds a brand logo or name was visible.</li>
                <li><strong>Disclosure Markers:</strong> Presence of labels like "Ad", "Sponsorship", or "Partnership".</li>
                <li><strong>AI Reasoning:</strong> Natural language explanation of why the content was flagged.</li>
              </ul>
            </DocSection>
          </div>
        </div>
      </section>
    </SiteShell>
  )
}

function DocSection({ id, title, icon, children }: { id: string, title: string, icon: any, children: any }) {
  return (
    <section id={id} className="scroll-mt-24 space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/5 text-primary border border-primary/10">
          {icon}
        </div>
        <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
      </div>
      <div className="text-muted-foreground leading-relaxed text-lg">
        {children}
      </div>
    </section>
  )
}

function FeatureCard({ icon, title, description }: { icon: any, title: string, description: string }) {
  return (
    <div className="p-4 rounded-2xl bg-muted/50 border border-border/50">
       <div className="flex items-center gap-2 mb-2">
         <div className="text-primary">{icon}</div>
         <h4 className="font-bold text-foreground text-sm">{title}</h4>
       </div>
       <p className="text-xs text-muted-foreground leading-normal">{description}</p>
    </div>
  )
}

function EndpointRow({ method, path, description }: { method: string, path: string, description: string }) {
  const methodColors: Record<string, string> = {
    GET: 'bg-emerald-500/10 text-emerald-600',
    POST: 'bg-blue-500/10 text-blue-600',
    PATCH: 'bg-amber-500/10 text-amber-600',
    DELETE: 'bg-red-500/10 text-red-600',
  }

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl border border-border/50 bg-card/50 gap-4">
       <div className="flex items-center gap-3">
          <span className={`px-2 py-0.5 rounded text-[10px] font-black tracking-widest ${methodColors[method] || 'bg-muted'}`}>
            {method}
          </span>
          <code className="text-sm font-bold text-foreground">{path}</code>
       </div>
       <span className="text-xs text-muted-foreground">{description}</span>
    </div>
  )
}

function TocLink({ href, label }: { href: string, label: string }) {
  return (
    <Link 
      href={href} 
      className="text-sm font-medium text-muted-foreground hover:text-primary px-3 py-1.5 rounded-lg hover:bg-muted transition-all"
    >
      {label}
    </Link>
  )
}

