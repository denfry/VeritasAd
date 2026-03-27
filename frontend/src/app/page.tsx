"use client"

import Link from "next/link"
import { motion, useReducedMotion } from "framer-motion"
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  ShieldCheck,
  SparklesIcon,
  SquareStack,
  Zap,
} from "lucide-react"
import { SiteShell } from "@/components/SiteShell"
import { CountUp } from "@/components/ui/CountUp"
import { SectionReveal } from "@/components/SectionReveal"

const featureCards = [
  {
    title: "Multimodal detection",
    desc: "Visual, audio, and text signals analyzed together for stronger disclosure coverage.",
    icon: BrainCircuit,
    span: "md:col-span-2",
  },
  {
    title: "Fast compliance view",
    desc: "See the signal, the evidence, and the risk at a glance.",
    icon: ShieldCheck,
    span: "md:col-span-1",
  },
  {
    title: "Workflow speed",
    desc: "Upload, inspect, export, and share without leaving the analysis flow.",
    icon: Zap,
    span: "md:col-span-1",
  },
  {
    title: "Actionable output",
    desc: "From score to structured report, built for review and decision-making.",
    icon: BarChart3,
    span: "md:col-span-2",
  },
]

const proofStats = [
  { label: "Analyses completed", value: 12840 },
  { label: "Average confidence", value: 98.4, decimals: 1 },
  { label: "Minutes saved / week", value: 420 },
  { label: "Brands tracked", value: 760 },
]

