"use client"

import Link from "next/link"
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion"
import {
  Activity,
  ArrowRight,
  AudioLines,
  BadgeCheck,
  Boxes,
  BrainCircuit,
  CheckCircle2,
  Eye,
  Radar,
  Server,
  ShieldCheck,
  Waves,
} from "lucide-react"
import { ApiConnectionStatus } from "@/components/ApiConnectionStatus"
import { SectionReveal } from "@/components/SectionReveal"
import { SiteShell } from "@/components/SiteShell"
import { CountUp } from "@/components/ui/CountUp"
import { ThreeScene } from "@/components/three/ThreeScene"

const proofStats = [
  { label: "Analyses processed", value: 12840 },
  { label: "Average confidence", value: 98.4, decimals: 1, suffix: "%" },
  { label: "Detected brand events", value: 317000 },
  { label: "Export-ready reports", value: 9420 },
]

const pillars = [
  {
    title: "Multi-layer evidence",
    description: "Visual logos, spoken mentions, disclosure labels, links, and CTA signals assembled into one verdict.",
    icon: BrainCircuit,
    accent: "from-cyan-500/30 to-sky-500/10",
  },
  {
    title: "Command-center UX",
    description: "A product surface that feels credible on day one, with motion, depth, and focused reporting instead of flat admin panels.",
    icon: Radar,
    accent: "from-sky-500/30 to-orange-400/10",
  },
  {
    title: "Self-hosted MVP path",
    description: "Point the frontend to your backend, disable auth for demos, and verify the server immediately from the UI.",
    icon: Server,
    accent: "from-orange-400/30 to-cyan-400/10",
  },
]

const pipelineSteps = [
  {
    eyebrow: "01 / Intake",
    title: "Receive a video URL or file upload",
    body: "The product accepts direct uploads or public URLs and pushes them into a single analysis flow without making the user think about infrastructure.",
    icon: Boxes,
  },
  {
    eyebrow: "02 / Analysis",
    title: "Fuse visual, audio, and disclosure signals",
    body: "Brand exposure, voice references, missing disclaimers, and outbound links build a structured confidence score instead of a black-box answer.",
    icon: Waves,
  },
  {
    eyebrow: "03 / Delivery",
    title: "Return a verdict your team can act on",
    body: "Reports, timelines, export actions, and live status updates turn the backend output into something a client or reviewer can trust.",
    icon: BadgeCheck,
  },
]

const mvpSteps = [
  {
    title: "Point the frontend at your backend",
    detail: "Set `NEXT_PUBLIC_API_URL` to your own API domain or local FastAPI instance.",
  },
  {
    title: "Run without Supabase if needed",
    detail: "Enable `NEXT_PUBLIC_DISABLE_AUTH=true` on the frontend and `DISABLE_AUTH=true` on the backend for a demo-ready MVP path.",
  },
  {
    title: "Expose your frontend domain in CORS",
    detail: "Add your frontend host to backend `CORS_ORIGINS` so uploads, progress streams, and reports work from the browser.",
  },
]

const signalTiles = [
  { label: "Detected brands", value: "12", icon: Eye },
  { label: "Voice mentions", value: "7", icon: AudioLines },
  { label: "Disclosure gaps", value: "4", icon: ShieldCheck },
]

