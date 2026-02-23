"use client"

import Link from "next/link"
import { XCircle } from "lucide-react"
import { SiteShell } from "@/components/SiteShell"

export default function PaymentCancelPage() {
  return (
    <SiteShell>
      <section className="container mx-auto max-w-3xl px-4 section">
        <div className="card p-10 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 text-destructive">
            <XCircle className="h-8 w-8" />
          </div>
          <h1 className="mt-6 text-3xl font-semibold">Payment canceled</h1>
          <p className="mt-4 text-muted-foreground">
            The payment flow was canceled. You can try again or return to pricing.
          </p>
          <Link href="/pricing" className="btn btn-outline mt-8 px-6 py-3">
            Back to pricing
          </Link>
        </div>
      </section>
    </SiteShell>
  )
}
