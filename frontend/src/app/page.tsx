"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, CheckCircle2, Shield, Zap, BarChart3, Lock } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export default function HomePage() {
  return (
    <SiteShell>
      {/* Hero Section */}
      <section className="relative border-b bg-background pt-24 pb-32 overflow-hidden">
        {/* Subtle Grid Background */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:32px_32px]"></div>
        
        {/* Radial mask for the grid */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,hsl(var(--background))_80%)]"></div>
        
        <div className="container relative mx-auto max-w-5xl px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
            className="inline-flex items-center rounded-full border bg-muted/30 px-3 py-1 text-xs font-medium text-muted-foreground mb-12 backdrop-blur-sm"
          >
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
            Intelligence for Advertising Compliance
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1, ease: [0.23, 1, 0.32, 1] }}
            className="text-5xl font-bold tracking-tight sm:text-7xl md:text-8xl leading-[1.1] bg-clip-text text-transparent bg-gradient-to-b from-foreground to-foreground/50"
          >
            Detect Hidden <br className="hidden sm:block" />
            Advertising.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2, ease: [0.23, 1, 0.32, 1] }}
            className="mx-auto mt-8 max-w-xl text-lg text-muted-foreground/80 leading-relaxed"
          >
            Verify integrations with multi-modal AI. Analyze visual, 
            audio and text disclosure signals across all platforms.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3, ease: [0.23, 1, 0.32, 1] }}
            className="mt-12 flex items-center justify-center gap-4"
          >
            <Link href="/analyze" className="btn btn-primary h-12 px-10 rounded-full font-semibold transition-all hover:scale-[1.02] active:scale-[0.98]">
              Get Started
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link href="/docs" className="btn btn-outline h-12 px-10 rounded-full bg-background/50 backdrop-blur-sm">
              Documentation
            </Link>
          </motion.div>

          {/* Abstract UI Preview with sharper styles */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: [0.23, 1, 0.32, 1] }}
            className="mt-24 relative mx-auto max-w-4xl"
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-border/50 via-primary/5 to-border/50 rounded-2xl blur-sm opacity-50"></div>
            <div className="relative rounded-2xl border bg-card/30 p-2 shadow-2xl backdrop-blur-xl">
              <div className="rounded-xl border bg-background/80 p-6 aspect-[16/9] flex flex-col gap-6 overflow-hidden">
                <div className="flex items-center justify-between border-b pb-4">
                  <div className="flex gap-2">
                    <div className="h-3 w-3 rounded-full bg-red-500/20"></div>
                    <div className="h-3 w-3 rounded-full bg-amber-500/20"></div>
                    <div className="h-3 w-3 rounded-full bg-emerald-500/20"></div>
                  </div>
                  <div className="h-4 w-32 bg-muted rounded"></div>
                </div>
                <div className="flex-1 grid grid-cols-12 gap-6">
                  <div className="col-span-8 flex flex-col gap-4">
                    <div className="h-4 w-1/2 bg-muted rounded"></div>
                    <div className="flex-1 bg-muted/20 rounded-lg border border-dashed flex items-center justify-center">
                       <BarChart3 className="h-12 w-12 text-muted-foreground/10" />
                    </div>
                  </div>
                  <div className="col-span-4 flex flex-col gap-4">
                    <div className="h-24 bg-muted/40 rounded-lg"></div>
                    <div className="h-24 bg-muted/40 rounded-lg"></div>
                    <div className="h-24 bg-muted/40 rounded-lg"></div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-muted/30 border-b">
        <div className="container mx-auto max-w-6xl px-4">
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-3">
            <Feature 
              icon={Shield}
              title="Brand Safety"
              desc="Ensure all content meets regulatory requirements with automated disclosure checks."
            />
            <Feature 
              icon={Zap}
              title="Real-time Processing"
              desc="Upload videos or paste URLs. Get comprehensive analysis in minutes, not hours."
            />
            <Feature 
              icon={Lock}
              title="Enterprise Security"
              desc="Your data is processed in isolated environments with strict retention policies."
            />
          </div>
        </div>
      </section>
    </SiteShell>
  )
}

function Feature({ icon: Icon, title, desc }: { icon: any, title: string, desc: string }) {
  return (
    <div className="group space-y-3">
      <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg border bg-background shadow-sm transition-colors group-hover:border-primary/50">
        <Icon className="h-6 w-6 text-foreground" />
      </div>
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="text-muted-foreground">{desc}</p>
    </div>
  )
}
