"use client"

import Link from "next/link"
import { ShieldCheck } from "lucide-react"
import { motion } from "framer-motion"

const productLinks = [
  { href: "/analyze", label: "Analyze" },
  { href: "/history", label: "History" },
  { href: "/pricing", label: "Pricing" },
  { href: "/docs", label: "Documentation" },
]

const legalLinks = [
  { href: "/legal/terms", label: "Terms of Service" },
  { href: "/legal/privacy", label: "Privacy Policy" },
  { href: "/legal/cookies", label: "Cookie Policy" },
  { href: "/legal/gdpr", label: "GDPR Rights" },
  { href: "/legal/disclaimer", label: "Disclaimer" },
]

export function SiteFooter() {
  return (
    <footer className="border-t border-border/50 bg-background/80 backdrop-blur-2xl">
      <div className="container mx-auto max-w-6xl px-4 py-12">
        <div className="grid gap-10 md:grid-cols-[1.5fr_0.75fr_0.75fr]">
          {/* Brand column */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
          >
            <Link href="/" className="inline-flex items-center gap-2.5 group">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full gradient-premium text-primary-foreground shadow-[0_8px_20px_-8px_hsl(var(--primary)/0.5)]">
                <ShieldCheck className="h-4 w-4" />
              </span>
              <span className="gradient-text text-base font-semibold">VeritasAd</span>
            </Link>

            <p className="mt-4 max-w-xs text-sm leading-6 text-muted-foreground text-balance">
              AI-first advertising disclosure detection for marketing teams, compliance
              officers, and social platforms.
            </p>

            <p className="mt-5 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground/50">
              Built with FastAPI · Next.js · ML
            </p>
          </motion.div>

          {/* Product links */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.08 }}
          >
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground/60 mb-4">
              Product
            </p>
            <ul className="space-y-3">
              {productLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1 group"
                  >
                    <span className="group-hover:translate-x-0.5 transition-transform duration-200">
                      {link.label}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Legal links */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.14 }}
          >
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground/60 mb-4">
              Legal
            </p>
            <ul className="space-y-3">
              {legalLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1 group"
                  >
                    <span className="group-hover:translate-x-0.5 transition-transform duration-200">
                      {link.label}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Bottom bar */}
        <motion.div
          className="mt-10 pt-6 border-t border-border/40 flex flex-col sm:flex-row items-center justify-between gap-3"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
        >
          <p className="text-xs text-muted-foreground/60">
            © {new Date().getFullYear()} VeritasAd. All rights reserved.
          </p>
          <div className="flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.6)]" />
            <span className="text-xs text-muted-foreground/60">All systems operational</span>
          </div>
        </motion.div>
      </div>
    </footer>
  )
}
