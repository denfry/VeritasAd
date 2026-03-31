"use client"

import { useEffect, useState, type FormEvent } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { motion, useReducedMotion } from "framer-motion"
import { ArrowRight, Github, Globe, Loader2, ShieldCheck } from "lucide-react"
import { toast } from "sonner"
import { SiteShell } from "@/components/SiteShell"
import { useAuth } from "@/contexts/auth-context"
import { ThreeScene } from "@/components/three/ThreeScene"

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { signIn, isMock } = useAuth()
  const reduceMotion = useReducedMotion()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (searchParams.get("registered") === "true") {
      toast.success("Account created. You can sign in now.")
    }
  }, [searchParams])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!email.trim() || !password) {
      toast.error("Enter email and password")
      return
    }

    setLoading(true)
    try {
      await signIn(email.trim(), password)
      toast.success(isMock ? "Signed in with mock auth" : "Signed in successfully")
      router.push("/dashboard")
    } catch (error: unknown) {
      toast.error(error instanceof Error ? error.message : "Failed to sign in")
    } finally {
      setLoading(false)
    }
  }

  return (
    <ThreeScene intensity="light" type="particles">
      <SiteShell>
        <section className="container mx-auto grid min-h-[calc(100vh-8rem)] max-w-7xl gap-8 px-4 py-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:py-16">
        <motion.div
          className="relative overflow-hidden rounded-[2rem] border border-border/60 bg-background/70 p-8 shadow-[0_28px_90px_rgba(0,0,0,0.12)] backdrop-blur-2xl lg:p-10"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-cyan-400/5 to-transparent" />
          {!reduceMotion ? (
            <motion.div
              className="absolute right-[-80px] top-[-80px] h-64 w-64 rounded-full bg-primary/10 blur-3xl"
              animate={{ scale: [1, 1.12, 1], opacity: [0.35, 0.55, 0.35] }}
              transition={{ duration: 10, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
            />
          ) : null}
          <div className="relative space-y-8">
            <Link href="/" className="inline-flex items-center gap-2 text-sm font-semibold">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-full gradient-premium text-primary-foreground shadow-[0_14px_30px_-12px_hsl(var(--primary)/0.55)]">
                <ShieldCheck className="h-5 w-5" />
              </span>
              VeritasAd
            </Link>

            <div className="max-w-xl space-y-4">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                Premium access
              </p>
              <h1 className="text-balance text-4xl font-semibold tracking-tight lg:text-5xl">
                Sign in to a cleaner, faster analysis workspace.
              </h1>
              <p className="max-w-lg text-sm leading-7 text-muted-foreground lg:text-base">
                Access your dashboard, analysis history, reports, and workflow controls from one place.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              {[
                ["Fast setup", "Mock auth ready"],
                ["Better flow", "One workspace"],
                ["Clear status", "Always visible"],
              ].map(([title, desc]) => (
                <div key={title} className="surface p-4">
                  <div className="text-sm font-semibold">{title}</div>
                  <p className="mt-1 text-xs text-muted-foreground">{desc}</p>
                </div>
              ))}
            </div>

            <blockquote className="surface border-l-2 border-primary/40 p-5">
              <p className="text-sm leading-7 text-muted-foreground">
                “A high-trust interface should feel calm, fast, and structured. That is the direction
                this redesign is moving toward.”
              </p>
              <footer className="mt-3 text-xs font-medium text-foreground">Product design note</footer>
            </blockquote>
          </div>
        </motion.div>

        <motion.div
          className="surface p-8 lg:p-10"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.05 }}
        >
          <div className="mx-auto max-w-md space-y-6">
            <div className="space-y-2 text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground/70">
                Sign in
              </p>
              <h2 className="text-2xl font-semibold tracking-tight">Welcome back</h2>
              <p className="text-sm text-muted-foreground">Enter your email to continue.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none" htmlFor="email">
                  Email
                </label>
                <input
                  id="email"
                  placeholder="name@example.com"
                  type="email"
                  autoCapitalize="none"
                  autoComplete="email"
                  autoCorrect="off"
                  className="input-field"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium leading-none" htmlFor="password">
                    Password
                  </label>
                  <Link href="/auth/forgot-password" className="text-xs text-muted-foreground hover:text-foreground">
                    Forgot password?
                  </Link>
                </div>
                <input
                  id="password"
                  type="password"
                  className="input-field"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                />
              </div>
              <button className="btn btn-primary h-12 w-full" disabled={loading}>
                {loading ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  <>
                    Continue
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            <div className="relative py-2">
              <div className="absolute inset-x-0 top-1/2 h-px bg-border/70" />
              <span className="relative mx-auto block w-fit bg-card px-3 text-[10px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
                Or continue with
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button className="btn btn-outline h-11 w-full" type="button" disabled>
                <Github className="h-4 w-4" />
                GitHub
              </button>
              <button className="btn btn-outline h-11 w-full" type="button" disabled>
                <Globe className="h-4 w-4" />
                Google
              </button>
            </div>

            <p className="text-center text-sm text-muted-foreground">
              <Link href="/auth/register" className="underline underline-offset-4 hover:text-foreground">
                Don&apos;t have an account? Sign up
              </Link>
            </p>
          </div>
        </motion.div>
      </section>
    </SiteShell>
    </ThreeScene>
  )
}
