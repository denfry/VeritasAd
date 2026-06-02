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
  Sparkles,
  TrendingUp,
  FileText,
} from "lucide-react"
import { ApiConnectionStatus } from "@/components/ApiConnectionStatus"
import { SectionReveal } from "@/components/SectionReveal"
import { SiteShell } from "@/components/SiteShell"
import { CountUp } from "@/components/ui/CountUp"
import { ThreeScene } from "@/components/three/ThreeScene"
import { useLanguage } from "@/contexts/language-context"

export default function HomePage() {
  const reduceMotion = useReducedMotion()
  const { scrollYProgress } = useScroll()
  const previewY = useTransform(scrollYProgress, [0, 1], [0, reduceMotion ? 0 : -100])
  const haloY = useTransform(scrollYProgress, [0, 1], [0, reduceMotion ? 0 : 160])
  const { t } = useLanguage()
  const h = t.home

  const proofStats = [
    { label: h.stats.analyses, value: 12840, icon: TrendingUp },
    { label: h.stats.confidence, value: 98.4, decimals: 1, suffix: "%", icon: ShieldCheck },
    { label: h.stats.brands, value: 317000, icon: Eye },
    { label: h.stats.reports, value: 9420, icon: FileText },
  ]

  const signalTiles = [
    { label: h.signalBrands, value: "12", icon: Eye },
    { label: h.signalVoice, value: "7", icon: AudioLines },
    { label: h.signalDisclosure, value: "4", icon: ShieldCheck },
  ]

  const pillarIcons = [BrainCircuit, Radar, Server]
  const pillarAccents = [
    "from-cyan-500/20 to-sky-500/5",
    "from-sky-500/20 to-indigo-500/5",
    "from-orange-400/20 to-amber-400/5",
  ]
  const pillarIconBgs = [
    "bg-cyan-500/10 text-cyan-500",
    "bg-sky-500/10 text-sky-500",
    "bg-orange-400/10 text-orange-500",
  ]

  const pipelineIcons = [Boxes, Waves, BadgeCheck]

  return (
    <ThreeScene intensity="medium" type="neural">
      <SiteShell>

        {/* ── Hero ── */}
        <section className="relative overflow-hidden border-b border-border/40">
          <div className="container mx-auto max-w-7xl px-4 pt-16 pb-20 lg:pt-24 lg:pb-28">
            <div className="grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
              <SectionReveal className="relative z-10">
                {/* Eyebrow pill + status */}
                <div className="flex flex-wrap items-center gap-3">
                  <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-background/80 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground backdrop-blur-xl">
                    <span className="status-dot status-dot-green" />
                    {h.heroBadge}
                  </span>
                  <ApiConnectionStatus compact />
                </div>

                {/* Headline */}
                <h1 className="display-type mt-7 max-w-4xl text-5xl font-semibold leading-[0.95] sm:text-6xl lg:text-7xl xl:text-[5.4rem]">
                  {h.heroTitle1}{" "}
                  <span className="gradient-text">{h.heroTitle2}</span>{" "}
                  {h.heroTitle3}
                </h1>

                <p className="mt-6 max-w-xl text-lg leading-8 text-muted-foreground">
                  {h.heroDescription}
                </p>

                {/* CTAs */}
                <div className="mt-9 flex flex-wrap gap-3">
                  <Link
                    href="/analyze"
                    className="btn btn-primary btn-premium h-12 px-7 shadow-[0_20px_50px_-18px_hsl(var(--primary)/0.8)]"
                  >
                    {h.ctaAnalyze}
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link href="/docs" className="btn btn-outline h-12 px-6">
                    {h.ctaDocs}
                  </Link>
                </div>

                {/* Feature pills */}
                <div className="mt-8 flex flex-wrap gap-2">
                  {h.featurePills.map((item) => (
                    <span
                      key={item}
                      className="rounded-full border border-border/60 bg-background/70 px-3 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur-xl"
                    >
                      {item}
                    </span>
                  ))}
                </div>

                {/* Stats grid */}
                <div className="mt-10 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  {proofStats.map((stat) => {
                    const Icon = stat.icon
                    return (
                      <div key={stat.label} className="card bg-noise p-4 hover:shadow-[0_8px_30px_rgba(0,0,0,0.10)] transition-shadow duration-300">
                        <div className="flex items-center gap-2">
                          <Icon className="h-3.5 w-3.5 text-primary/60" />
                          <span className="eyebrow">{stat.label}</span>
                        </div>
                        <div className="mt-3 text-[1.75rem] font-semibold tracking-tight">
                          <CountUp end={stat.value} decimals={stat.decimals ?? 0} />
                          {stat.suffix ?? ""}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </SectionReveal>

              {/* Preview card */}
              <SectionReveal delay={0.06}>
                <div className="relative">
                  <motion.div
                    className="absolute inset-x-[8%] top-4 h-40 rounded-full bg-gradient-to-r from-cyan-400/18 via-sky-400/18 to-orange-300/18 blur-3xl"
                    style={{ y: haloY }}
                  />

                  <motion.div
                    className="section-shell bg-noise relative p-4 md:p-5"
                    style={{ y: previewY }}
                  >
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,hsl(var(--primary)/0.14),transparent_32%),linear-gradient(135deg,rgba(255,255,255,0.07),transparent_36%)]" />

                    <div className="relative rounded-[1.5rem] border border-border/60 bg-background/86 p-5 backdrop-blur-2xl">
                      {/* Window chrome */}
                      <div className="flex items-center justify-between border-b border-border/60 pb-4">
                        <div className="flex items-center gap-2">
                          <span className="h-3 w-3 rounded-full bg-red-500/70" />
                          <span className="h-3 w-3 rounded-full bg-amber-400/70" />
                          <span className="h-3 w-3 rounded-full bg-emerald-400/70" />
                        </div>
                        <span className="badge badge-green">
                          <Activity className="h-3 w-3" />
                          {h.previewLiveSystem}
                        </span>
                      </div>

                      <div className="mt-5 grid gap-4">
                        {/* Verdict + signal tiles */}
                        <div className="grid gap-4 md:grid-cols-[1.1fr_0.9fr]">
                          {/* Verdict */}
                          <div className="rounded-[1.3rem] border border-border/60 bg-gradient-to-br from-cyan-500/10 via-sky-500/5 to-orange-400/5 p-5">
                            <p className="eyebrow">{h.previewVerdict}</p>
                            <div className="mt-3 flex items-end justify-between gap-4">
                              <div>
                                <div className="text-4xl font-semibold tracking-tight">
                                  <CountUp end={98.4} decimals={1} />%
                                </div>
                                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                  {h.previewConfidenceDesc}
                                </p>
                              </div>
                              <span className="badge badge-green whitespace-nowrap">{h.previewVerified}</span>
                            </div>
                            <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted/60">
                              <div className="h-full w-[88%] rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-orange-400" />
                            </div>
                          </div>

                          {/* Signal tiles */}
                          <div className="grid gap-3">
                            {signalTiles.map(({ label, value, icon: Icon }) => (
                              <div key={label} className="rounded-[1.2rem] border border-border/60 bg-background/84 p-4">
                                <div className="flex items-center justify-between">
                                  <p className="eyebrow">{label}</p>
                                  <Icon className="h-4 w-4 text-primary/70" />
                                </div>
                                <div className="mt-2 text-2xl font-semibold tracking-tight">{value}</div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Pipeline + evidence */}
                        <div className="grid gap-3 md:grid-cols-[1.2fr_0.8fr]">
                          <div className="rounded-[1.3rem] border border-border/60 bg-background/84 p-4">
                            <p className="eyebrow">{h.previewPipeline}</p>
                            <div className="mt-4 grid gap-2.5">
                              {[
                                [h.previewUploadDone, h.statusDone, "badge-green"],
                                [h.previewSpeechActive, h.statusActive, "badge-primary"],
                                [h.previewReportQueued, h.statusQueued, "badge-amber"],
                              ].map(([step, status, tone]) => (
                                <div key={step} className="flex items-center justify-between rounded-2xl border border-border/50 bg-muted/15 px-4 py-2.5">
                                  <span className="text-sm font-medium">{step}</span>
                                  <span className={`badge ${tone}`}>{status}</span>
                                </div>
                              ))}
                            </div>
                          </div>

                          <div className="rounded-[1.3rem] border border-border/60 bg-background/84 p-4">
                            <p className="eyebrow">{h.previewEvidence}</p>
                            <div className="mt-4 space-y-3">
                              <ScoreRow label={h.evidenceVisual} value={78} tone="cyan" />
                              <ScoreRow label={h.evidenceAudio} value={61} tone="blue" />
                              <ScoreRow label={h.evidenceDisclosure} value={34} tone="orange" />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Floating tooltips */}
                    {!reduceMotion ? (
                      <>
                        <motion.div
                          className="pointer-events-none absolute -left-5 top-16 hidden rounded-full border border-border/60 bg-background/90 px-4 py-2 text-xs font-medium text-muted-foreground shadow-xl backdrop-blur-xl lg:block"
                          animate={{ y: [0, -10, 0] }}
                          transition={{ duration: 7, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
                        >
                          {h.previewTooltip1}
                        </motion.div>
                        <motion.div
                          className="pointer-events-none absolute -right-6 bottom-12 hidden rounded-full border border-border/60 bg-background/90 px-4 py-2 text-xs font-medium text-muted-foreground shadow-xl backdrop-blur-xl lg:block"
                          animate={{ y: [0, 10, 0] }}
                          transition={{ duration: 8, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
                        >
                          {h.previewTooltip2}
                        </motion.div>
                      </>
                    ) : null}
                  </motion.div>
                </div>
              </SectionReveal>
            </div>
          </div>
        </section>

        {/* ── Pillars ── */}
        <section className="border-b border-border/40 py-20">
          <div className="container mx-auto max-w-7xl px-4">
            <SectionReveal className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
              <div className="max-w-xl">
                <p className="eyebrow">{h.pillarsEyebrow}</p>
                <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-5xl">
                  {h.pillarsTitle}
                </h2>
              </div>
              <p className="max-w-md text-sm leading-7 text-muted-foreground">
                {h.pillarsDescription}
              </p>
            </SectionReveal>

            <div className="mt-10 grid gap-4 lg:grid-cols-3">
              {h.pillars.map((pillar, index) => {
                const Icon = pillarIcons[index]
                return (
                  <SectionReveal key={pillar.title} delay={index * 0.06}>
                    <div className="surface bg-noise group relative h-full overflow-hidden p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_70px_rgba(0,0,0,0.14)]">
                      <div className={`absolute inset-0 bg-gradient-to-br ${pillarAccents[index]} opacity-100`} />
                      <div className="relative">
                        <div className={`inline-flex h-11 w-11 items-center justify-center rounded-2xl ${pillarIconBgs[index]} border border-border/40`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <h3 className="mt-5 text-xl font-semibold tracking-tight">{pillar.title}</h3>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">{pillar.description}</p>
                      </div>
                    </div>
                  </SectionReveal>
                )
              })}
            </div>
          </div>
        </section>

        {/* ── MVP path + API status ── */}
        <section className="border-b border-border/40 py-20">
          <div className="container mx-auto max-w-7xl px-4">
            <div className="grid gap-6 lg:grid-cols-[0.96fr_1.04fr]">
              <SectionReveal className="space-y-6">
                <div className="section-shell bg-noise p-8">
                  <p className="eyebrow">{h.mvpEyebrow}</p>
                  <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-4xl">
                    {h.mvpTitle}
                  </h2>
                  <p className="mt-4 text-sm leading-7 text-muted-foreground">
                    {h.mvpDescription}
                  </p>

                  <div className="mt-6 space-y-3">
                    {h.mvpSteps.map((step, index) => (
                      <div key={step.title} className="rounded-[1.3rem] border border-border/60 bg-background/76 p-4">
                        <div className="flex items-center gap-3">
                          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[11px] font-bold text-primary">
                            {index + 1}
                          </span>
                          <h3 className="text-sm font-semibold">{step.title}</h3>
                        </div>
                        <p className="mt-2 pl-9 text-sm leading-6 text-muted-foreground">{step.detail}</p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 grid gap-3 md:grid-cols-2">
                    <ConfigCard
                      title={h.frontendEnv}
                      rows={[
                        "NEXT_PUBLIC_API_URL=https://api.your-domain.com",
                        "NEXT_PUBLIC_DISABLE_AUTH=true",
                      ]}
                    />
                    <ConfigCard
                      title={h.backendEnv}
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
                  <p className="eyebrow">{h.productSurfaces}</p>
                  <div className="mt-5 grid gap-4 md:grid-cols-3">
                    {h.surfaces.map((s) => (
                      <SurfaceCard key={s.title} title={s.title} body={s.body} />
                    ))}
                  </div>
                </div>
              </SectionReveal>
            </div>
          </div>
        </section>

        {/* ── Pipeline ── */}
        <section className="border-b border-border/40 py-20">
          <div className="container mx-auto max-w-7xl px-4">
            <SectionReveal className="grid gap-6 lg:grid-cols-[0.92fr_1.08fr]">
              <div className="section-shell p-8">
                <p className="eyebrow">{h.pipelineEyebrow}</p>
                <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-4xl">
                  {h.pipelineTitle}
                </h2>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">
                  {h.pipelineDescription}
                </p>
              </div>

              <div className="space-y-4">
                {h.pipeline.map((step, index) => {
                  const Icon = pipelineIcons[index]
                  return (
                    <SectionReveal key={step.title} delay={index * 0.06}>
                      <div className="surface p-6 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_16px_50px_rgba(0,0,0,0.12)]">
                        <div className="flex gap-4">
                          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-border/60 bg-background/82 text-primary">
                            <Icon className="h-5 w-5" />
                          </div>
                          <div>
                            <p className="eyebrow">{step.eyebrow}</p>
                            <h3 className="mt-2 text-xl font-semibold tracking-tight">{step.title}</h3>
                            <p className="mt-2 text-sm leading-7 text-muted-foreground">{step.body}</p>
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

        {/* ── CTA ── */}
        <section className="py-20">
          <div className="container mx-auto max-w-7xl px-4">
            <SectionReveal>
              <div className="section-shell relative overflow-hidden p-8 md:p-12">
                <div className="absolute inset-0 bg-[linear-gradient(120deg,rgba(34,211,238,0.10),transparent_36%,rgba(251,146,60,0.10))]" />
                <div className="absolute inset-0 bg-dots opacity-40" />
                <div className="relative flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
                  <div className="max-w-2xl">
                    <p className="eyebrow">{h.ctaEyebrow}</p>
                    <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-5xl">
                      {h.ctaTitle}
                    </h2>
                    <p className="mt-4 text-sm leading-7 text-muted-foreground">
                      {h.ctaDescription}
                    </p>
                  </div>
                  <div className="flex flex-shrink-0 flex-wrap gap-3">
                    <Link href="/analyze" className="btn btn-primary btn-premium h-12 px-7">
                      <Sparkles className="h-4 w-4" />
                      {h.ctaStartAnalysis}
                    </Link>
                    <Link href="/docs" className="btn btn-outline h-12 px-6">
                      {h.ctaOpenDocs}
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
  const barClass =
    tone === "orange"
      ? "from-orange-400 to-amber-400"
      : tone === "blue"
        ? "from-sky-500 to-indigo-500"
        : "from-cyan-400 to-sky-500"

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs font-medium text-muted-foreground">
        <span>{label}</span>
        <span className="font-mono text-foreground">{value}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-muted/70">
        <div className={`h-full rounded-full bg-gradient-to-r ${barClass}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

function ConfigCard({ title, rows }: { title: string; rows: string[] }) {
  return (
    <div className="rounded-[1.2rem] border border-border/60 bg-foreground/[0.03] p-4">
      <p className="eyebrow">{title}</p>
      <div className="mt-3 space-y-2">
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
    <div className="rounded-[1.2rem] border border-border/60 bg-background/78 p-4 transition-all duration-200 hover:border-primary/30">
      <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/8 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
        <CheckCircle2 className="h-3.5 w-3.5" />
        {title}
      </div>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{body}</p>
    </div>
  )
}
