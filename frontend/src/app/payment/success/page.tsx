"use client"

import Link from "next/link"
import { CheckCircle2 } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export default function PaymentSuccessPage() {
  return (
    <SiteShell>
      <section className="container mx-auto max-w-3xl px-4 section">
        <div className="card p-10 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
            <CheckCircle2 className="h-8 w-8" />
          </div>
          <h1 className="mt-6 text-3xl font-semibold">Payment successful</h1>
          <p className="mt-4 text-muted-foreground">
            Your Pro subscription is now active. You can return to the dashboard to see updated
            limits.
          </p>
          <Link href="/dashboard" className="btn btn-primary mt-8 px-6 py-3">
            Go to dashboard
          </Link>
        </div>
      </section>
    </SiteShell>
  )
}
