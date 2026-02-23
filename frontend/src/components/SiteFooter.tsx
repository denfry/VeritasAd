"use client"

import Link from "next/link"
import { motion } from "framer-motion"

const footerLinks = [
  { href: "/docs", label: "Documentation" },
  { href: "/pricing", label: "Pricing" },
  { href: "/analyze", label: "Analyze" },
  { href: "/history", label: "History" },
]

export function SiteFooter() {
  return (
    <motion.footer
      className="border-t border-border/50 bg-background/80 backdrop-blur-xl py-12"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
    >
      <div className="container mx-auto max-w-6xl px-4 text-sm text-muted-foreground grid gap-8 md:grid-cols-[1.3fr_0.7fr]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <p className="text-base font-semibold text-foreground">VeritasAd</p>
          <p className="mt-2 max-w-md">
            AI-first advertising disclosure detection for modern marketing teams,
            compliance officers, and social platforms.
          </p>
          <p className="mt-4 text-xs uppercase tracking-[0.2em] text-muted-foreground/70">
            Built with FastAPI, Next.js, and modern ML tooling.
          </p>
        </motion.div>
        
        <motion.div
          className="grid gap-2"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground/70">Product</p>
          {footerLinks.map((link, index) => (
            <motion.div
              key={link.href}
              initial={{ opacity: 0, x: -10 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
            >
              <Link
                href={link.href}
                className="text-muted-foreground hover:text-foreground transition-colors inline-block group"
              >
                {link.label}
                <span className="ml-0 group-hover:ml-1 transition-all duration-300">→</span>
              </Link>
            </motion.div>
          ))}
          <motion.p
            className="pt-4 text-xs"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
          >
            (c) 2026 VeritasAd
          </motion.p>
        </motion.div>
      </div>
    </motion.footer>
  )
}