export default function HomePage() {
  const reduceMotion = useReducedMotion()
  const { scrollYProgress } = useScroll()
  const previewY = useTransform(scrollYProgress, [0, 1], [0, reduceMotion ? 0 : -120])
  const haloY = useTransform(scrollYProgress, [0, 1], [0, reduceMotion ? 0 : 180])

  return (
    <ThreeScene intensity="medium" type="neural">
      <SiteShell>
      <section className="relative overflow-hidden border-b border-border/40">
        <div className="container mx-auto max-w-7xl px-4 pt-16 pb-18 lg:pt-24 lg:pb-24">
          <div className="grid items-center gap-12 lg:grid-cols-[1.02fr_0.98fr]">
            <SectionReveal className="relative z-10">
              <div className="flex flex-wrap items-center gap-3">
                <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-background/72 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-muted-foreground backdrop-blur-xl">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_18px_rgba(16,185,129,0.55)]" />
                  Self-hosted ad intelligence
                </div>
                <ApiConnectionStatus compact />
              </div>

              <h1 className="display-type mt-7 max-w-4xl text-5xl font-semibold leading-[0.95] text-foreground sm:text-6xl lg:text-7xl xl:text-[5.6rem]">
                Build an
                <span className="gradient-text"> AI compliance command center </span>
                that already feels like a premium product.
              </h1>

              <p className="mt-7 max-w-2xl text-lg leading-8 text-muted-foreground">
                VeritasAd analyzes videos and social content for advertising signals, then turns backend output
                into a polished surface with motion, proof, and self-hosted MVP readiness.
              </p>

              <div className="mt-9 flex flex-wrap gap-3">
                <Link href="/analyze" className="btn btn-primary btn-premium h-12 px-6 shadow-[0_24px_60px_-20px_hsl(var(--primary)/0.8)]">
                  Open analysis workspace
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link href="/docs" className="btn btn-outline h-12 px-6 bg-background/72">
                  View self-hosted setup
                </Link>
              </div>

              <div className="mt-10 flex flex-wrap gap-2">
                {["Realtime progress", "Brand timeline", "PDF reports", "Mock auth", "Custom API"].map((item) => (
                  <span
                    key={item}
                    className="rounded-full border border-border/60 bg-background/68 px-3 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur-xl"
                  >
                    {item}
                  </span>
                ))}
              </div>

              <div className="mt-10 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {proofStats.map((stat) => (
                  <div key={stat.label} className="card bg-noise p-4">
                    <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground/70">{stat.label}</div>
                    <div className="mt-3 text-3xl font-semibold tracking-tight">
                      <CountUp end={stat.value} decimals={stat.decimals ?? 0} />
                      {stat.suffix ?? ""}
                    </div>
                  </div>
                ))}
              </div>
            </SectionReveal>

            <SectionReveal delay={0.05}>
              <div className="relative">
                <motion.div
                  className="absolute inset-x-[8%] top-4 h-40 rounded-full bg-gradient-to-r from-cyan-400/20 via-sky-400/20 to-orange-300/20 blur-3xl"
                  style={{ y: haloY }}
                />

                <motion.div
                  className="section-shell bg-noise relative p-4 md:p-5"
                  style={{ y: previewY }}
                >
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,hsl(var(--primary)/0.16),transparent_32%),linear-gradient(135deg,rgba(255,255,255,0.08),transparent_35%)]" />

                  <div className="relative rounded-[1.5rem] border border-border/60 bg-background/84 p-5 backdrop-blur-2xl">
                    <div className="flex items-center justify-between border-b border-border/60 pb-4">
                      <div className="flex items-center gap-2">
                        <span className="h-3 w-3 rounded-full bg-red-500/75" />
                        <span className="h-3 w-3 rounded-full bg-amber-400/75" />
                        <span className="h-3 w-3 rounded-full bg-emerald-400/75" />
                      </div>
                      <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-emerald-500">
                        <Activity className="h-3.5 w-3.5" />
                        Live system
                      </div>
                    </div>

                    <div className="mt-5 grid gap-4">
                      <div className="grid gap-4 md:grid-cols-[1.1fr_0.9fr]">
                        <div className="rounded-[1.3rem] border border-border/60 bg-[linear-gradient(135deg,rgba(20,184,166,0.14),rgba(59,130,246,0.08),rgba(251,146,60,0.08))] p-5">
                          <p className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground/72">Current verdict</p>
                          <div className="mt-3 flex items-end justify-between gap-4">
                            <div>
                              <div className="text-4xl font-semibold tracking-tight">
                                <CountUp end={98.4} decimals={1} />%
                              </div>
                              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                High-confidence ad detection with corroborated logo and speech evidence.
                              </p>
                            </div>
                            <div className="rounded-full border border-emerald-500/20 bg-background/72 px-3 py-1.5 text-xs font-semibold text-emerald-500">
                              Verified
                            </div>
                          </div>
                          <div className="mt-4 h-2.5 overflow-hidden rounded-full bg-white/35">
                            <div className="h-full w-[88%] rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-orange-400" />
                          </div>
                        </div>

                        <div className="grid gap-3">
                          {signalTiles.map(({ label, value, icon: Icon }) => (
                            <div key={label} className="rounded-[1.2rem] border border-border/60 bg-background/84 p-4">
                              <div className="flex items-center justify-between">
                                <p className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground/70">{label}</p>
                                <Icon className="h-4 w-4 text-primary" />
                              </div>
                              <div className="mt-3 text-2xl font-semibold tracking-tight">{value}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="grid gap-3 md:grid-cols-[1.2fr_0.8fr]">
                        <div className="rounded-[1.3rem] border border-border/60 bg-background/84 p-4">
                          <p className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground/70">Pipeline snapshot</p>
                          <div className="mt-4 grid gap-3">
                            {[
                              ["Upload normalized", "Done", "bg-emerald-500/14 text-emerald-500"],
                              ["Speech-to-text and OCR", "Active", "bg-primary/14 text-primary"],
                              ["Report compilation", "Queued", "bg-orange-400/14 text-orange-500"],
                            ].map(([step, status, tone]) => (
                              <div key={step} className="flex items-center justify-between rounded-2xl border border-border/50 bg-muted/18 px-4 py-3">
                                <span className="text-sm font-medium text-foreground">{step}</span>
                                <span className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${tone}`}>
                                  {status}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="rounded-[1.3rem] border border-border/60 bg-background/84 p-4">
                          <p className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground/70">Evidence mix</p>
                          <div className="mt-4 space-y-3">
                            <ScoreRow label="Visual" value={78} tone="cyan" />
                            <ScoreRow label="Audio" value={61} tone="blue" />
                            <ScoreRow label="Disclosure" value={34} tone="orange" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {!reduceMotion ? (
                    <>
                      <motion.div
                        className="pointer-events-none absolute -left-5 top-16 hidden rounded-full border border-border/60 bg-background/84 px-4 py-2 text-xs font-medium text-muted-foreground shadow-xl backdrop-blur-xl lg:block"
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 7, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
                      >
                        Progress stream attached
                      </motion.div>
                      <motion.div
                        className="pointer-events-none absolute -right-6 bottom-12 hidden rounded-full border border-border/60 bg-background/84 px-4 py-2 text-xs font-medium text-muted-foreground shadow-xl backdrop-blur-xl lg:block"
                        animate={{ y: [0, 10, 0] }}
                        transition={{ duration: 8, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
                      >
                        PDF export ready
                      </motion.div>
                    </>
                  ) : null}
                </motion.div>
              </div>
            </SectionReveal>
          </div>
        </div>
      </section>

      <section className="border-b border-border/40 py-20">
        <div className="container mx-auto max-w-7xl px-4">
          <SectionReveal className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
            <div className="max-w-2xl">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Product pillars</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-5xl">
                A sharper story than “upload file, get score”.
              </h2>
            </div>
            <p className="max-w-xl text-sm leading-7 text-muted-foreground">
              The design now frames VeritasAd as a serious product platform, while the MVP path removes the usual
              friction of auth and backend uncertainty during early deployment.
            </p>
          </SectionReveal>

          <div className="mt-10 grid gap-4 lg:grid-cols-3">
            {pillars.map((pillar, index) => {
              const Icon = pillar.icon
              return (
                <SectionReveal key={pillar.title} delay={index * 0.05}>
                  <div className="surface bg-noise group relative h-full overflow-hidden p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_34px_100px_rgba(0,0,0,0.16)]">
                    <div className={`absolute inset-0 bg-gradient-to-br ${pillar.accent} opacity-90`} />
                    <div className="relative">
                      <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-border/60 bg-background/82 text-primary shadow-sm">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="mt-5 text-2xl font-semibold tracking-tight">{pillar.title}</h3>
                      <p className="mt-4 text-sm leading-7 text-muted-foreground">{pillar.description}</p>
                    </div>
                  </div>
                </SectionReveal>
              )
            })}
          </div>
        </div>
      </section>

      <section className="border-b border-border/40 py-20">
        <div className="container mx-auto max-w-7xl px-4">
          <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
            <SectionReveal className="space-y-6">
              <div className="section-shell bg-noise p-8">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">MVP path</p>
                <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-4xl">
                  Connect your own server and verify it from the frontend.
                </h2>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">
                  You asked for a site that is beautiful and deployable. The new flow keeps the visual quality high
                  but also exposes whether the UI is actually talking to your backend.
                </p>

                <div className="mt-6 space-y-4">
                  {mvpSteps.map((step, index) => (
                    <div key={step.title} className="rounded-[1.3rem] border border-border/60 bg-background/76 p-4">
                      <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                        Step {index + 1}
                      </div>
                      <h3 className="mt-2 text-lg font-semibold tracking-tight">{step.title}</h3>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">{step.detail}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-6 grid gap-3 md:grid-cols-2">
                  <ConfigCard
                    title="Frontend env"
                    rows={[
                      "NEXT_PUBLIC_API_URL=https://api.your-domain.com",
                      "NEXT_PUBLIC_DISABLE_AUTH=true",
                    ]}
                  />
                  <ConfigCard
                    title="Backend env"
                    rows={[
                      "DISABLE_AUTH=true",
                      'CORS_ORIGINS=["https://app.your-domain.com"]',
                    ]}
                  />
                </div>
              </div>
            </SectionReveal>

            <SectionReveal delay={0.06} className="space-y-6">
              <ApiConnectionStatus />

              <div className="section-shell p-6">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">
                  Product surfaces
                </p>
                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  <SurfaceCard
                    title="Landing"
                    body="Premium first impression with layered motion, bento structure, and self-hosted messaging."
                  />
                  <SurfaceCard
                    title="Analyze"
                    body="A production-style workspace with upload, realtime progress, timelines, and export actions."
                  />
                  <SurfaceCard
                    title="Docs"
                    body="A clearer self-hosted setup path so the frontend, backend, and auth mode align faster."
                  />
                </div>
              </div>
            </SectionReveal>
          </div>
        </div>
      </section>

      <section className="border-b border-border/40 py-20">
        <div className="container mx-auto max-w-7xl px-4">
          <SectionReveal className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="section-shell p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Pipeline</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-4xl">
                One flow from intake to evidence-ready report.
              </h2>
              <p className="mt-4 max-w-xl text-sm leading-7 text-muted-foreground">
                Instead of a disconnected UI, the new MVP tells one coherent story: input, analysis, reporting, and
                deployment readiness all live inside the same visual language.
              </p>
            </div>

            <div className="space-y-4">
              {pipelineSteps.map((step, index) => {
                const Icon = step.icon
                return (
                  <SectionReveal key={step.title} delay={index * 0.06}>
                    <div className="surface p-6">
                      <div className="flex gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-border/60 bg-background/82 text-primary">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                            {step.eyebrow}
                          </p>
                          <h3 className="mt-2 text-xl font-semibold tracking-tight">{step.title}</h3>
                          <p className="mt-3 text-sm leading-7 text-muted-foreground">{step.body}</p>
                        </div>
                      </div>
                    </div>
                  </SectionReveal>
                )
              })}
            </div>
          </SectionReveal>
        </div>
      </section>

      <section className="py-20">
        <div className="container mx-auto max-w-7xl px-4">
          <SectionReveal>
            <div className="section-shell overflow-hidden p-8 md:p-10">
              <div className="absolute inset-0 bg-[linear-gradient(120deg,rgba(34,211,238,0.12),transparent_34%,rgba(251,146,60,0.12))]" />
              <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
                <div className="max-w-2xl">
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground/70">Launch next</p>
                  <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-5xl">
                    Move from prototype to a convincing MVP with your own backend attached.
                  </h2>
                  <p className="mt-4 text-sm leading-7 text-muted-foreground">
                    The new UI gives you a better first impression, while the connection state and self-hosted path
                    make it much easier to demo the product on your own infrastructure.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <Link href="/analyze" className="btn btn-primary h-12 px-6">
                    Start analysis
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link href="/docs" className="btn btn-outline h-12 px-6 bg-background/76">
                    Open setup docs
                  </Link>
                </div>
              </div>
            </div>
          </SectionReveal>
        </div>
      </section>
    </SiteShell>
    </ThreeScene>
  )
}

function ScoreRow({
  label,
  value,
  tone,
}: {
  label: string
  value: number
  tone: "cyan" | "blue" | "orange"
}) {
  const barClassName =
    tone === "orange"
      ? "from-orange-400 to-amber-400"
      : tone === "blue"
        ? "from-sky-500 to-indigo-500"
        : "from-cyan-400 to-sky-500"

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs font-medium text-muted-foreground">
        <span>{label}</span>
        <span className="font-mono text-foreground">{value}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted/80">
        <div className={`h-full rounded-full bg-gradient-to-r ${barClassName}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

function ConfigCard({ title, rows }: { title: string; rows: string[] }) {
  return (
    <div className="rounded-[1.2rem] border border-border/60 bg-foreground/[0.035] p-4">
      <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">{title}</div>
      <div className="mt-4 space-y-2">
        {rows.map((row) => (
          <div
            key={row}
            className="rounded-xl border border-border/60 bg-background/80 px-3 py-2 font-mono text-xs text-foreground"
          >
            {row}
          </div>
        ))}
      </div>
    </div>
  )
}

function SurfaceCard({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-[1.2rem] border border-border/60 bg-background/78 p-4">
      <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
        <CheckCircle2 className="h-3.5 w-3.5" />
        {title}
      </div>
      <p className="mt-4 text-sm leading-6 text-muted-foreground">{body}</p>
    </div>
  )
}
