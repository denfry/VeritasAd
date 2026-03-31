"use client"

import { AppShell } from "@/components/AppShell"
import { motion } from "framer-motion"
import { XCircle, ArrowLeft, ArrowRight, Zap } from "lucide-react"
import Link from "next/link"

export default function PaymentCancelPage() {
  return (
    <AppShell>
      <section className="container mx-auto max-w-2xl px-4 py-24 lg:py-32">
        <motion.div
          className="surface p-10 text-center space-y-8 relative overflow-hidden"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <div className="absolute -top-24 -right-24 h-48 w-48 bg-amber-500/5 rounded-full blur-3xl" />
          <div className="absolute -bottom-24 -left-24 h-48 w-48 bg-muted/20 rounded-full blur-3xl" />

          <div className="relative z-10 space-y-8">
            <motion.div
              initial={{ scale: 0, rotate: 10 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200, damping: 15 }}
              className="mx-auto h-20 w-20 rounded-full bg-amber-500/10 flex items-center justify-center"
            >
              <XCircle className="h-10 w-10 text-amber-500" />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="space-y-3"
            >
              <h1 className="text-3xl font-semibold tracking-tight">Payment Canceled</h1>
              <p className="text-muted-foreground font-medium max-w-md mx-auto">
                Your payment was not completed. No charges were made. You can try again or explore other options.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="p-6 rounded-2xl bg-muted/20 border border-dashed border-border/50 space-y-4"
            >
              <p className="text-sm text-muted-foreground font-medium">Common reasons for cancellation:</p>
              <ul className="text-sm text-muted-foreground space-y-2 text-left max-w-xs mx-auto">
                <li className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground mt-1.5 flex-shrink-0" />
                  Payment window was closed before completion
                </li>
                <li className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground mt-1.5 flex-shrink-0" />
                  Browser navigation during checkout
                </li>
                <li className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground mt-1.5 flex-shrink-0" />
                  Payment method declined
                </li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex flex-col sm:flex-row gap-3 justify-center pt-2"
            >
              <Link
                href="/pricing"
                className="btn btn-primary h-12 px-8 rounded-full font-semibold gap-2 shadow-lg shadow-primary/20 transition-all hover:scale-105"
              >
                <Zap className="h-4 w-4" />
                View Pricing Plans
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/dashboard"
                className="btn btn-outline h-12 px-8 rounded-full font-semibold gap-2 transition-all hover:scale-105"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Link>
            </motion.div>
          </div>
        </motion.div>
      </section>
    </AppShell>
  )
}
