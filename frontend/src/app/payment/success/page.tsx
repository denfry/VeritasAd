"use client"

import { AppShell } from "@/components/AppShell"
import { motion } from "framer-motion"
import { CheckCircle2, ArrowRight, LayoutDashboard, Search, Sparkles } from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense } from "react"

function PaymentSuccessContent() {
  const searchParams = useSearchParams()
  const credits = searchParams.get("credits")
  const plan = searchParams.get("plan")
  const transactionId = searchParams.get("transaction_id")

  return (
    <AppShell>
      <section className="container mx-auto max-w-2xl px-4 py-24 lg:py-32">
        <motion.div
          className="surface p-10 text-center space-y-8 relative overflow-hidden"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <div className="absolute -top-24 -right-24 h-48 w-48 bg-emerald-500/5 rounded-full blur-3xl" />
          <div className="absolute -bottom-24 -left-24 h-48 w-48 bg-primary/5 rounded-full blur-3xl" />

          <div className="relative z-10 space-y-8">
            <motion.div
              initial={{ scale: 0, rotate: -10 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200, damping: 15 }}
              className="mx-auto h-20 w-20 rounded-full bg-emerald-500/10 flex items-center justify-center"
            >
              <CheckCircle2 className="h-10 w-10 text-emerald-500" />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="space-y-3"
            >
              <h1 className="text-3xl font-semibold tracking-tight">Payment Successful</h1>
              <p className="text-muted-foreground font-medium">
                Your purchase has been processed and your account has been updated.
              </p>
            </motion.div>

            {(credits || plan) && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="p-6 rounded-2xl bg-muted/30 border border-border/50 space-y-4"
              >
                {plan && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground font-medium">Plan</span>
                      <span className="text-sm font-semibold capitalize flex items-center gap-1.5">
                        <Sparkles className="h-3.5 w-3.5 text-primary" />
                        {plan}
                      </span>
                    </div>
                    <div className="h-px bg-border/50" />
                  </>
                )}
                {credits && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground font-medium">Credits added</span>
                      <span className="text-lg font-bold text-emerald-500">+{credits}</span>
                    </div>
                    <div className="h-px bg-border/50" />
                  </>
                )}
                {transactionId && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground font-medium">Transaction ID</span>
                    <span className="text-xs font-mono text-muted-foreground">{transactionId}</span>
                  </div>
                )}
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex flex-col sm:flex-row gap-3 justify-center pt-2"
            >
              <Link
                href="/dashboard"
                className="btn btn-primary h-12 px-8 rounded-full font-semibold gap-2 shadow-lg shadow-primary/20 transition-all hover:scale-105"
              >
                <LayoutDashboard className="h-4 w-4" />
                Go to Dashboard
              </Link>
              <Link
                href="/analyze"
                className="btn btn-outline h-12 px-8 rounded-full font-semibold gap-2 transition-all hover:scale-105"
              >
                <Search className="h-4 w-4" />
                Start Analyzing
                <ArrowRight className="h-4 w-4" />
              </Link>
            </motion.div>
          </div>
        </motion.div>
      </section>
    </AppShell>
  )
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <AppShell>
        <div className="container mx-auto max-w-2xl px-4 py-24 lg:py-32">
          <div className="surface p-10 text-center">Loading...</div>
        </div>
      </AppShell>
    }>
      <PaymentSuccessContent />
    </Suspense>
  )
}