export default function HomePage() {
  const reduceMotion = useReducedMotion()

  return (
    <SiteShell>
      <section className="relative overflow-hidden border-b border-border/40">
        <div className="container mx-auto max-w-7xl px-4 pt-20 pb-16 lg:pt-28 lg:pb-24">
          <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
            <SectionReveal className="relative z-10">
              <div className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-background/75 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur-md">
                <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_16px_rgba(16,185,129,0.45)]" />
                Intelligence for advertising compliance
              </div>

              <h1 className="mt-6 max-w-3xl text-balance text-5xl font-semibold tracking-tight text-foreground sm:text-6xl lg:text-7xl">
                Detect hidden advertising with a{" "}
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-sky-400 via-cyan-300 to-blue-500">
                  premium compliance engine
                </span>
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
                Verify sponsorships, brand mentions, and disclosure signals across video, audio, and text.
                Designed for teams that need fast decisions, clean evidence, and a product that feels
                serious from the first click.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <Link
                  href="/analyze"
                  className="btn btn-primary h-12 px-6 shadow-[0_18px_40px_-14px_hsl(var(--primary)/0.6)]"
                >
                  Start analysis
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="/docs"
                  className="btn btn-outline h-12 px-6 bg-background/70 backdrop-blur-sm"
                >
                  View docs
                </Link>
              </div>

              <div className="mt-8 flex flex-wrap gap-2">
                {["Video", "Audio", "Text", "Reports", "API"].map((item) => (
                  <span
                    key={item}
                    className="rounded-full border border-border/70 bg-background/75 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur-sm"
                  >
                    {item}
                  </span>
                ))}
              </div>

              <div className="mt-10 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {proofStats.map((stat) => (
                  <div key={stat.label} className="card surface p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground/70">
                      {stat.label}
                    </div>
                    <div className="mt-3 text-3xl font-semibold tracking-tight">
                      <CountUp end={stat.value} decimals={stat.decimals ?? 0} />
                      {stat.label === "Average confidence" ? "%" : ""}
                    </div>
                  </div>
                ))}
              </div>
            </SectionReveal>

            <SectionReveal delay={0.06}>
              <div className="relative">
                <div className="absolute -inset-6 rounded-[2rem] bg-gradient-to-br from-primary/10 via-cyan-400/5 to-transparent blur-2xl" />
                <div className="surface relative overflow-hidden border-border/60 p-4 shadow-[0_40px_120px_rgba(0,0,0,0.18)]">
                  <div className="rounded-[1.1rem] border border-border/60 bg-background/90 p-5 backdrop-blur-xl">
                    <div className="flex items-center justify-between border-b border-border/60 pb-4">
                      <div className="flex items-center gap-2">
                        <span className="h-3 w-3 rounded-full bg-red-500/80" />
                        <span className="h-3 w-3 rounded-full bg-amber-400/80" />
                        <span className="h-3 w-3 rounded-full bg-emerald-400/80" />
                      </div>
                      <div className="text-xs font-medium text-muted-foreground">Analysis preview</div>
                    </div>

                    <div className="mt-5 grid gap-4">
                      <div className="rounded-2xl border border-border/60 bg-muted/35 p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground/70">
                              Confidence score
                            </p>
                            <div className="mt-2 text-4xl font-semibold tracking-tight text-foreground">
                              <CountUp end={98.4} decimals={1} />%
                            </div>
                          </div>
                          <div className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-500">
                            Verified
                          </div>
                        </div>
                        <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted/80">
                          <div className="h-full w-[84%] rounded-full bg-gradient-to-r from-sky-400 via-cyan-400 to-blue-500" />
                        </div>
                      </div>

                      <div className="grid gap-3 sm:grid-cols-3">
                        {[
                          ["Detected brands", "12"],
                          ["Disclosure markers", "4"],
                          ["Review time", "42s"],
                        ].map(([label, value]) => (
                          <div key={label} className="rounded-2xl border border-border/60 bg-background/80 p-4">
                            <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground/70">
                              {label}
                            </div>
                            <div className="mt-3 text-2xl font-semibold tracking-tight">{value}</div>
                          </div>
                        ))}
                      </div>

                      <div className="grid gap-3 md:grid-cols-[1.25fr_0.75fr]">
                        <div className="rounded-2xl border border-border/60 bg-background/80 p-4">
                          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground/70">
                            Evidence summary
                          </p>
                          <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Visual logo exposure, spoken brand names, and missing disclosure labels detected
                            within a single review pass.
                          </p>
                        </div>
                        <div className="rounded-2xl border border-border/60 bg-background/80 p-4">
                          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground/70">
                            Status
                          </p>
                          <div className="mt-3 inline-flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-500">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            Complete
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {!reduceMotion ? (
                  <motion.div
                    className="pointer-events-none absolute -right-4 top-8 hidden rounded-full border border-border/60 bg-background/85 px-4 py-2 text-xs font-medium text-muted-foreground shadow-lg backdrop-blur-md lg:block"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 6, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
                  >
                    Live analysis
                  </motion.div>
                ) : null}
                {!reduceMotion ? (
                  <motion.div
                    className="pointer-events-none absolute -left-6 bottom-10 hidden rounded-full border border-border/60 bg-background/85 px-4 py-2 text-xs font-medium text-muted-foreground shadow-lg backdrop-blur-md lg:block"
                    animate={{ y: [0, 10, 0] }}
                    transition={{ duration: 7, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
                  >
                    Brand exposure
                  </motion.div>
                ) : null}
              </div>
            </SectionReveal>
          </div>
        </div>
      </section>

      <section className="border-b border-border/40 py-20">
        <div className="container mx-auto max-w-7xl px-4">
          <SectionReveal className="flex items-end justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                Why teams use VeritasAd
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-4xl">
                More signal, less noise.
              </h2>
            </div>
            <p className="hidden max-w-xl text-sm leading-6 text-muted-foreground md:block">
              The site should feel like a high-end product command center: precise, readable, layered,
              and able to explain itself without visual clutter.
            </p>
          </SectionReveal>

          <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {featureCards.map((feature, index) => {
              const Icon = feature.icon
              return (
                <SectionReveal key={feature.title} delay={index * 0.05} className={feature.span}>
                  <div className="surface group relative h-full overflow-hidden p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_28px_70px_rgba(0,0,0,0.14)]">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/0 via-primary/0 to-cyan-400/10 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                    <div className="relative">
                      <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-border/60 bg-background/80 text-primary shadow-sm">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="mt-5 text-xl font-semibold tracking-tight">{feature.title}</h3>
                      <p className="mt-3 max-w-md text-sm leading-6 text-muted-foreground">{feature.desc}</p>
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
          <SectionReveal className="grid gap-4 md:grid-cols-3">
            <div className="surface md:col-span-2 p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                Detection flow
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight">One analysis, structured for decisions.</h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-muted-foreground">
                The workflow stays fast, but the output looks like a polished report: clear confidence,
                evidence, timestamps, and next steps in one readable system.
              </p>
            </div>

            <div className="surface p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                Motion rules
              </p>
              <div className="mt-4 space-y-3 text-sm leading-6 text-muted-foreground">
                <div className="flex items-center gap-2"><SparklesIcon className="h-4 w-4 text-primary" />Reveal on scroll</div>
                <div className="flex items-center gap-2"><SquareStack className="h-4 w-4 text-primary" />Bento grids for features</div>
                <div className="flex items-center gap-2"><Clock3 className="h-4 w-4 text-primary" />Counters in viewport only</div>
              </div>
            </div>
          </SectionReveal>
        </div>
      </section>

      <section className="relative overflow-hidden py-20">
        <div className="container mx-auto max-w-7xl px-4">
          <SectionReveal>
            <div className="relative overflow-hidden rounded-[2rem] border border-border/60 bg-background/75 p-8 shadow-[0_24px_80px_rgba(0,0,0,0.12)] backdrop-blur-2xl">
              <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-cyan-400/5 to-transparent" />
              <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                <div className="max-w-2xl">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                    Final CTA
                  </p>
                  <h2 className="mt-3 text-3xl font-semibold tracking-tight lg:text-4xl">
                    Ship a compliance product that feels as premium as the data it produces.
                  </h2>
                  <p className="mt-4 text-sm leading-7 text-muted-foreground">
                    Use the same system across landing, analysis, dashboard, docs, and auth so the whole site
                    reads like one product, not a set of disconnected pages.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <Link href="/analyze" className="btn btn-primary h-12 px-6">
                    Start analysis
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link href="/pricing" className="btn btn-outline h-12 px-6 bg-background/75">
                    See pricing
                  </Link>
                </div>
              </div>
            </div>
          </SectionReveal>
        </div>
      </section>
    </SiteShell>
  )
}
