"use client"

import { useState, type FormEvent } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { ArrowRight, Loader2, ShieldCheck } from "lucide-react"
import { toast } from "sonner"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { ThreeScene } from "@/components/three/ThreeScene"

export default function RegisterPage() {
  const router = useRouter()
  const { signUp, isMock } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<{ email?: string; password?: string; confirmPassword?: string }>({})

  const validate = (emailValue = email, passwordValue = password, confirmValue = confirmPassword) => {
    const nextErrors: typeof errors = {}

    if (!emailValue.trim()) {
      nextErrors.email = "Email is required"
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue)) {
      nextErrors.email = "Invalid email format"
    }

    if (!passwordValue) {
      nextErrors.password = "Password is required"
    } else if (passwordValue.length < 8) {
      nextErrors.password = "Password must be at least 8 characters"
    }

    if (!confirmValue) {
      nextErrors.confirmPassword = "Please confirm your password"
    } else if (passwordValue && confirmValue !== passwordValue) {
      nextErrors.confirmPassword = "Passwords do not match"
    }

    setErrors(nextErrors)
    return nextErrors
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const nextErrors = validate()
    if (Object.keys(nextErrors).length > 0) return

    setLoading(true)
    try {
      await signUp(email.trim(), password)
      if (isMock) {
        toast.success("Mock mode: account created locally.")
      } else {
        toast.success(`Registration successful. Check ${email} to confirm your account.`, { duration: 8000 })
      }
      router.push("/auth/login?registered=true")
    } catch (error: unknown) {
      toast.error(error instanceof Error ? error.message : "Failed to create account")
    } finally {
      setLoading(false)
    }
  }

  return (
    <ThreeScene intensity="light" type="particles">
      <SiteShell>
        <section className="container mx-auto grid min-h-[calc(100vh-8rem)] max-w-7xl gap-8 px-4 py-12 lg:grid-cols-[0.95fr_1.05fr] lg:items-center lg:py-16">
        <motion.div
          className="surface p-8 lg:p-10"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="mx-auto max-w-md space-y-6">
            <div className="inline-flex items-center gap-2 text-sm font-semibold">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-full gradient-premium text-primary-foreground">
                <ShieldCheck className="h-5 w-5" />
              </span>
              VeritasAd
            </div>

            <div className="space-y-2">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                Create account
              </p>
              <h1 className="text-3xl font-semibold tracking-tight lg:text-4xl">
                Start with a workflow that feels considered.
              </h1>
              <p className="text-sm leading-7 text-muted-foreground">
                Create your account to use the analysis dashboard, reports, and pricing tiers.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  className={`input-field ${errors.email ? "input-error" : ""}`}
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    validate(e.target.value, password, confirmPassword)
                  }}
                />
                {errors.email ? <p className="text-xs text-red-500">{errors.email}</p> : null}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  className={`input-field ${errors.password ? "input-error" : ""}`}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    validate(email, e.target.value, confirmPassword)
                  }}
                />
                {errors.password ? <p className="text-xs text-red-500">{errors.password}</p> : <p className="text-xs text-muted-foreground">At least 8 characters.</p>}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="confirmPassword">Confirm password</label>
                <input
                  id="confirmPassword"
                  type="password"
                  className={`input-field ${errors.confirmPassword ? "input-error" : ""}`}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value)
                    validate(email, password, e.target.value)
                  }}
                />
                {errors.confirmPassword ? <p className="text-xs text-red-500">{errors.confirmPassword}</p> : null}
              </div>

              <button type="submit" disabled={loading} className="btn btn-primary h-12 w-full">
                {loading ? (
                  <span className="inline-flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin" />Creating account...</span>
                ) : (
                  <>
                    Create account
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            <p className="text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link href="/auth/login" className="underline underline-offset-4 hover:text-foreground">
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>

        <motion.div
          className="relative overflow-hidden rounded-[2rem] border border-border/60 bg-background/70 p-8 shadow-[0_28px_90px_rgba(0,0,0,0.12)] backdrop-blur-2xl lg:p-10"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-cyan-400/5 to-transparent" />
          <div className="relative space-y-6">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
              What you get
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              {[
                ["Premium reports", "Sharper output for review"],
                ["Live workflow", "Clean progress states"],
                ["Usage tracking", "Clear quotas and limits"],
                ["Modern pricing", "Designed for teams"],
              ].map(([title, desc]) => (
                <div key={title} className="surface p-4">
                  <div className="text-sm font-semibold">{title}</div>
                  <p className="mt-1 text-xs text-muted-foreground">{desc}</p>
                </div>
              ))}
            </div>

            <blockquote className="surface border-l-2 border-primary/40 p-5">
              <p className="text-sm leading-7 text-muted-foreground">
                “Registration should be the lightest part of the experience, not the most confusing one.”
              </p>
              <footer className="mt-3 text-xs font-medium text-foreground">Auth design note</footer>
            </blockquote>
          </div>
        </motion.div>
      </section>
    </SiteShell>
    </ThreeScene>
  )
}
